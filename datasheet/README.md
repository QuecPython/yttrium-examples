# 相关资料归集

Yttrium 开发板相关设计资料和规格文档。

## 文件清单

### 原理图与 PCB

| 文件 | 说明 | 页数 |
|---|---|---|
| `EG800Z_LCD_SCH_V1.1_20250326.pdf` | 原理图：EG800Z 模块 + LCD + 外设电路 | 7 页 |
| `EG800Z_LCD_PCB_V1.1_20250326.pdf` | PCB 丝印图：Top 层 + Bottom 层 | 2 页 |

> 密码：`quectel`
>
> 原理图分页：Sheet 1 封面 / Sheet 2 EG800Z 模块引脚 / Sheet 3 电源 / Sheet 4 USB + RS485 / Sheet 5 LCD + Camera + 音频 / Sheet 6 以太网 + CAN + Flash / Sheet 7 按键 + LED + 蜂鸣器

### 产品文档

| 文件 | 说明 | 页数 |
|---|---|---|
| `QuecPython_Yttrium 开发板介绍.pdf` | QuecPython 官方开发板介绍：接口布局、开关说明、基础参数 | 9 页 |
| `Yttrium开发板_产品规格书_V1.0.1.pdf` | 产品规格书：详细接口表、电气参数、尺寸重量、认证信息 | 22 页 |

## 关键信息速查

### 拨码开关

| 开关 | 功能 |
|---|---|
| S0301 | 供电方式选择：DC 5V / USB Type-C |
| S0401 | 主 UART 连接：USB UART / RS485 |
| S0601 | SPI0 连接：NET（以太网）/ FLASH |
| S0705 | 蜂鸣器复用：1-3 导通 → GPIO2 控制蜂鸣器 |

### 接口连接器

| 编号 | 类型 | 信号 |
|---|---|---|
| J0501 | 16-pin FPC | LCD（SPI + 触摸 I2C） |
| J0503 | 6-pin FPC | Camera |
| J0601 | RJ45 | 以太网 |
| J0602 | 3-pin 端子 | CAN |
| J0403 | 3-pin 端子 | RS485 |
| J0702 | 8-pin 排针 | 预留：MAIN_TXD/RXD、LCD、CTP_INT、GND、ADC |
| J0703 | 8-pin 排针 | 预留：QSPI、LCD 信号 |
