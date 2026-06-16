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


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or ばくだんRect
    戻り値：判定結果タプル（横方向判定結果，縦方向判定結果）
    画面内:True 画面外:False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に、半透明の黒い画面と「Game Over」の文字、
    泣いているこうかとんを表示する関数
    引数 screen：画面Surface
    戻り値：なし
    """
    bg_black = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(bg_black, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    bg_black.set_alpha(128)  # 修正: 標準的な半透明（約50%）に戻す

    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    bg_black.blit(txt, txt_rct)

    kk_img = pg.image.load("fig/8.png")
    kk_rct1 = kk_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))
    kk_rct2 = kk_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))
    bg_black.blit(kk_img, kk_rct1)
    bg_black.blit(kk_img, kk_rct2)

    screen.blit(bg_black, [0, 0])
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    時間経過で拡大する爆弾Surfaceのリストと、加速する加速度のリストを返す関数
    戻り値：爆弾Surfaceのリストと加速度リストのタプル
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー、その方向を向いたこうかとん画像を値とする辞書を返す関数
    戻り値：移動量タプルと画像の辞書
    """
    kk_img = pg.image.load("fig/3.png")
    kk_img_f = pg.transform.flip(kk_img, True, False)
    return {
        (0, 0): pg.transform.rotozoom(kk_img, 0, 0.9),
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 0.9),
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 0.9),
        (0, -5): pg.transform.rotozoom(kk_img_f, 90, 0.9),
        (+5, -5): pg.transform.rotozoom(kk_img_f, 45, 0.9),
        (+5, 0): pg.transform.rotozoom(kk_img_f, 0, 0.9),
        (+5, +5): pg.transform.rotozoom(kk_img_f, -45, 0.9),
        (0, +5): pg.transform.rotozoom(kk_img_f, -90, 0.9),
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 0.9),
    }


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾からこうかとんへの移動方向ベクトルを計算する関数
    引数 org: 爆弾Rect
    引数 dst: こうかとんRect
    引数 current_xy: 現在の移動速度ベクトル
    戻り値: 正規化された移動速度ベクトル、または元のベクトル
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx**2 + dy**2)
    if norm < 300:
        return current_xy
    vx = dx / norm * math.sqrt(50)
    vy = dy / norm * math.sqrt(50)
    return vx, vy


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    #爆弾の初期化
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

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        avx = vx * bb_accs[min(tmr//500, 9)]
        avy = vy * bb_accs[min(tmr//500, 9)]

        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

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