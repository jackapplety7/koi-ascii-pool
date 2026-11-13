# koi.py — 终端里游动的 ASCII 锦鲤

单文件、零依赖的终端动画：几条锦鲤在池塘里横着游，尾巴一摆一摆，水面有波纹，
水底有水草和上升的气泡。纯 ASCII 输出 + 256 色/真彩色，Windows / macOS / Linux 都能跑。

```
        __    __                                                  koi.py   Ctrl+C exit  
    ___/  \__/  \___                                                                    
   /   \__      __/   \                                                                 
  \__    \/    \/    __/                                                                
     \___/      \___/                                      __      __                   
                                                       ___/  \__/  \___                 
                                                      /   \__        __/   \            
                                   __    __          |       \______/       |           
                               ___/  \__/  \___       \__    \/      \/    __/          
                              /   \__      __/   \       \___/  __    \___/             
                             \__    \/    \/    __/   ___/  \__/  \___                  
                                \___/      \___/     /   \__      __/   \               
              __    __                              \__    \/    \/    __/              
          ___/  \__/  \___                             \___/      \___/                 
         /   \__      __/   \                                                           
        \__    \/    \/    __/                                                          
           \___/      \___/                                                             
                                                                                        
                                                                                        
                                        )  (                                            
                                       ( ) )                                            
                                        ) (                                             
~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~~~~~_~~~~~~
```

## 跑起来

```bash
python koi.py                 # 一直在游，Ctrl+C 退出
python koi.py 30              # 游 30 秒后退出
python koi.py --calm          # 不要气泡
python koi.py --no-color      # 纯 ASCII，不上色（录屏/老终端）
python koi.py --color         # 输出到管道也强制上色
python koi.py --still         # 只打印一帧（截图 / 当壁纸）
python koi.py --width 100 --height 26
```

只要 Python 3.7+，不用装任何东西。

## 配色

蓝色用的是 DSH 界面里「平价 · xx小时后进入高峰」那行字的蓝（`--dsw-alias-state-info-primary`，`#3b82f6`）。
颜色常量都在文件开头，改一行就能换：

```python
ACCENT = (59, 130, 246)        # #3b82f6，大肥鱼
C_LIGHT_BLUE = (110, 170, 255) # 浅一档的小鱼
C_SKY = (150, 196, 255)        # 再浅一档
C_GREY = 245                   # 256 色号也行
C_GREY_LIGHT = 250
```

`fg()` 同时支持 RGB 元组（真彩色 `ESC[38;2;r;g;bm`）和 256 色号；终端不支持真彩色时换成最接近的色号。

## 结构

- `Koi`：一条鱼（两帧图形、颜色、位置、速度、摆尾相位、上下浮动）
- `make_pond()`：四条小鱼（浅蓝/灰）+ 一条大肥鱼（蓝，多一圈肚子）
- `compose()`：把水面、水草、气泡、鱼画进字符网格与颜色网格；鱼之间用占用表，后画的鱼不会把前一条糊掉
- `encode()`：按颜色游程输出 ANSI；`plain()` 是 No-Color 分支
- `main()`：备用屏幕、逐帧渲染、每 30 帧检查一次终端尺寸

## 同一套配色用在 DSH 桌面版

背景锦鲤池是 `@tal-shin/dsh-koi-pond` 插件，配置在 `~/.dsh/profiles/desktop/cordis.patch.yml`：

```yaml
- id: koi-pond
  name: '@tal-shin/dsh-koi-pond'
  config:
    fish: 6
    palette: cool
    young: true
```

插件自带的调色池只有 `mixed / warm / cool / mono`，`cool` 里原本还有绿(jade)和紫(plum)。
只想要蓝和灰，就改插件本体 `client.js` 的 `ACCENT_PRESETS.cool`：

```js
cool: ['blue', 'silver', 'pearl'],
```

让靠输入栏的那条鱼固定变蓝：在 `seed()` 建鱼循环后取画面最下方的一条：

```js
const nearest = this.koi.reduce((a, b) => (b.nodes[1] > a.nodes[1] ? b : a));
nearest.accent = ACCENTS.blue;
```

## 坑

- Windows 老控制台默认不解析 ANSI，脚本里已经 `SetConsoleMode(..., 7)` 打开 VT。
- 界面文字别用中文宽度字符，否则 `ljust` 对齐会错行。
- 终端不支持真彩色时，鱼会退回 256 色近似值。

## 许可

MIT。见 [LICENSE](LICENSE)。
