import sys
filename = sys.argv[1]
with open(filename, "r") as f:
    content = f.read()

if "import pgvector" not in content:
    content = content.replace("import sqlalchemy as sa", "import sqlalchemy as sa\nimport pgvector")

with open(filename, "w") as f:
    f.write(content)
