# 通信协议 Hub

本章讲解 Demo 中的通信协议 Hub，包含 **UART**、**CAN**、**AT**、**RS485** 四个通信终端，通过二级页面统一入口访问。

## 功能概述

Comm Hub 是一个二级导航页面，展示 4 个协议入口图标，点击进入对应的交互终端：

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

### 3. AT 命令终端

### 4. RS485 终端

## 硬件连接

| 接口 | 板载端子/连接器 | 说明 |
|---|---|---|
| UART | USB-C → XR21B1411IL16 USB-UART | 通过 USB 连接 PC 通信 |
