# 饮品选购 Demo

本章讲解 Demo 中的饮品选购功能，包含 **商品浏览**、**Tab 切换**、**购物车勾选** 和 **二维码付款** 完整流程。

## 功能概述

一个完整的饮品选购 → 支付 Demo，模拟线下点单场景：

| 特性 | 说明 |
|---|---|
| 双 Tab | Coffee（4 款）/ Milk Tea（4 款） |
| 商品卡片 | 图片 + 名称 + 价格 + 勾选圆 |
| 实时总价 | 底部 Total 随勾选动态更新 |
| 二维码付款 | Pay → 全屏付款页 → 二维码 + 总价 + 明细 |

## 交互流程

```
商品选购页（Coffee / Milk Tea Tab）
  ├── 点击 Tab 切换类别
  ├── 点击勾选圆 选中/取消 商品
  ├── 底部 Total 实时更新
  └── 点击 Pay 按钮
        └── 付款页（全屏）
              ├── 二维码（qrcode 模块生成）
              ├── Total: $XX
              ├── 订单明细
              └── < Back 返回选购页
```

## 代码解析

### 1. 商品数据

```python
COFFEE = (
    ("U:/images/coconut.jpg",    "Coconut",     "$18"),
    ("U:/images/americano.jpg",  "Americano",   "$15"),
    ("U:/images/Mint.jpg",       "Mint",        "$20"),
    ("U:/images/hazelnut.jpg",   "Hazelnut",    "$22"),
)
TEA = (
    ("U:/images/bubble.jpg",     "Bubble",      "$14"),
    ("U:/images/pudding.jpg",    "Pudding",     "$16"),
    ("U:/images/Brown_sugar.jpg","Brown Sugar", "$15"),
    ("U:/images/taro_bobo.jpg",  "Taro Bobo",   "$18"),
)
```

每个商品 = `(图片路径, 名称, 价格)`。图片位于 `U:/images/` 目录下。

### 2. Tab 切换

```python
def _on_tab(self, tab):
    if tab == "Coffee":
        self._active_tab = self.TAB_COFFEE
        self._tab_coffee.set_style_bg_color(0x6F4E37)  # 棕色高亮
        self._tab_tea.set_style_bg_color(0x334466)     # 灰色未选中
        # 延迟 50ms 切换，避免 UI 闪烁
        lv.timer_create(lambda t: self._do_switch(), 50, None)
    elif tab == "Milk Tea":
        # 奶茶 Tab 高亮为奶茶色
        ...
```

### 3. 商品卡片

每张卡片结构：

```
┌──────────────────┐
│                  │
│    商品图片      │  ← lv.img, 100×70
│                  │
├──────────────────┤
│ Coconut     (○)  │  ← 名称 + 勾选圆按钮
│ $18              │  ← 价格（橙色）
└──────────────────┘
```

卡片背景 `0x16213E`（深蓝），圆角 6px。

### 4. 选中 / 取消

```python
def _on_select(self, idx, btn):
    if idx in self._selected:
        self._selected.discard(idx)
        btn.set_style_bg_opa(lv.OPA.TRANSP, 0)       # 空心
        btn.set_style_border_color(0x888888, 0)        # 灰色边框
    else:
        self._selected.add(idx)
        btn.set_style_bg_color(0x00E676, 0)            # 绿色填充
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_border_color(0x00E676, 0)        # 绿色边框
    self._update_total()  # 更新底部总价
```

### 5. 总价计算

```python
def _update_total(self):
    items = self.COFFEE if active_tab == COFFEE else self.TEA
    total = sum(int(items[idx][2].replace("$", "")) for idx in self._selected)
    self._total_lbl.set_text("Total: $" + str(total))
```

### 6. 二维码付款

```python
def _do_pay(self):
    # 生成付款文本
    pay_text = "YttriumPay\nTotal:${}\n{}".format(total, ",".join(order))

    # 调用 qrcode 模块生成矩阵
    import qrcode
    result = qrcode.getQRData(pay_text, 1, 0xFFFF, 0x0000)

    # 全屏付款页：白底卡片 + 二维码方块 + 总价 + 明细
    # 二维码用 lv.obj 方块逐格绘制（黑色方块 on 白色背景）
```

付款页面结构：

```
┌──────────────────────┐
│  < Back              │  ← 返回按钮
│                      │
│    Scan to Pay       │  ← 标题
│  ┌──────────────┐    │
│  │              │    │
│  │   二维码      │    │  ← 120×120 白底 + 黑色方块
│  │              │    │
│  └──────────────┘    │
│  Total: $50          │  ← 总价
│  Coconut, Mint       │  ← 前 4 个商品名
└──────────────────────┘
```

## 商品图片清单

| 文件 | 对应商品 |
|---|---|
| `U:/images/coconut.jpg` | Coconut |
| `U:/images/americano.jpg` | Americano |
| `U:/images/Mint.jpg` | Mint |
| `U:/images/hazelnut.jpg` | Hazelnut |
| `U:/images/bubble.jpg` | Bubble |
| `U:/images/pudding.jpg` | Pudding |
| `U:/images/Brown_sugar.jpg` | Brown Sugar |
| `U:/images/taro_bobo.jpg` | Taro Bobo |

图片尺寸建议 100×70，项目 `images/` 目录中提供。

## 代码位置

[src/qr_shop.py](../../src/qr_shop.py) → `class QrPage(AppPage)`

## 涉及模块

| 模块 | 用途 |
|---|---|
| `lvgl` | UI 控件（卡片、按钮、标签、图片） |
| `qrcode` | 二维码矩阵生成（`getQRData`） |
