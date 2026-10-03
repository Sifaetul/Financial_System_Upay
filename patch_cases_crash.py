import os

# Fix Investigations Page
with open("frontend/src/app/investigations/page.tsx", "r") as f: content = f.read()
# Replace c.primary_entity_id.split('-')[0] with something safe
content = content.replace("c.primary_entity_id.split('-')[0]", "(c.primary_entity_id ? c.primary_entity_id.split('-')[0] : 'Unknown Entity')")
# Replace c.created_at with something safe
content = content.replace("new Date(c.created_at).toLocaleDateString()", "new Date(c.created_at || Date.now()).toLocaleDateString()")
# Replace Case #... with c.number
content = content.replace("Case #{c.id.split('-')[0].toUpperCase()}", "{c.number || 'CASE-' + c.id.split('-')[0].toUpperCase()}")

with open("frontend/src/app/investigations/page.tsx", "w") as f: f.write(content)


# Fix Copilot Page
with open("frontend/src/app/copilot/page.tsx", "r") as f: content = f.read()
content = content.replace("involving entity ${c.primary_entity_id}", "with severity ${c.severity || 'HIGH'}")
with open("frontend/src/app/copilot/page.tsx", "w") as f: f.write(content)
