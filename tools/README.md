# 工具

案例开发使用到的工具集合。

## 工具清单

| 工具 | 文件 | 版本 | 用途 |
|---|---|---|---|
| FlashTools | `FlashTools_V4.1.19_2509010.zip` | V4.1.19 | 固件烧录工具，将 `.pac` 固件包烧录到 EG800Z 模组 |
| QPYcom | `QPYcom_V4.2.0.zip` | V4.2.0 | QuecPython 串口交互工具：REPL 终端、文件传输、一键导入代码 |
| SSCOM | `sscom5.13.1.zip` | V5.13.1 | 通用串口调试工具，备选终端 |

## 使用说明

### FlashTools

1. 解压后运行 `FlashTools.exe`
2. 选择固件目录中的 `quec_download_usb.ini`
3. USB 连接开发板，选择 Quectel USB AT Port
4. 勾选 Erase All (User Mode) 和 Erase NVM
5. 点击 Reset and download 开始烧录

> 详见 [02_firmwareFlashing](../docs/02_firmwareFlashing/README.md)

### QPYcom

1. 解压后运行 QPYcom
2. 选择 Quectel USB AT Port，波特率 115200
3. 点击打开串口，按 Enter 进入 REPL
4. 右键 `/usr/` 目录 → 一键导入 → 选择 `src/` 文件夹部署代码

> 详见 [03_runDemo](../docs/03_runDemo/README.md)

### SSCOM

通用串口调试工具，支持多种波特率，用于替代 QPYCOM 进行基础串口通信测试。默认波特率 115200。

## 文件大小

> 注意：`QPYcom_V4.2.0.zip` 约 194MB，已加入 `.gitignore`，需从移远官方渠道单独下载。
