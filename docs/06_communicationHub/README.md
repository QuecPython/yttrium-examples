# 通信协议 Hub

本章讲解 Demo 中的通信协议 Hub，包含 **UART**、**CAN**、**AT**、**RS485** 四个通信终端，通过二级页面统一入口访问。

## 功能概述

Comm Hub 是一个二级导航页面，展示 4 个协议入口图标，点击进入对应的交互终端：

![Comm Hub](images/comm-hub.png)

| 协议 | 状态 | 说明 |
|---|---|---|
| UART | ✅ 已调通 | 串口终端，TX/RX 收发 + 键盘输入 |
| CAN | 界面就绪 | CAN 总线监控终端 |
| AT | 界面就绪 | AT 命令交互终端，真实 atcmd 收发 |
| RS485 | 界面就绪 | RS485 Modbus 终端 |

## 导航架构

```
主屏幕 → Comm Hub（二级页面）
              ├── UART → UART 终端
              ├── CAN  → CAN 终端
              ├── AT   → AT 终端
              └── RS485 → RS485 终端
```

- Comm Hub 的返回按钮 → 回到主屏幕
- 子页面（UART/CAN/AT/RS485）的返回按钮 → 回到 Comm Hub

## 各协议详解

### 1. UART 串口终端

![UART 界面](images/uart-terminal.png)

| 参数 | 值 |
|---|---|
| 端口 | UART2 |
| 波特率 | 115200 |
| 数据位 | 8 |
| 校验 | None |
| 停止位 | 1 |
| 流控 | 无 |

界面组成：
- 状态栏：`UART2:115200`
- 日志区（最多 6 行）：TX（青色）/ RX（绿色）双向日志
- 输入区：LVGL 虚拟键盘 + textarea

```python
# UART 初始化
from machine import UART
uart = UART(UART.UART2, 115200, 8, 0, 1, 0)
# 发送
uart.write(data.encode())
# 接收（lv.timer 轮询）
rx_data = uart.read(uart.any())
```

### 2. CAN 总线终端

![CAN 界面](images/can-terminal.png)

| 参数 | 值 |
|---|---|
| 速率 | 500kbps |
| 收发器 | SIT65HVD230DR |
| 模组引脚 | CAN_RXD / CAN_TXD / CAN_STB |

界面组成：
- 状态栏：`CAN:500kbps`
- 日志区：显示发送/接收的 CAN 帧
- 输入区：键盘 + textarea 输入帧数据

硬件连接：EG800Z 模组 CAN 引脚 → SIT65HVD230DR 收发器 → 3-pin 端子（CANH / CANL / GND）。

### 3. AT 命令终端

![AT 界面](images/at-terminal.png)

界面组成：
- 状态栏：`Modem: Ready`
- 日志区（最多 6 行）：AT 命令及响应
- 输入区：键盘 + textarea 输入 AT 命令

```python
import atcmd
# 发送 AT 命令并接收响应
response = atcmd.send("AT+CSQ\r\n")
```

### 4. RS485 终端

![RS485 界面](images/rs485-terminal.png)

| 参数 | 值 |
|---|---|
| 波特率 | 9600 |
| 数据位 | 8 |
| 校验 | None |
| 停止位 | 1 |
| 收发器 | SIT3088EESA |
| 接线 | A / B 差分线 |

界面组成：
- 状态栏：`RS485:9600-8-N-1 A/B`
- 日志区：TX（青色）/ RX（绿色）Modbus 帧
- 输入区：键盘 + textarea 输入 Modbus 命令

**RS485 方向控制**：`RS485_TX/RX_Select` 信号（高 = TX，低 = RX），由驱动层自动切换，应用层无需干预。

## 通用代码结构

四个协议终端页面共享相同的架构：

```
ProtocolPage(AppPage)
├── 状态栏（lv.obj + lv.label）
├── 日志区（lv.obj，深色终端背景，最多 6 行）
│   └── 彩色标签（TX=青色 / RX=绿色 / 系统=灰色）
├── 输入区（lv.textarea + lv.keyboard）
│   └── 发送按钮 → 调用协议 API → 追加日志
└── _on_back() → 回到 Comm Hub
```

## 代码位置

| 文件 | 行号 | 内容 |
|---|---|---|
| [src/yttrium.py](../../src/yttrium.py) | L3121 | `CommHubPage` — Hub 页面 |
| | L3181 | `UartPage` — UART 终端 |
| | L728 | `CanPage` — CAN 终端 |
| | L3404 | `AtPage` — AT 终端 |
| | L3607 | `Rs485Page` — RS485 终端 |

## 涉及模块

| 模块 | 用途 |
|---|---|
| `machine.UART` | 硬件串口收发 |
| `atcmd` | AT 命令发送/接收 |
| `lvgl` | 终端 UI（键盘、文本框、日志行） |

## 硬件连接

| 接口 | 板载端子/连接器 | 说明 |
|---|---|---|
| UART | USB-C → XR21B1411IL16 USB-UART | 通过 USB 连接 PC 通信 |
| CAN | J0602 3-pin 端子（CANH/CANL/GND） | 外接 CAN 总线设备 |
| RS485 | J0403 3-pin 端子（A/B/GND） | 外接 RS485 总线设备 |
| AT | 模组内部 AT 引擎 | 无需外部连接 |
