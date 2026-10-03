with open("frontend/src/app/risk/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "const casesRes = await",
    "const casesRes: any = await"
)
content = content.replace(
    "c => c.status !==",
    "(c: any) => c.status !=="
)
content = content.replace(
    "c => c.severity ===",
    "(c: any) => c.severity ==="
)

with open("frontend/src/app/risk/page.tsx", "w") as f:
    f.write(content)
