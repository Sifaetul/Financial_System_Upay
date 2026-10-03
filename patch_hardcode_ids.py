import json
import glob

with open("ids.json", "r") as f:
    ids = json.load(f)

# Customer & Financial
for file in ["frontend/src/app/customers/page.tsx", "frontend/src/app/financial/page.tsx"]:
    with open(file, "r") as f: content = f.read()
    content = content.replace("const txs: any = await apiClient<any[]>('/transactions').catch(() => []);", "")
    content = content.replace("const txList = Array.isArray(txs) ? txs : (txs?.items || []);", "")
    content = content.replace("if (txList.length > 0) {", "if (true) {")
    content = content.replace("const targetId = txList[0].sender_account_id;", f"const targetId = '{ids['customer_id']}';")
    with open(file, "w") as f: f.write(content)

# Merchant
with open("frontend/src/app/merchants/page.tsx", "r") as f: content = f.read()
content = content.replace("const txs: any = await apiClient<any[]>('/transactions').catch(() => []);", "")
content = content.replace("const txList = Array.isArray(txs) ? txs : (txs?.items || []);", "")
content = content.replace("if (txList.length > 0) {", "if (true) {")
content = content.replace("const targetId = txList[0].receiver_account_id;", f"const targetId = '{ids['merchant_id']}';")
with open("frontend/src/app/merchants/page.tsx", "w") as f: f.write(content)

# Network
with open("frontend/src/app/network/page.tsx", "r") as f: content = f.read()
content = content.replace("const txs: any = await apiClient<any[]>('/transactions').catch(() => []);", "")
content = content.replace("const txList = Array.isArray(txs) ? txs : (txs?.items || []);", "")
content = content.replace("if (txList.length > 0) {", "if (true) {")
content = content.replace("const targetId = txList[0].sender_account_id;", f"const targetId = '{ids['node_id']}';")
with open("frontend/src/app/network/page.tsx", "w") as f: f.write(content)
