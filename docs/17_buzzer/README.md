# 蜂鸣器

GPIO 驱动板载蜂鸣器，短响 Beep 和持续响 On/Off。

## 硬件连接

蜂鸣器通过拨码开关 **S0705** 连接到 GPIO2：

> S0705 的 1-3 导通 → GPIO2 作为蜂鸣器 BEEP 的控制

电路：`EG800Z GPIO2 → R0701(1K) → Q0701(DTC043ZEBTL) → BUZ0701`

## 功能

- Beep：短响 150ms
- On / Off：持续响 / 关闭
- 状态显示：Ready / Beeping... / Sustained ON

## 关键代码

```python
from machine import Pin
buz = Pin(Pin.GPIO2, Pin.OUT, Pin.PULL_DISABLE, 0)

# 短响
buz.write(1); utime.sleep_ms(150); buz.write(0)

# 持续
buz.write(1)   # 开
buz.write(0)   # 关
```

## 代码位置

[src/buzzer.py](../../src/buzzer.py) → `class BuzzerPage(AppPage)`
