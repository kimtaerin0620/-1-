import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_DOWN
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLUE = (0, 0, 200) # 고정된 블록 배경색
RED = (200, 0, 0) # 떨어지는 블록 숫자 색
WHITE_TEXT = (240, 240, 240) # 고정된 블록 숫자 색

pygame.init()

# 게임 크기 설정
CELL_SIZE = 60 # 셀 크기
GRID_WIDTH = 5 + 2  # 폭 양쪽 한 칸
GRID_HEIGHT = 8 + 1 # 높이 바닥 한 칸

# 화면 전체 크기 설정
OFFSET_X = 50 # 왼쪽 여백
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + OFFSET_X * 2 + 200 # 화면 전체 너비 여백
SCREEN_HEIGHT = 800 # 원하는 세로 길이로 고정

# 게임판을 화면 중앙에 배치하기 위한 OFFSET_Y 값을 자동 계산
grid_pixel_height = GRID_HEIGHT * CELL_SIZE
OFFSET_Y = (SCREEN_HEIGHT - grid_pixel_height) // 2

# 전역 변수
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("10트리스")
fpsclock = pygame.time.Clock()
FPS = 15

# 게임 상태 변수들 딕셔너리
game_state = {
    'field': [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)],
    'current_number': None,
    'next_number': None,
    'block_x': 0,
    'block_y': 0,
    'score': 0,
    'game_over': False
}

def create_new_block():
    # 새 블록 생성
    game_state['current_number'] = game_state['next_number']
    game_state['next_number'] = random.randint(1, 9)
    game_state['block_x'] = GRID_WIDTH // 2 # 블록 게임 중앙에 배치
    game_state['block_y'] = -2 # 블록이 배경에서 떨어진다

def is_valid_position(x, y):
    # 위치가 빈 공간인지 확인
    # y가 영역 밖이면 충돌할 대상이 없으므로 항상 유효
    if y < 0:
        return True

    # 그리드 영역 안일 경우, 벽과 다른 블록을 확인
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        return game_state['field'][y][x] == 'B'

    return False

def apply_gravity():
    # 제거된 블록 위 공간을 채우기 위해 블록들을 아래로 내립니다.
    field = game_state['field']
    for x in range(1, GRID_WIDTH - 1):
        new_col = [field[y][x] for y in range(GRID_HEIGHT - 2, -1, -1) if field[y][x].isdigit()]
        for y in range(1, GRID_HEIGHT -1):
            field[y][x] = 'B'
        for i, num in enumerate(new_col):
            field[GRID_HEIGHT - 2 - i][x] = num

def check_and_clear_matches():
    # 가로 또는 세로로 합이 10이 되는 그룹을 찾아 제거하고 중력을 적용합니다.
    field = game_state['field']

    while True:
        master_coords_to_remove = set()

        # 가로 방향 검사
        for y in range(GRID_HEIGHT - 1):
            for x_start in range(1, GRID_WIDTH - 1):
                current_sum = 0
                current_path = []
                for x in range(x_start, GRID_WIDTH - 1):
                    if field[y][x].isdigit():
                        current_sum += int(field[y][x])
                        current_path.append((x, y))
                        if current_sum == 10 and len(current_path) >= 2:
                            master_coords_to_remove.update(current_path)
                            break
                        if current_sum > 10: break
                    else: break

        # 세로 방향 검사
        for x in range(1, GRID_WIDTH - 1):
            for y_start in range(GRID_HEIGHT - 1):
                current_sum = 0
                current_path = []
                for y in range(y_start, GRID_HEIGHT - 1):
                    if field[y][x].isdigit():
                        current_sum += int(field[y][x])
                        current_path.append((x, y))
                        if current_sum == 10 and len(current_path) >= 2:
                            master_coords_to_remove.update(current_path)
                            break
                        if current_sum > 10: break
                    else: break

        if master_coords_to_remove:
            for x, y in master_coords_to_remove:
                field[y][x] = 'B'
            removed_count = len(master_coords_to_remove)
            game_state['score'] += 10 * (2 ** (removed_count - 2))
            draw_game()
            pygame.time.wait(200)
            apply_gravity()
            draw_game()
            pygame.time.wait(200)
        else:
            break

