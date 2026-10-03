with open("app/models/__init__.py", "a") as f:
    f.write("\nfrom .risk import RiskEvaluation, RiskEvaluationSignal\n")
