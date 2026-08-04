# 时钟 + 秒表

本章讲解 Demo 中的时钟与秒表功能，左侧实时时钟，右侧秒表计时。

## 功能概述

- 左半区：绿字大时间 + 日期星期
- 右半区：秒表（计次/复位/启动/暂停）

## 运行效果

左侧 `HH:MM:SS`（绿色大字）+ 日期星期行，中间竖线分隔，右侧秒表显示 + Lap / Reset / Start / Stop 四个按钮。

## 代码解析

### 时钟更新

```python
t = utime.localtime()
self._time_lbl.set_text("{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
self._date_lbl.set_text("{:04d}/{:02d}/{:02d} {:s}".format(
    t[0], t[1], t[2], ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")[t[6]]))
```

### 秒表驱动

```python
# lv.timer 每 20ms 累加
self._elapsed += 20
m = self._elapsed // 60000
s = (self._elapsed // 1000) % 60
ms = (self._elapsed // 10) % 100
```

### 按钮操作

| 按钮 | 功能 |
|---|---|
| Lap | 计次（记录当前时间） |
| Reset | 复位归零 |
| Start | 开始 |
| Stop | 暂停 |

## 代码位置

[src/clock.py](../../src/clock.py) → `class ClockPage(AppPage)`

## 涉及模块

| 模块 | 用途 |
|---|---|
| `utime` | 系统时间 |
| `lvgl` | label、btn、timer |
