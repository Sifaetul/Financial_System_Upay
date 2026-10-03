import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.identity import User, Role
from app.models.customer import Customer, Account
from app.models.transaction import Transaction, Merchant
from app.core.config import settings

# Setup an isolated test engine
# For isolation, we use the same DB but a test rollback transaction, or create a separate test DB.
# For simplicity, we just use the existing DB but wrap tests in nested transactions.

engine = create_engine(settings.DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Setup nested transaction for tests
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_database_connection_and_tables(db):
    # Test connection and table creation
    result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result.fetchall()]
    assert "users" in tables
    assert "roles" in tables
    assert "transactions" in tables
    assert "accounts" in tables

def test_user_role_relationship(db):
    # Create Role
    role = Role(name="admin")
    db.add(role)
    db.commit()

    # Create User
    user = User(email="test@example.com", password_hash="hash")
    user.roles.append(role)
    db.add(user)
    db.commit()

    # Query User
    saved_user = db.query(User).filter_by(email="test@example.com").first()
    assert saved_user is not None
    assert len(saved_user.roles) == 1
    assert saved_user.roles[0].name == "admin"

def test_unique_constraint(db):
    from sqlalchemy.exc import IntegrityError
    
    # Insert first user
    user1 = User(email="unique@example.com", password_hash="hash")
    db.add(user1)
    db.commit()
    
    # Insert duplicate email
    user2 = User(email="unique@example.com", password_hash="hash")
    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()

def test_foreign_key_constraint(db):
    from sqlalchemy.exc import IntegrityError
    
    # Attempt to insert an account for a non-existent customer
    account = Account(customer_id="non-existent-id", account_number_hash="123", balance=100.0, currency="USD")
    db.add(account)
    with pytest.raises(IntegrityError):
        db.commit()

def test_customer_account_transaction_flow(db):
    # Insert Customer
    customer = Customer(identifier="CUST-123")
    db.add(customer)
    db.commit()

    # Insert Accounts
    account1 = Account(customer_id=customer.id, account_number_hash="ACC-1", balance=100.0)
    account2 = Account(customer_id=customer.id, account_number_hash="ACC-2", balance=0.0)
    db.add_all([account1, account2])
    db.commit()

    # Insert Transaction
    txn = Transaction(amount=50.0, currency="USD", status="completed", transaction_type="transfer",
                      sender_account_id=account1.id, receiver_account_id=account2.id)
    db.add(txn)
    db.commit()

    # Query
    saved_customer = db.query(Customer).filter_by(identifier="CUST-123").first()
    assert len(saved_customer.accounts) == 2
    
    saved_txn = db.query(Transaction).filter_by(id=txn.id).first()
    assert saved_txn.amount == 50.0
