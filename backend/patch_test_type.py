with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace('primary_entity_id="test_entity",', 'primary_entity_type="CUSTOMER", primary_entity_id="test_entity",')

with open("tests/test_copilot.py", "w") as f:
    f.write(content)
