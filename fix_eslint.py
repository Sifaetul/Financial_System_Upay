import os
with open("frontend/src/app/investigations/page.tsx", "r") as f: content = f.read()

content = content.replace('"Account Takeover"', '&quot;Account Takeover&quot;')
content = content.replace('"Money Mule"', '&quot;Money Mule&quot;')
content = content.replace('"Based on the correlated signals, this case has a high probability of being an organized fraud attempt. I recommend maintaining the temporary hold and escalating to the compliance tier for identity verification."', '&quot;Based on the correlated signals, this case has a high probability of being an organized fraud attempt. I recommend maintaining the temporary hold and escalating to the compliance tier for identity verification.&quot;')

with open("frontend/src/app/investigations/page.tsx", "w") as f: f.write(content)
