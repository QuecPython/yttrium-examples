# 虚拟键盘

LVGL 内置 `lv.keyboard` 控件实现文本输入。

## 功能概述

- 多行输入框（支持换行）
- QWERTY 全键盘，贴屏底固定 160px 高
- 默认文本 "Yttrium-Dev"

## 关键代码

```python
ta = lv.textarea(self.screen)
ta.set_text("Yttrium-Dev")
ta.set_size(w - 12, screen_h - kb_h - base_y)

kb = lv.keyboard(self.screen)
kb.set_textarea(ta)      # 绑定输入框
kb.set_size(w, 160)      # 贴屏底
```

## 注意事项

- 不用 `set_one_line(True)`，否则回车无法换行
- `set_textarea()` 会自动调整键盘位置

## 代码位置

[src/keyboard.py](../../src/keyboard.py) → `class KeyboardPage(AppPage)`
