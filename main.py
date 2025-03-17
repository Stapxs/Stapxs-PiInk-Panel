import asyncio
from function.screen import Screen

async def main(screen: Screen):
    tasks = [
        asyncio.ensure_future(screen.run())
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    screen = Screen(250, 122, debug=True, drawView=True)
    asyncio.run(main(screen))