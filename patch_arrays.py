import glob

for filename in ['frontend/src/app/customers/page.tsx', 'frontend/src/app/fraud/page.tsx', 'frontend/src/app/transactions/page.tsx']:
    with open(filename, 'r') as f:
        content = f.read()
    
    content = content.replace("res.items || []", "Array.isArray(res) ? res : (res.items || [])")
    
    with open(filename, 'w') as f:
        f.write(content)
