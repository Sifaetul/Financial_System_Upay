import glob
for file in glob.glob("frontend/src/app/*/page.tsx"):
    with open(file, "r") as f: content = f.read()
    if "const txs = await apiClient" in content:
        content = content.replace("const txs = await apiClient", "const txs: any = await apiClient")
        with open(file, "w") as f: f.write(content)
