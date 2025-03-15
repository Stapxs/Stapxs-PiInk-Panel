import asyncio
from function.screen import screen as Screen

async def main():

    screen = Screen(250, 122)
    tasks = [
        asyncio.ensure_future(screen.run())
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())