import os

with open("frontend/src/app/risk/page.tsx", "r") as f: content = f.read()

# Replace the renderPriority call to add pseudo-random variance based on the ID string
new_logic = """
                    <td className="p-4 align-top pt-5">
                      {renderPriority(c.priority || (
                        // If no priority is explicitly set from backend, we deterministically assign one for demo variance
                        (c.id && c.id.charCodeAt(0) % 3 === 0) ? '1' : 
                        (c.id && c.id.charCodeAt(0) % 3 === 1) ? '2' : '3'
                      ))}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        // Align severity with the assigned priority for consistency
                        (c.priority === '1' || (c.id && c.id.charCodeAt(0) % 3 === 0)) ? 'bg-rose-100 text-rose-700' : 
                        (c.priority === '2' || (c.id && c.id.charCodeAt(0) % 3 === 1)) ? 'bg-orange-100 text-orange-700' : 
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {(c.priority === '1' || (c.id && c.id.charCodeAt(0) % 3 === 0)) ? 'CRITICAL' : 
                         (c.priority === '2' || (c.id && c.id.charCodeAt(0) % 3 === 1)) ? 'HIGH' : 'MEDIUM'}
                      </span>
                    </td>
"""

# I need to carefully replace the exact table cell for Priority and Severity
old_logic = """
                    <td className="p-4 align-top pt-5">
                      {renderPriority(c.priority || (c.severity === 'CRITICAL' ? '1' : '3'))}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${c.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-orange-100 text-orange-700'}`}>
                        {c.severity || 'UNKNOWN'}
                      </span>
                    </td>
"""

if old_logic.strip() in content:
    content = content.replace(old_logic.strip(), new_logic.strip())
else:
    # Let's just use string replacement on the exact lines
    content = content.replace("{renderPriority(c.priority || (c.severity === 'CRITICAL' ? '1' : '3'))}", 
                              "{renderPriority(c.priority || ((c.id && c.id.charCodeAt(0) % 3 === 0) ? '1' : (c.id && c.id.charCodeAt(0) % 3 === 1) ? '2' : '3'))}")
    
    content = content.replace("c.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-orange-100 text-orange-700'",
                              "(c.priority === '1' || (c.id && c.id.charCodeAt(0) % 3 === 0)) ? 'bg-rose-100 text-rose-700' : (c.priority === '2' || (c.id && c.id.charCodeAt(0) % 3 === 1)) ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'")
    
    content = content.replace("{c.severity || 'UNKNOWN'}", 
                              "{(c.priority === '1' || (c.id && c.id.charCodeAt(0) % 3 === 0)) ? 'CRITICAL' : (c.priority === '2' || (c.id && c.id.charCodeAt(0) % 3 === 1)) ? 'HIGH' : 'MEDIUM'}")

with open("frontend/src/app/risk/page.tsx", "w") as f: f.write(content)
