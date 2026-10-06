import math
import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rect: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんまたは爆弾のRect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue／画面外ならFalse
    """
    yoko, tate = True, True
    if rect.left < 0 or WIDTH < rect.right:  
        yoko = False
    if rect.top < 0 or HEIGHT < rect.bottom:  
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に画面をブラックアウトし、こうかとんとメッセージを表示する
    """
    bg_overlay = pg.Surface((WIDTH, HEIGHT))
    bg_overlay.set_alpha(180)
    bg_overlay.fill((0, 0, 0))

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    bg_overlay.blit(txt, txt_rct)

    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct1 = kk_img.get_rect()
    kk_rct1.center = WIDTH // 2 - 200, HEIGHT // 2
    bg_overlay.blit(kk_img, kk_rct1)

    kk_rct2 = kk_img.get_rect()
    kk_rct2.center = WIDTH // 2 + 200, HEIGHT // 2
    bg_overlay.blit(kk_img, kk_rct2)

    screen.blit(bg_overlay, [0, 0])
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    拡大する爆弾のSurfaceリストと加速度のリストを生成する
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)

    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応するこうかとん画像Surfaceの辞書を返す
    """
    base_img = pg.image.load("fig/3.png")
    right_img = pg.transform.flip(base_img, True, False)

    kk_dict = {
        (0, 0): pg.transform.rotozoom(right_img, 0, 0.9),
        (+5, 0): pg.transform.rotozoom(right_img, 0, 0.9),
        (+5, -5): pg.transform.rotozoom(right_img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(right_img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(base_img, -45, 0.9),
        (-5, 0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, +5): pg.transform.rotozoom(base_img, 45, 0.9),
        (0, +5): pg.transform.rotozoom(right_img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(right_img, -45, 0.9),
    }
    return kk_dict


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    org（爆弾）から dst（こうかとん）に向かうベクトルを計算して返す
    距離が300未満の場合は慣性（current_xy）を返す
    """
    
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    
    
    norm = math.hypot(dx, dy)
    
   
    if norm < 300:
        return current_xy
    
    
    target_norm = math.sqrt(50)
    vx = dx / norm * target_norm
    vy = dy / norm * target_norm
    
    return vx, vy


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5
    
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        #
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, tpl in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        
        center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = center

        
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)

        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()