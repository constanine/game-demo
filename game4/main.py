# game4/main.py
import pygame
import sys
import os

# 移除或注释掉相对导入
# from .systems.game_manager import GameManager
# from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE

# 改为绝对导入 (假设你的项目根目录在 Python 路径中，或者你从项目根目录运行)
# 但更健壮的方式是动态添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)  # 将项目根目录添加到 sys.path

# 现在可以使用绝对导入了
from game4.systems.game_manager import GameManager
from game4.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE


# ... rest of the code ...
def main():
    # ... (rest of the main function remains the same) ...
    # 注意：内部 GameManager 内部的相对导入可能也需要调整，或者确保包结构被正确识别
    # 如果 GameManager 内部也有相对导入问题，也需要类似地修改或确保运行方式正确
    try:
        # 初始化Pygame
        pygame.init()

        # 创建窗口
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("冒头冒险游戏")

        # 加载字体 (使用 constants.py 中的 FONT_PATH)
        # 注意：constants.py 中的 FONT_PATH 是基于 __file__ 的，应该已经考虑了目录结构
        # 但如果 main.py 被直接运行，__file__ 会不同，可能需要调整字体路径获取方式
        # 为了安全起见，在 main.py 中也重新计算一次字体路径

        # 获取 game4 包的目录
        game4_dir = os.path.dirname(os.path.abspath(__file__))  # This is .../qwen-game-demo/game4
        font_path = os.path.join(game4_dir, "assets", "fonts", "simhei.ttf")

        # 加载字体
        if not os.path.exists(font_path):
            print(f"错误: 找不到字体文件 {font_path}")
            print("请确保在 game4 目录下有 assets/fonts/simhei.ttf 文件")
            sys.exit(1)

        try:
            font = pygame.font.Font(font_path, FONT_SIZE)
        except pygame.error as e:
            print(f"错误: 无法加载字体文件: {e}")
            sys.exit(1)

        # 创建游戏管理器
        game = GameManager(screen, font)

        # 主游戏循环
        running = True
        clock = pygame.time.Clock()

        while running:
            dt = clock.tick(60)  # 60 FPS
            running = game.run(dt)

        pygame.quit()
        sys.exit()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    # 当直接运行此脚本时，这种方法配合 sys.path 修改可能有效
    # 但最标准和推荐的方式仍然是使用 `python -m game4.main` 从项目根目录运行
    main()