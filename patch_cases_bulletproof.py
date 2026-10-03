import os

# Fix Investigations Page
with open("frontend/src/app/investigations/page.tsx", "r") as f: content = f.read()
# Replace c.id.split
content = content.replace("c.id.split('-')[0].toUpperCase()", "(c.id ? c.id.split('-')[0].toUpperCase() : 'UNKNOWN')")
with open("frontend/src/app/investigations/page.tsx", "w") as f: f.write(content)

# Fix Risk Page
with open("frontend/src/app/risk/page.tsx", "r") as f: content = f.read()
content = content.replace("c.id.substring(0,8)", "(c.id ? c.id.substring(0,8) : 'UNKNOWN')")
with open("frontend/src/app/risk/page.tsx", "w") as f: f.write(content)
