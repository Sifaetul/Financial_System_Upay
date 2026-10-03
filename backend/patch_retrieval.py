import os

for filename in ["app/services/copilot_retrieval.py", "tests/test_copilot.py"]:
    with open(filename, "r") as f:
        content = f.read()
    
    content = content.replace("from app.models.copilot import AIDocument, AIChunk", "from app.models.ai import AiDocument, AiChunk")
    content = content.replace("AIDocument", "AiDocument")
    content = content.replace("AIChunk", "AiChunk")
    
    with open(filename, "w") as f:
        f.write(content)
