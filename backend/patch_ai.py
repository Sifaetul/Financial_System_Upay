with open("app/models/ai.py", "r") as f:
    content = f.read()

content = content.replace("Vector(1536)", "Vector(384)")

with open("app/models/ai.py", "w") as f:
    f.write(content)
