with open("app/services/transaction_service.py", "r") as f:
    content = f.read()

content = content.replace("raise HTTPException(status_code=409, detail=\"Idempotency conflict or Invalid Reference\")", "print(f'INTEGRITY ERROR: {e}'); raise HTTPException(status_code=409, detail=f\"Idempotency conflict or Invalid Reference: {e}\")")

with open("app/services/transaction_service.py", "w") as f:
    f.write(content)
