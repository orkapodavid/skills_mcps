from scripts.httpx_skill import HttpxSkill

skill = HttpxSkill()
skill.stream_download("https://httpbin.org/bytes/1048576", "./one_mb.bin")
print("Downloaded 1 MB to one_mb.bin")
