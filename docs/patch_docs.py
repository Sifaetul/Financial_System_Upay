import re

# Update project-state.md
with open("project-state.md", "r") as f:
    content = f.read()

content = content.replace("Current Phase: 12", "Current Phase: 12 (VERIFIED)")
content = content.replace("Phase 12 Status: IN PROGRESS", "Phase 12 Status: COMPLETED")
content = content.replace("- Next Phase: Phase 12", "- Next Phase: Phase 13 - Monitoring & Governance")

with open("project-state.md", "w") as f:
    f.write(content)

# Update feature-matrix.md
with open("feature-matrix.md", "r") as f:
    content = f.read()

content = content.replace("| Phase 12 | AI Investigation Copilot | ❌ Not Started |", "| Phase 12 | AI Investigation Copilot | ✅ Completed |")
content = content.replace("| Phase 12 | AI Investigation Copilot | 🚧 In Progress |", "| Phase 12 | AI Investigation Copilot | ✅ Completed |")

with open("feature-matrix.md", "w") as f:
    f.write(content)
