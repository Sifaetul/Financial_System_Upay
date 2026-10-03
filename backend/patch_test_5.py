with open("tests/test_investigation.py", "r") as f:
    content = f.read()

content = content.replace("assert alert2 is None", "assert alert2.id == alert1.id")
content = content.replace("case = InvestigationService.create_case_from_alert(db, alert.id)", "case = InvestigationService.create_case_from_alert(db, alert)")

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
