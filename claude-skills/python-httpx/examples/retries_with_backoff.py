from scripts.httpx_skill import HttpxSkill

# Demonstrates simple retry-with-backoff around transient failures
skill = HttpxSkill(retries=3, http2=False)

# httpbin /status/503 will return 503; swap with a flaky endpoint in real usage
resp = skill.get("https://httpbin.org/status/503")
print(resp.status_code)
