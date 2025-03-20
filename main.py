import asyncio
from function.screen import Screen
from function.control import Control

async def main(screen: Screen):
    tasks = [
        asyncio.ensure_future(screen.run()),
        asyncio.ensure_future(acce.run())
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    screen = Screen(250, 122, debug=True, drawView=True)
    acce = Control(0x18)
    asyncio.run(main(screen, acce))