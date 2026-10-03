with open("tests/test_verification.py", "r") as f:
    content = f.read()

content = content.replace(
    'tx = service.advance_status(tx.id, "COMPLETED") # VALIDATED -> PROCESSING -> COMPLETED',
    'with pytest.raises(HTTPException) as excinfo:\n        service.advance_status(tx.id, "COMPLETED")\n    assert excinfo.value.status_code == 400'
)

with open("tests/test_verification.py", "w") as f:
    f.write(content)
