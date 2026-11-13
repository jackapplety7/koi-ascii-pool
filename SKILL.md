---
name: ascii-koi-pond
description: 在终端里养一池会游动的 ASCII 锦鲤（单文件 Python、只用标准库），并附带把 DSH 背景锦鲤池（dsh-glass 的 koi-pond 插件）调成蓝/灰配色、让靠输入栏那条鱼变蓝的做法。用户提到终端锦鲤、ASCII 动画、桌面宠物、koi.py、koi-pond 配色时使用。
---

# ASCII 锦鲤池

## 概览

`koi.py` 是单文件、零依赖的终端动画：几条锦鲤在池塘里横向游动，尾巴两帧摆动，水面有波纹，
水底有水草和上升的气泡。纯 ASCII 输出 + 256 色/真彩色，Windows 控制台也能跑。

同一套配色也用于 DSH 桌面版背景里的锦鲤池（`@tal-shin/dsh-koi-pond` 插件）。

## 快速开始

```bash
python koi.py                 # 一直在游，Ctrl+C 退出
python koi.py 30              # 游 30 秒
python koi.py --calm          # 不要气泡
python koi.py --no-color      # 纯 ASCII，不上色
python koi.py --color         # 输出到管道也强制上色
python koi.py --still         # 只打印一帧（截图/测试）
python koi.py --width 100 --height 26
```

## 结构

- `Koi`：一条鱼（两帧图形、颜色、位置、速度、摆尾相位）
- `make_pond()`：四条小鱼 + 一条大肥鱼
- `compose()`：水面、水草、气泡、鱼画进字符网格 + 颜色网格；鱼之间用占用表互不覆盖
- `encode()`：颜色游程编码成 ANSI；`plain()` 是 No-Color 分支
- `main()`：备用屏幕、逐帧渲染、每 30 帧检查终端尺寸

## 自定义

颜色常量在文件开头，蓝色取的是 DSH 界面「平价 · xx小时后进入高峰」那行字的蓝
（`--dsw-alias-state-info-primary`，`#3b82f6`）：

```python
ACCENT = (59, 130, 246)        # #3b82f6，大肥鱼
C_LIGHT_BLUE = (110, 170, 255) # 浅一档的小鱼
C_SKY = (150, 196, 255)        # 再浅一档
C_GREY = 245                   # 256 色号也可以
C_GREY_LIGHT = 250
```

`fg()` 同时支持 RGB 元组（真彩色）和 256 色号。鱼的数量在 `make_pond()` 里改。

## DSH 背景锦鲤池（koi-pond 插件）

配置在 `~/.dsh/profiles/desktop/cordis.patch.yml` 末尾，按 id 覆盖：

```yaml
- id: koi-pond
  name: '@tal-shin/dsh-koi-pond'
  config:
    fish: 6
    palette: cool
    young: true
```

插件调色池只有 `mixed / warm / cool / mono`，且 `cool` 原本含绿(jade)、紫(plum)。
只要蓝和灰，就改插件本体 `ACCENT_PRESETS.cool`：

```js
cool: ['blue', 'silver', 'pearl'],
```

并把 `ACCENTS.blue` 设成想要的蓝。让**靠输入栏的那条鱼**固定变蓝：在 `seed()` 建鱼循环之后：

```js
const nearest = this.koi.reduce((a, b) => (b.nodes[1] > a.nodes[1] ? b : a));
nearest.accent = ACCENTS.blue;
```

改完刷新窗口（必要时重启 DSH）生效。

## 坑

- Windows 老控制台默认不解析 ANSI：脚本里已 `SetConsoleMode(..., 7)` 打开 VT。
- 界面文字别用中文宽度字符，`ljust` 对齐会错行。
- 插件是本地解包副本（`~/.dsh/plugins/dsh-glass-main/koi-pond`），重装/更新会覆盖，改前备份 `client.js.bak-koi`。
- 改完 `client.js` 用 `node --check`（复制成 `.mjs`）验一遍。
