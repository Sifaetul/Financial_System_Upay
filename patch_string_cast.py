import os
with open("frontend/src/app/investigations/page.tsx", "r") as f: content = f.read()
content = content.replace("c.primary_entity_id.split('-')[0]", "String(c.primary_entity_id).split('-')[0]")
with open("frontend/src/app/investigations/page.tsx", "w") as f: f.write(content)
