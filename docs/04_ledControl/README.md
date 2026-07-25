# LED 控制

本章讲解 Demo 中的 LED 滑块功能，使用 **PWM** 控制开发板 STATUS LED 的亮度。

## 功能概述

- **PWM 通道**：PWM11
- **对应引脚**：Pin25（STATUS LED）
- **PWM 模式**：`ABOVE_1US`（高电平时间 ≥ 1μs）
- **频率**：约 1kHz（cycle = 1000μs）
- **控制方式**：滑块拖动 0% ~ 100% 调节占空比

## 运行效果

界面组成：
- 绿色灯泡图形（透明度随亮度变化）
- 百分比数字显示
- 亮度调节滑块
- 状态栏：`PWM CH:11 Duty:XX%`

## 代码解析

### 1. 初始化 PWM

```python
from misc import PWM

# cycleTime = 1000μs ≈ 1kHz
# 默认占空比 75%（highTime = 750μs）
pwm = PWM(PWM.PWM11, PWM.ABOVE_1US, 750, 1000)
pwm.open()
```

### 2. 滑块控制亮度

```python
# 滑块值变化回调
def _on_slider(self, e=None):
    v = self._slider.get_value()      # 0 ~ 100
    high = int(1000 * v / 100)        # 占空比 = highTime / cycleTime
    if high < 1:
        high = 1                       # ABOVE_1US 不接受 0
    self._pwm.open(PWM.ABOVE_1US, high, 1000)
```

### 3. 视觉反馈

```python
# 灯泡透明度随亮度 0~100% 映射到 alpha 0~255
bulb.set_style_bg_opa(int(255 * v / 100), 0)
```

### 4. 退出时释放

```python
def _on_back(self, e=None):
    self._pwm.close()     # 关闭 PWM 输出
    super()._on_back(e)
```

## 代码位置

[src/yttrium.py](../../src/yttrium.py) → `class LedPage(AppPage)`（第 121 行起）

## 涉及模块

| 模块 | 用途 |
|---|---|
| `misc.PWM` | PWM 硬件控制 |
| `lvgl` | 滑块控件（`lv.slider`）& UI 更新 |

## 关键参数说明

| 参数 | 值 | 说明 |
|---|---|---|
| PWM 通道 | `PWM.PWM11` | EG800Z 模组 PWM11 通道 |
| `ABOVE_1US` | 精度模式 | 保证占空比 ≥ 1μs，避免硬件异常 |
| `cycleTime` | 1000μs | 周期 1ms，频率 1kHz |
| `highTime` | `cycle × duty / 100` | 动态计算，随滑块变化 |
| 滑块范围 | 0 ~ 100 | 映射到占空比 0% ~ 100% |

## 硬件连接

STATUS LED 为板载 LED（绿色），由 EG800Z 模组 Pin25 直接驱动，无需外部接线。

> 如需控制其他 PWM 外设（如背光 LCD_PWM1），修改 `PWM.PWMxx` 通道号即可。
