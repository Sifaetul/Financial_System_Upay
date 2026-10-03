import subprocess
result = subprocess.run(["venv/bin/pytest", "tests/test_investigation.py", "-v"], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
