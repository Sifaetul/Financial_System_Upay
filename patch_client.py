with open("frontend/src/lib/api/client.ts", "r") as f:
    content = f.read()

auto_login_code = """
  if (response.status === 401) {
    // Auto-login for demo purposes
    try {
      const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'username=rbac@example.com&password=StrongPassword123!'
      });
      if (loginRes.ok) {
        const data = await loginRes.json();
        localStorage.setItem('auth_token', data.access_token);
        // Retry original request
        options.headers = { ...options.headers, 'Authorization': `Bearer ${data.access_token}` };
        const retryRes = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (retryRes.status === 204) return {} as T;
        return retryRes.json();
      }
    } catch (e) {
      console.error("Auto-login failed", e);
    }
  }
"""

content = content.replace("if (!response.ok) {", auto_login_code + "\n  if (!response.ok) {")

with open("frontend/src/lib/api/client.ts", "w") as f:
    f.write(content)
