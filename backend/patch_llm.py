with open("app/services/llm_provider.py", "r") as f:
    content = f.read()

content = content.replace(
    'if "Insufficient evidence" in context or context.strip() == "":',
    'if "Insufficient evidence" in prompt or "Insufficient evidence" in context or context.strip() == "":'
)
with open("app/services/llm_provider.py", "w") as f:
    f.write(content)
