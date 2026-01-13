from scripts.httpx_skill import HttpxSkill

skill = HttpxSkill(http2=True, retries=2)
r = skill.get("https://httpbin.org/get", params={"hello": "world"})
r.raise_for_status()
print(r.json())
