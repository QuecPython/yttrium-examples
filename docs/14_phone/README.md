# 电话拨号

模拟手机拨号键盘，支持号码输入和通话状态管理。

## 功能概述

- 标准 3×4 数字键盘（1-9、*、0、#）
- 顶部号码显示 + Del 按钮
- CALL（绿）/ Back（灰）操作按钮
- 通话状态机：IDLE → CALLING → ACTIVE / INCOMING

## 按键布局

```
┌─────┬─────┬─────┐
│  1  │  2  │  3  │
│  4  │  5  │  6  │
│  7  │  8  │  9  │
│  *  │  0  │  #  │
├─────┴─────┴─────┤
│   CALL    Back  │
└─────────────────┘
```

## 通话状态

| 状态 | CALL 按钮 | Back 按钮 |
|---|---|---|
| IDLE | CALL（绿） | Back（灰） |
| CALLING | 置灰 | Hangup（红） |
| ACTIVE | 置灰 | Hangup（红） |
| INCOMING | Answer（绿） | Reject（红） |

## 代码位置

[src/phone.py](../../src/phone.py) → `class PhonePage(AppPage)`

## 涉及模块

| 模块 | 用途 |
|---|---|
| `lvgl` | btn、label 布局 |
| `voiceCall` | 通话 API（可选） |
