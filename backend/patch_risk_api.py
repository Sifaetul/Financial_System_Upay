with open("app/api/v1/endpoints/risk.py", "r") as f:
    content = f.read()

history_endpoint = """
@router.get("/transaction/{transaction_id}", response_model=List[RiskEvaluationResult])
def get_transaction_evaluations(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["manage_transactions"]))
):
    evs = db.query(RiskEvaluation).filter(RiskEvaluation.transaction_id == transaction_id).order_by(RiskEvaluation.created_at.desc()).all()
    return evs
"""
if "get_transaction_evaluations" not in content:
    content += history_endpoint

with open("app/api/v1/endpoints/risk.py", "w") as f:
    f.write(content)
