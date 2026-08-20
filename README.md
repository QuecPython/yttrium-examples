# Yttrium大屏开发板

基于 **QuecPython + LVGL** 的 Quectel EC718 开发板综合 Demo 应用，480×320 横屏触控界面。

## 硬件

| 组件 | 型号 |
|---|---|
| 主控 | Quectel EC718 |
| LCD | ST7796, 320×480 竖屏 → 硬件旋转 480×320 横屏 |
| 触摸 | ft6x36 (I2C) |
| 网卡 | W5500 (SPI) |

## 部署

将 `src/*.py` 和 `icons/`、`images/` 目录使用QPYCom放到设备 `/usr` 根目录，右键_main.py运行代码：

## 功能清单

### 主屏幕（5×3 图标网格）

| 图标 | 功能 | 说明 |
|---|---|---|
| LED | LED 滑块 | PWM 调光（pin25），滑块控制亮度 |
| Clock | 时钟 + 秒表 | 实时时钟 + 计次秒表 |
| ADC | 电压仪表盘 | 三色弧段仪表，ADC0 实时采样 |
| Calc | 计算器 | 四则运算 + 百分比，5×4 按钮 |
| Comm | **通信协议 Hub** | 二级页面，4 个协议入口 |
| Key | 虚拟键盘 | LVGL 内置键盘 + 文本框 |
| Camera | 摄像头预览 | GC0308 取景框 + 快门键 |
| QR | **饮品选购 Demo** | Coffee / Milk Tea 选购 → 付款二维码 |
| Audio | 录音播放 | 波形显示 + Rec/Play/Stop |
| USB | U 盘浏览器 | 文件列表 + 目录切换 |
| Phone | 电话拨号 | 拨号键盘 + CALL/Back |
| Game | **游戏 Hub** | 二级页面，3 个游戏入口 |
| ETH | **以太网 Hub** | 二级页面，3 个功能入口 |
| Buzzer | 蜂鸣器 | 蜂鸣器控制 |
| Weather | 天气 | 天气信息展示 |

### 通信协议 Hub（Comm）

| 协议 | 功能 | 状态 |
|---|---|---|
| UART | 串口终端，TX/RX 收发 + 键盘输入 | ✅ 已调通 |
| CAN | CAN 总线监控终端 | 界面就绪 |
| AT | AT 命令交互终端，真实 atcmd 收发 | 界面就绪 |
| RS485 | RS485 Modbus 终端 | 界面就绪 |

### 游戏 Hub（Game）

| 游戏 | 说明 |
|---|---|
| Snake | 贪吃蛇，34×20 网格，触摸滑动操控 |
| 2048 | 经典 2048，4×4 网格，滑动合并 |
| Tetris | 俄罗斯方块 |

### 以太网 Hub（ETH）

| 功能 | 说明 |
|---|---|
| IP | 网络信息（W5500 初始化、ipconfig、DHCP） |
| PING | Ping 诊断工具 |
| TCP | TCP Client 终端 |

### 饮品选购 Demo（QR）

- Coffee / Milk Tea 两个 Tab，各 4 个商品
- 商品卡片：图片 + 名称 + 价格 + 勾选圆
- 选中商品 → Pay → 弹出付款二维码 + 总价
- 商品图片放 `U:/images/`

## 目录结构

```
YttriumEC718/
├── README.md
├── src/
│   └── yttrium.py          # 主应用（自包含，单文件 ~4300 行）
├── icons/                  # 48×48 PNG 图标（~60 个）
├── images/                 # 商品图片（100×70，8 张）
├── firmware/               # EC718 固件
└── _sch/                   # 原理图截图
```

## API 依赖

| 模块 | 用途 |
|---|---|
| `lvgl` | GUI 框架 |
| `machine` (LCD, Pin, UART) | 硬件驱动 |
| `tp.ft6x36` | 触摸驱动 |
| `misc` (PWM, ADC, Power) | 外设控制 |
| `atcmd` | AT 指令发送 |
| `ethernet` (W5500) | 以太网 |
| `qrcode` | 二维码生成 |
| `_thread`, `utime` | 线程 + 定时 |

## 开发说明

- 界面基类 `AppPage` 统一管理标题栏和返回按钮
- 所有页面通过 `PAGE_MAP` 字典注册，`MainScreen._open_page()` 统一导航
- 二级 Hub（Game / Comm / ETH）通过 `lv.scr_load()` 整页切换
- 键盘输入采用 `lv.keyboard` + `lv.textarea` 模式，定时器 pin 住键盘位置
- 参考正点原子 HMI 串口屏案例设计交互

