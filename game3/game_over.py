import pygame


def show_game_over_screen(screen, floor):
    """显示游戏结束界面"""
    try:
        font = pygame.font.SysFont('simhei,arial,helvetica', 48)
        small_font = pygame.font.SysFont('simhei,arial,helvetica', 36)
    except:
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 36)

    screen.fill((0, 0, 0))  # 黑色背景

    # 显示游戏结束文字
    game_over_text = font.render("游戏结束", True, (255, 0, 0))
    screen.blit(game_over_text, (300, 200))

    # 显示达到的层数
    floor_text = small_font.render(f"你达到了第 {floor} 层", True, (255, 255, 255))
    screen.blit(floor_text, (300, 300))

    # 显示Top5信息
    top5_text = small_font.render("历史最高记录:", True, (255, 255, 0))
    screen.blit(top5_text, (300, 400))

    # 这里可以读取保存的记录
    records = [10, 8, 6, 4, 2]  # 示例数据
    for i, record in enumerate(records):
        record_text = small_font.render(f"{i + 1}. 第 {record} 层", True, (255, 255, 255))
        screen.blit(record_text, (320, 450 + i * 40))

    # 显示重新开始提示
    restart_text = small_font.render("按任意键重新开始", True, (0, 255, 0))
    screen.blit(restart_text, (250, 700))

    pygame.display.flip()

    # 等待用户按键
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False