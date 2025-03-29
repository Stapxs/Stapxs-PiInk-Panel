import threading
from function.screen import Screen
from function.control import Control
from pathlib import Path

def run_acce(acce):
    acce.run()

if __name__ == "__main__":
    current_path = str(Path(__file__).resolve().parent)
    # 运行模式：virtual、hardware、all
    run_mode = 'all'
    debug = True

    screen = Screen(250, 122, debug=debug, run_mode=run_mode, current_path=current_path)
    acce = Control(0x18, screen=screen, has_hardware=run_mode in ['hardware', 'all'])

    if(run_mode in ['hardware', 'all']):
        # 运行运动传感器控制
        acce_thread = threading.Thread(target=run_acce, args=(acce,), daemon=True)
        acce_thread.start()

    # 运行屏幕渲染
    screen.run()