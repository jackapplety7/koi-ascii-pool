#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
koi.py —— 终端里游动的 ASCII 锦鲤
============================================================================
用法：
    python koi.py                # 一直在游
    python koi.py 30             # 游 30 秒后退出
    python koi.py --calm         # 不要气泡，安静点
    python koi.py --no-color     # 不上色，纯 ASCII
    python koi.py --still        # 只打印一帧（截图 / 测试用）
    python koi.py --width 100 --height 26

配色：浅蓝和灰的小鱼，另有一条大肥鱼是深蓝的。
依赖：只用标准库；输出纯 ASCII，Windows 控制台也能跑。
============================================================================
"""
import math
import os
import random
import shutil
import sys
import time

ESC = "\x1b["
RESET = ESC + "0m"

# ---- 颜色 ----------------------------------------------------------------
# 蓝色取的是 DSH 界面里「（平价 · xx小时后进入高峰）」那行字的蓝（主题 accent）。
ACCENT = (59, 130, 246)        # #3b82f6
C_LIGHT_BLUE = (110, 170, 255) # 浅一点
C_SKY = (150, 196, 255)        # 更浅
C_BLUE = ACCENT                # 大肥鱼：和界面文字同一个蓝
C_GREY = 245                   # 中灰（256 色）
C_GREY_LIGHT = 250             # 浅灰
C_WATER = 38           # 水面
C_PLANT = 35           # 水草
C_BUBBLE = 250
C_HINT = 240


def fg(c):
    """c 是 256 色号，或 (r, g, b) 真彩色。"""
    if isinstance(c, tuple):
        return ESC + "38;2;%d;%d;%dm" % c
    return ESC + "38;5;%dm" % c


# ---- 鱼的样子（尾巴两帧：A / B）-------------------------------------------
FISH_A = [
    r"      __    __ ",
    r"  ___/  \__/  \___ ",
    r" /   \__      __/   \ ",
    r"\__    \/    \/    __/",
    r"   \___/      \___/",
]

FISH_B = [
    r"       __    __ ",
    r"   ___/  \__/  \___ ",
    r"  /   \__      __/   \ ",
    r" \__    \/    \/    __/",
    r"    \___/      \___/",
]

# 大肥鱼：同一条鱼，多一圈肚子
FAT_A = [
    r"       __      __ ",
    r"   ___/  \__/  \___ ",
    r"  /   \__        __/   \ ",
    r" |       \______/       |",
    r"  \__    \/      \/    __/",
    r"     \___/        \___/",
]

FAT_B = [
    r"        __      __ ",
    r"    ___/  \__/  \___ ",
    r"   /   \__        __/   \ ",
    r"  |       \______/       |",
    r"   \__    \/      \/    __/",
    r"      \___/        \___/",
]

PLANT = [r"  )  (  ", r" ( ) )  ", r"  ) (   "]


class Koi(object):
    def __init__(self, art_a, art_b, color, x, y, speed, big):
        self.art_a = art_a
        self.art_b = art_b
        self.color = color
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.big = big
        self.phase = random.uniform(0, math.tau)
        self.bob = random.uniform(0.5, 1.1)

    def frame(self, t):
        return self.art_a if math.sin(t * 6.0 + self.phase) > 0 else self.art_b

    def width(self):
        return max(len(line) for line in self.art_a)


def make_koi(w, h, big=False, color=None):
    if big:
        return Koi(FAT_A, FAT_B, C_BLUE, w * random.uniform(0.15, 0.85),
                   random.uniform(3, max(4, h - 11)), random.uniform(1.1, 1.7), True)
    color = color if color is not None else C_LIGHT_BLUE
    return Koi(FISH_A, FISH_B, color, w * random.uniform(0.2, 0.95),
               random.uniform(3, max(4, h - 9)), random.uniform(1.8, 3.2), False)


def make_pond(w, h):
    """四条小鱼：两条浅蓝、两条灰；再加一条深蓝的大肥鱼。"""
    colors = (C_LIGHT_BLUE, C_GREY, C_SKY, C_GREY_LIGHT)
    fish = [make_koi(w, h, color=colors[i]) for i in range(4)]
    return fish + [make_koi(w, h, big=True)]


def compose(fish, w, h, t, calm, bubbles):
    """返回 (字符网格, 颜色网格)。鱼之间不互相覆盖：后画的鱼被前面的挡住。"""
    grid = [[" "] * w for _ in range(h)]
    col = [[None] * w for _ in range(h)]
    water_y = h - 2

    for x in range(w):
        ch = "_" if (x + int(t * 6)) % 11 == 0 else "~"
        if 0 <= water_y < h:
            grid[water_y][x] = ch
            col[water_y][x] = C_WATER

    px = max(0, (w - 12) // 2)
    for i, line in enumerate(PLANT):
        for j, ch in enumerate(line):
            if ch != " ":
                y = water_y - 3 + i
                if 0 <= y < h and 0 <= px + j < w:
                    grid[y][px + j] = ch
                    col[y][px + j] = C_PLANT

    if not calm:
        for bx, by in bubbles:
            by = int(by)
            if 1 <= by < water_y and 0 <= bx < w:
                grid[by][bx] = "."
                col[by][bx] = C_BUBBLE

    taken = [[False] * w for _ in range(h)]
    for k in sorted(fish, key=lambda k: 0 if k.big else 1):
        art = k.frame(t)
        bx = int(k.x)
        by = int(k.y + math.sin(t * k.bob + k.phase) * 1.5)
        for i, line in enumerate(art):
            y = by + i
            if y < 0 or y >= h:
                continue
            for j, ch in enumerate(line):
                if ch == " ":
                    continue
                x = bx + j
                if x < 0 or x >= w or taken[y][x]:
                    continue
                taken[y][x] = True
                grid[y][x] = ch
                col[y][x] = k.color

    hint = " koi.py   Ctrl+C exit "
    hx = max(0, w - len(hint) - 1)
    for i, ch in enumerate(hint):
        if hx + i < w:
            grid[0][hx + i] = ch
            col[0][hx + i] = C_HINT

    return grid, col


def encode(grid, col):
    out = []
    for y, row in enumerate(grid):
        buf = []
        last = None
        for x, ch in enumerate(row):
            c = col[y][x]
            if c != last:
                buf.append(fg(c) if c is not None else RESET)
                last = c
            buf.append(ch)
        if last is not None:
            buf.append(RESET)
        out.append("".join(buf))
    return "\n".join(out)


def plain(grid):
    return "\n".join("".join(row) for row in grid)


def size():
    try:
        s = shutil.get_terminal_size((80, 24))
        return max(30, s.columns), max(10, s.lines - 1)
    except Exception:
        return 80, 23


def main():
    argv = sys.argv[1:]
    calm = "--calm" in argv
    still = "--still" in argv
    force_color = "--color" in argv
    no_color = "--no-color" in argv
    nums = [a for a in argv if not a.startswith("--")]
    limit = float(nums[0]) if nums else None

    over_w = over_h = None
    for i, a in enumerate(argv):
        if a == "--width" and i + 1 < len(argv):
            over_w = int(argv[i + 1])
        if a == "--height" and i + 1 < len(argv):
            over_h = int(argv[i + 1])

    color = force_color or (not no_color and sys.stdout.isatty())

    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

    w, h = size()
    if over_w:
        w = max(20, over_w)
    if over_h:
        h = max(8, over_h)

    fish = make_pond(w, h)
    bubbles = []

    if still:
        xs = (0.03, 0.32, 0.58, 0.08, 0.58)
        fy = (0.06, 0.34, 0.60, 0.80, 0.20)
        for i, k in enumerate(fish):
            k.x = max(1, min(w * xs[i], w - k.width() - 1))
            top = 2
            bottom = max(top, h - (9 if k.big else 8))
            k.y = int(top + (bottom - top) * fy[i])
        for i in range(3):
            bubbles.append([int(w * (0.22 + 0.25 * i)), max(3, h - 8)])
        grid, col = compose(fish, w, h, 3.0, calm, bubbles)
        print(encode(grid, col) if color else plain(grid))
        return

    limit_t0 = time.time()
    t = 0.0
    last = time.time()
    sys.stdout.write(ESC + "?1049h" + ESC + "2J" + ESC + "?25l")
    sys.stdout.flush()
    try:
        while True:
            now = time.time()
            dt = min(0.12, now - last)
            last = now
            t += dt
            if limit and now - limit_t0 > limit:
                break

            nw, nh = size()
            if (nw, nh) != (w, h):
                w, h = nw, nh
                for k in fish:
                    k.y = min(k.y, max(3, h - 11))
                sys.stdout.write(ESC + "2J")

            for k in fish:
                k.x -= k.speed * 10.0 * dt
                if k.x < -k.width() - 2:
                    k.x = float(w) + random.uniform(0, 18)
                    k.y = random.uniform(3, max(4, h - 11))

            if not calm and random.random() < dt * 3:
                bubbles.append([random.randint(1, w - 2), h - 3])
            for b in bubbles:
                b[1] -= dt * 6.0
            bubbles = [b for b in bubbles if b[1] > 1][-24:]

            grid, col = compose(fish, w, h, t, calm, bubbles)
            body = encode(grid, col) if color else plain(grid)
            sys.stdout.write(ESC + "H" + body)
            sys.stdout.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(ESC + "?25h" + ESC + "?1049l")
        sys.stdout.flush()
        print("\n  鱼游走了。\n")


if __name__ == "__main__":
    main()
