with open("tests/test_investigation.py", "r") as f:
    content = f.read()

content = content.replace("InvestigationService.add_case_note(db, case.id, user_id, \"Checking suspicious activity\")", "InvestigationService.add_note(db, case.id, user_id, \"Checking suspicious activity\")")
content = content.replace("updated_case = InvestigationService.update_case_status(db, case.id, \"CLOSED_TRUE_POSITIVE\", user_id)", "updated_case = InvestigationService.resolve_case(db, case.id, user_id, \"TRUE_POSITIVE\", \"Confirmed fraud\")")
content = content.replace("assert updated_case.status == \"CLOSED_TRUE_POSITIVE\"", "assert updated_case.status == \"RESOLVED\"\n    assert updated_case.resolution_type == \"TRUE_POSITIVE\"")

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
