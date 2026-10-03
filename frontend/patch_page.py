with open("src/app/cases/[id]/page.tsx", "r") as f:
    content = f.read()

if "CopilotPanel" not in content:
    content = content.replace(
        "import { useParams } from 'next/navigation'",
        "import { useParams } from 'next/navigation'\nimport CopilotPanel from '@/components/CopilotPanel'"
    )
    
    content = content.replace(
        "</div>\n  )\n}",
        "  <CopilotPanel caseId={caseId} />\n    </div>\n  )\n}"
    )

with open("src/app/cases/[id]/page.tsx", "w") as f:
    f.write(content)
