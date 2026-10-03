with open("app/api/v1/router.py", "r") as f:
    content = f.read()
if "from .endpoints import" in content and "copilot" not in content:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("from .endpoints import"):
            lines[i] = line + ", copilot"
    content = '\n'.join(lines)
with open("app/api/v1/router.py", "w") as f:
    f.write(content)
