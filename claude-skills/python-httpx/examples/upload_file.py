from scripts.httpx_skill import HttpxSkill

skill = HttpxSkill()
resp = skill.upload_file(
    "https://httpbin.org/post",
    "requirements.txt",
    field_name="file",
    content_type="text/plain",
)
resp.raise_for_status()
print(resp.json()["files"])  # echo from httpbin
