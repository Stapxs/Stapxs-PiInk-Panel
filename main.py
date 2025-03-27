import threading
from function.screen import Screen
from function.control import Control
from pathlib import Path

def run_screen(screen):
    screen.run()

def run_acce(acce):
    acce.run()

if __name__ == "__main__":
    current_path = str(Path(__file__).resolve().parent)
    debug = True
    virtual = True

    screen = Screen(250, 122, debug=debug, virtual=virtual, current_path=current_path)
    acce = Control(0x18, virtual=virtual, screen=screen)

    # 在单独的线程运行
    acce_thread = threading.Thread(target=run_acce, args=(acce,), daemon=True)
    acce_thread.start()

    # 在主线程运行
    run_screen(screen)