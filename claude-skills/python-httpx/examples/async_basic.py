import asyncio
from scripts.httpx_skill import HttpxSkill


async def main():
    skill = HttpxSkill(async_mode=True, http2=True, retries=2)
    r = await skill.aget("https://httpbin.org/get")
    r.raise_for_status()
    print(r.status_code)
    await skill.aclose()


if __name__ == "__main__":
    asyncio.run(main())