def draw_game():
    # 게임 화면 전체
    screen.fill(BLACK)
    field = game_state['field']
    font = pygame.font.SysFont(None, int(CELL_SIZE * 0.8))

    # 게임 필드 그리기
    for y, row in enumerate(field):
        for x, value in enumerate(row):
            rect = pygame.Rect(OFFSET_X + x * CELL_SIZE, OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if value == 'W':
                pygame.draw.rect(screen, GREY, rect)
            elif value == 'B':
                border_rect = pygame.Rect(OFFSET_X + x * CELL_SIZE, OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GREY, border_rect, 1)
            elif value.isdigit():
                pygame.draw.rect(screen, BLUE, rect)
                num_img = font.render(value, True, WHITE_TEXT)
                num_rect = num_img.get_rect(center=rect.center)
                screen.blit(num_img, num_rect)

    # 떨어지는 블록 그리기
    if not game_state['game_over'] and game_state['current_number'] is not None:
        rect = pygame.Rect(OFFSET_X + game_state['block_x'] * CELL_SIZE, OFFSET_Y + game_state['block_y'] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect)
        num_img = font.render(str(game_state['current_number']), True, RED)
        num_rect = num_img.get_rect(center=rect.center)
        screen.blit(num_img, num_rect)

    # UI 그리기
    ui_font = pygame.font.SysFont(None, 40)
    ui_area_x = OFFSET_X + GRID_WIDTH * CELL_SIZE + 20
    score_text = ui_font.render(f"SCORE: {game_state['score']}", True, WHITE)
    score_rect = score_text.get_rect(topleft=(ui_area_x, OFFSET_Y))
    screen.blit(score_text, score_rect)
    next_label_text = ui_font.render("NEXT", True, WHITE)
    next_label_rect = next_label_text.get_rect(topleft=(ui_area_x, score_rect.bottom + 50))
    screen.blit(next_label_text, next_label_rect)
    if game_state['next_number'] is not None:
        next_block_bg = pygame.Rect(0, 0, CELL_SIZE * 2, CELL_SIZE * 2)
        next_block_bg.topleft = (ui_area_x, next_label_rect.bottom + 10)
        pygame.draw.rect(screen, GREY, next_block_bg)
        big_font = pygame.font.SysFont(None, int(CELL_SIZE * 1.5))
        next_num_img = big_font.render(str(game_state['next_number']), True, RED)
        next_num_rect = next_num_img.get_rect(center=next_block_bg.center)
        screen.blit(next_num_img, next_num_rect)

    # 게임 오버 메시지
    if game_state['game_over']:
        bigfont = pygame.font.SysFont(None, 80)
        over_text = bigfont.render("GAME OVER", True, RED)
        # 게임오버 메시지 위치
        text_rect = over_text.get_rect(center=(OFFSET_X + (GRID_WIDTH * CELL_SIZE / 2), SCREEN_HEIGHT / 2))
        screen.blit(over_text, text_rect)

    pygame.display.update()

def main():
    field = game_state['field']
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1: field[y][x] = 'W'
            else: field[y][x] = 'B'

    game_state['next_number'] = random.randint(1, 9)
    create_new_block()
    last_drop_time = pygame.time.get_ticks()
    drop_interval = 500

    while True:
        if game_state['game_over']:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            draw_game()
            continue

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: pygame.quit(); sys.exit()
                if game_state['current_number'] is not None:
                    if event.key == K_LEFT and is_valid_position(game_state['block_x'] - 1, game_state['block_y']):
                        game_state['block_x'] -= 1
                    elif event.key == K_RIGHT and is_valid_position(game_state['block_x'] + 1, game_state['block_y']):
                        game_state['block_x'] += 1
                    elif event.key == K_DOWN:
                        if is_valid_position(game_state['block_x'], game_state['block_y'] + 1):
                            game_state['block_y'] += 1

        if game_state['current_number'] is not None:
            now = pygame.time.get_ticks()
            if now - last_drop_time > drop_interval:
                last_drop_time = now
                if is_valid_position(game_state['block_x'], game_state['block_y'] + 1):
                    game_state['block_y'] += 1
                else: # 블록이 어딘가에 닿았을 때
                    # 닿은 위치가 게임판 상단(y<0)이면 즉시 게임오버
                    if game_state['block_y'] < 0:
                        game_state['game_over'] = True
                    else:
                        # 정상적으로 게임판 안에 안착
                        field[game_state['block_y']][game_state['block_x']] = str(game_state['current_number'])

                    game_state['current_number'] = None

                    if not game_state['game_over']:
                        check_and_clear_matches()

        if game_state['current_number'] is None and not game_state['game_over']:
            create_new_block()

        draw_game()
        fpsclock.tick(FPS)

if __name__ == '__main__':
    main()