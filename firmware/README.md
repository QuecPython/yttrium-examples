# 固件使用说明

## 1、固件说明

### 固件文件

| 文件 | 说明 |
|---|---|
| `EG800ZCNLAR05A01M04_Yttrium_OCPU_QPY.7z` | Yttrium 开发板 QuecPython OpenCPU 固件 |

### 固件命名规则

`EG800Z CN L A R05A01M04 _ Yttrium _ OCPU_QPY`

- **EG800Z**：模组型号（Quectel EC718 系列，EG800Z 变体）
- **CN**：中国区域频段配置
- **L**：LCC 封装
- **A**：标准版本标识
- **R05A01M04**：固件版本号
- **Yttrium**：适配开发板代号
- **OCPU_QPY**：OpenCPU + QuecPython 运行环境

### 支持功能

| 类别 | 说明 |
|---|---|
| 系统 | QuecPython 标准库，OpenCPU 多线程（`_thread`） |
| GUI | LVGL 图形框架，支持 480×320 横屏触控 |
| LCD | ST7796 驱动，SPI 接口 |
| 触摸 | ft6x36 触摸驱动，I2C 接口 |
| 网络 | W5500 以太网（SPI），TCP/IP 协议栈 |
| 蜂窝 | LTE Cat.1 通信（EG800Z 模组） |
| 音频 | 录音与播放 |
| 外设 | GPIO、PWM、ADC、UART、CAN、RS485、I2C、SPI |
| USB | U 盘 Mass Storage 读写（暂不支持） |
| 摄像头 | GC0308 摄像头驱动（暂不支持） |
| 存储 | 文件系统 |

### API 依赖

| 模块 | 用途 |
|---|---|
| `lvgl` | GUI 框架 |
| `machine` | 硬件驱动（LCD、Pin、UART 等） |
| `tp.ft6x36` | 触摸驱动 |
| `misc` | 外设控制（PWM、ADC、Power） |
| `atcmd` | AT 指令收发 |
| `ethernet` (W5500) | 以太网通信 |
| `qrcode` | 二维码生成 |
| `_thread`、`utime` | 多线程 + 定时器 |
| `camera` | 摄像头驱动（暂不支持） |

> 固件烧录步骤详见 [docs/02_firmwareFlashing](../docs/02_firmwareFlashing/README.md)
