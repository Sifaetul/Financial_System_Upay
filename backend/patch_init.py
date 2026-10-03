with open("app/models/__init__.py", "r") as f:
    content = f.read()

content = content.replace("from app.models.copilot import AIDocument, AIChunk, CopilotConversation, CopilotMessage, CopilotCitation\n", "")
if "CopilotConversation" not in content:
    content += "from app.models.copilot import CopilotConversation, CopilotMessage, CopilotCitation\n"

with open("app/models/__init__.py", "w") as f:
    f.write(content)
