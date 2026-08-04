# 开发板介绍

## 概述

Yttrium 开发板基于 **Quectel EG800Z QuecOpen** 模组（EC718 系列），支持 LTE Cat.1 蜂窝通信，搭载 QuecPython 运行环境，集成 LCD 触控屏、以太网、CAN、RS485、音频、摄像头等丰富外设，适合 IoT 应用快速原型开发。

| 项目 | 说明 |
|---|---|
| 开发板型号 | EG800Z_LCD_V1.1（QEM800ZA-CN） |
| 主控模组 | Quectel EG800Z QuecOpen（EC718 系列） |
| 模组封装 | LCC |
| 设计版本 | V1.1（2025-03-26） |
| 制造商 | Quectel Wireless Solutions |

## 硬件规格

### 核心系统

| 项目 | 规格 |
|---|---|
| 模组 | EG800Z QuecOpen |
| 蜂窝网络 | LTE Cat.1 |
| 运行环境 | QuecPython（OpenCPU） |
| 存储 | 128Mbit SPI NOR Flash（XM25QH128C） |

### 显示与触控

| 项目 | 规格 |
|---|---|
| LCD 驱动 | ST7796 |
| 分辨率 | 320×480 竖屏 → 硬件旋转 480×320 横屏 |
| 接口 | SPI（16-pin FPC 连接器，FH34SRJ-16S-0.5SH） |
| 触控 | ft6x36，I2C 接口 |
| 背光 | PWM 调光（LCD_PWM1） |

### 音频

| 项目 | 规格 |
|---|---|
| 音频 Codec | ES8311 |
| 功放 | CS8126S |
| 接口 | PCM / I2S |
| 麦克风 | 板载 MIC |
| 扬声器 | 板载连接器（8-pin） |
| 蜂鸣器 | 板载蜂鸣器 |

### 通信接口

| 接口 | 芯片/说明 |
|---|---|
| 以太网 | CH390D（W5500 兼容），RJ45 带集成变压器，SPI 接口 |
| CAN | SIT65HVD230DR 收发器，3-pin 端子 |
| RS485 | SIT3088EESA 收发器，3-pin 端子 |
| USB | 双 USB-C 接口，XR21B1411IL16 USB-UART 桥接芯片 |
| UART | Main UART（TX/RX/RTS/CTS/DTR/DCD/RI）、Debug UART |
| I2C | I2C0 总线（连接触摸、Camera 等） |
| SPI | SPI0（以太网/Flash 切换）、LCD SPI、Camera SPI |
| SIM | 单 SIM 卡槽（USIM1，USIM2 仅预留引脚） |

### 其他外设

| 外设 | 说明 |
|---|---|
| Camera | 6-pin FPC 连接器，支持 GC0308，I2C + SPI 接口 |
| LED | 状态指示灯（Green）、网络指示灯（Green）、电源灯（Red） |
| 按键 | PWRKEY、RESET、BOOT、用户按键 |
| 天线 | U.FL 连接器（LTE 主天线，50Ω） |
| ADC | ADC0、ADC1 测试点 |
| GPIO | 多路 GPIO 引出（含 GPIO2/3/4/17 等） |

## 电源系统

| 电源轨 | 电压 | 最大电流 | 生成方式 |
|---|---|---|---|
| VBAT | 3.3V ~ 4.3V | 3A | DC 5V / USB VBUS 输入 → ETA2893E8A DC-DC（4V@3A） |
| VDD_EXT | 由模组输出 | — | EG800Z 内部 LDO |
| VDD_3V3 | 3.3V | 500mA | SGM2028-3.3 LDO |
| VDD_2V8 | 2.8V | 300mA | SGM2019-ADJ LDO |
| VDD_1V8 | 1.8V | 300mA | 板载 LDO（Camera 等外设供电） |

电源输入方式：DC 5V 端子 / USB-C VBUS / 电池 VBAT。

## Pin 定义

### LCD 接口（J0501，16-pin FPC）

| Pin | 信号 | 功能 |
|---|---|---|
| 1 | LED | 背光 PWM |
| 2 | LCD_CS | SPI 片选 |
| 3 | LCD_RST | 复位 |
| 4 | LCD_RS | 指令/数据选择 |
| 5 | SDI (MOSI) | SPI 数据输入 |
| 6 | LCD_SCK | SPI 时钟 |
| 7 | SDO (MISO) | SPI 数据输出 |
| 8 | CTP_SCL | 触摸 I2C 时钟 |
| 9 | CTP_RST | 触摸复位 |
| 10 | CTP_SDA | 触摸 I2C 数据 |
| 11 | CTP_INT | 触摸中断 |
| 12 | SD_CS | SD 卡片选（可选） |

### Camera 接口（J0503，6-pin FPC）

| Pin | 信号 | 功能 |
|---|---|---|
| 1 | CAM_VDD | 模拟供电 |
| 2 | CAM_VDDIO | IO 供电 |
| 3 | CAM_I2C_SCL | I2C 时钟 |
| 4 | CAM_I2C_SDA | I2C 数据 |
| 5 | GND | 地 |
| 6 | VCC | 电源 |

### 主要 GPIO 映射

| 模组 Pin | 功能 | 备注 |
|---|---|---|
| MAIN_TXD / MAIN_RXD | 主串口 | USB-UART 桥接 / RS485 切换 |
| DBG_TXD / DBG_RXD | 调试串口 | 独立 Debug 通道 |
| SPI0_CLK/SDI/SDO/CS | SPI0 | 以太网 / Flash 二选一（SEL_NET_FLASH 切换） |
| LCD_SPI_* | LCD 专用 SPI | 独立 SPI 通道 |
| I2C0_SCL/SDA | I2C0 | 触摸、Camera 共享 |
| CAN_RXD/TXD/STB | CAN 总线 | STB 待机控制 |
| PCM_CLK/SYNC/DIN/DOUT | 音频 PCM | 连接 ES8311 Codec |
| ADC0 / ADC1 | ADC 输入 | 测试点引出 |
| PWRKEY | 电源键 | 低电平开机 |
| RESET_N | 复位 | 低电平复位 |
| USB_BOOT | 烧录模式 | 进入下载模式 |
| STATUS / NET_STATUS | LED 指示 | 模组状态 / 网络状态 |
| WAKEUP0 | 唤醒 | 外部唤醒 |
| LED_PWM4 | LED PWM | 可调光 LED |
| BUZZER | 蜂鸣器 | GPIO 驱动 |

## 板载接口布局

参考 `datasheet/` 目录下的原理图和丝印图：

- `EG800Z_LCD_SCH_V1.1_20250326.pdf` — 原理图（7 页）
- `EG800Z_LCD_PCB_V1.1_20250326.pdf` — PCB 丝印图（Top + Bottom）

## 开发资源

| 资源 | 路径 |
|---|---|
| 固件包 | `firmware/` |
| 烧录工具 | `tools/FlashTools_V4.1.19_2509010.zip` |
| 串口工具 | `tools/sscom5.13.1.zip` |
| Demo 代码 | `src/yttrium.py` |
| 图标资源 | `icons/`、`images/` |
| 烧录教程 | [02_firmwareFlashing](../02_firmwareFlashing/README.md) |
| 运行教程 | [03_runDemo](../03_runDemo/README.md) |
