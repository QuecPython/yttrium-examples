# ADC 电压仪表盘

本章讲解 Demo 中的 ADC 电压仪表盘功能，使用 **ADC0** 实时采样电压并通过三色弧段仪表盘显示。

## 功能概述

- **ADC 通道**：ADC0
- **分辨率**：12-bit（0 ~ 4095）
- **采样范围**：0V ~ 3.3V
- **采样策略**：每 300ms 采集 6 次取平均，抑制抖动
- **分压比**：约 5.4:1（板上电阻分压，3.3V 输入 → raw ≈ 757）

## 运行效果

界面组成：
- 三色弧段仪表盘（绿 / 黄 / 红）
- 动态指针（随电压实时转动）
- 电压数值（精确到 0.01V）
- ADC Raw 值信息栏

## 仪表盘设计

| 弧段 | 角度范围 | 电压范围 | 颜色 |
|---|---|---|---|
| 绿色（安全） | 180° ~ 240° | 0V ~ 1.65V | `0x00E676` |
| 黄色（警告） | 240° ~ 300° | 1.65V ~ 3.3V | `0xFFEB3B` |
| 红色（危险） | 300° ~ 360° | > 3.3V | `0xFF5252` |

指针角度计算：
```
angle = 180° + (voltage / 3.3V) × 180°
0V → 180°（最左）
3.3V → 360°（最右）
```

## 代码解析

### 1. 初始化 ADC

```python
from misc import ADC

adc = ADC()
adc.open()
# scale = 3.3V / 757（实测 raw 值）= 约 0.00436 V/raw
# 3.3V 是 ADC 参考电压，757 是 3.3V 输入时的 raw 读数
# 板上电阻分压比约 5.4:1，实际待测电压 = raw × scale
```

### 2. 定时采样（lv.timer）

```python
# 每 300ms 触发一次，在主线程中采样（不阻塞 GUI）
self._adc_timer = lv.timer_create(self._adc_tick, 300, None)

def _adc_tick(self, timer):
    if not self._adc_active:
        return
    # 6 次采样取平均，滤除噪声
    samples = [self._adc.read(self._adc_chan) for _ in range(6)]
    samples = [s for s in samples if s is not None]
    raw = sum(samples) // len(samples)
    v = raw * self._adc_scale
```

### 3. 更新指针角度

```python
import math

vv = max(0.0, min(3.3, v))    # 限幅 0 ~ 3.3V
ang = math.radians(180 + (vv / 3.3) * 180)  # 转换为弧度

# 更新线段端点
self._p1.x = int(cx + (R - 16) * math.cos(ang))
self._p1.y = int(cy + (R - 16) * math.sin(ang))
self._needle.set_points([self._p0, self._p1], 2)
```

### 4. 退出时停止

```python
def _on_back(self, e=None):
    self._adc_active = False   # 停止采样标记
    # timer 仍在运行但 tick 回调检查 adc_active 为 False 直接 return
```

## 完整数据流

![数据流](images/adc-flow.png)

1. `lv.timer` 每 300ms 触发 `_adc_tick`
2. `ADC.read(ADC0)` × 6 次 → 取平均 raw
3. `raw × scale` → 电压值 V
4. 更新数值标签（`{:.2f}V`）
5. 计算角度 → 更新指针线段坐标
6. GUI 实时刷新

## 硬件连接

ADC0 测试点在板上有引出（参考 `datasheet/` 原理图 Sheet 7）。EG800Z 模组 ADC 输入经过板上电阻分压（约 5.4:1），实际输入电压范围为：

| 实际电压 | Raw 值（约） | 显示 |
|---|---|---|
| 0V | 0 | 0.00V |
| 1.65V | ~378 | 1.65V |
| 3.3V | ~757 | 3.30V |

> **注意**：`_adc_scale` 因板间差异需实测校准。用万用表测量 TP 点实际电压，记录对应 raw 值，重新计算 `scale = V_actual / raw`。

## 代码位置

[src/yttrium.py](../../src/yttrium.py) → `class AdcPage(AppPage)`（第 429 行起）

## 涉及模块

| 模块 | 用途 |
|---|---|
| `misc.ADC` | ADC 硬件采样 |
| `lvgl` | 弧段控件（`lv.arc`）、线段（`lv.line`）、定时器（`lv.timer`） |
| `math` | 角度计算（`math.cos`、`math.sin`、`math.radians`） |
