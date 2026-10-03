with open("frontend/src/app/fraud/page.tsx", "r") as f:
    content = f.read()

content = content.replace("a =>", "(a: any) =>")

with open("frontend/src/app/fraud/page.tsx", "w") as f:
    f.write(content)
