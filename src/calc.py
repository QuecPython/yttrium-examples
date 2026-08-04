# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class CalcPage(AppPage):
    """基础计算器 -- 四则运算，5x4 按钮网格。"""

    # -- 颜色 --
    C_NUM   = 0x334466
    C_OP    = 0x0F3460
    C_FUNC  = 0x2C3E50
    C_EQ    = 0x00E676
    C_TXT   = 0xFFFFFF

    # -- 布局（内容区 480x286）--
    DISP_H  = 48          # 显示栏高度
    COLS    = 4
    ROWS    = 5
    COL_W   = 120         # 480 // 4，满宽
    ROW_H   = 47          # (286 - 48) // 5

    # (文字, 颜色, 列跨度)
    _LAYOUT = (
        [("C",  C_FUNC, 1), ("<",  C_FUNC, 1), ("%",  C_FUNC, 1), ("/",  C_OP, 1)],
        [("7",  C_NUM,  1), ("8",  C_NUM,  1), ("9",  C_NUM,  1), ("*",  C_OP, 1)],
        [("4",  C_NUM,  1), ("5",  C_NUM,  1), ("6",  C_NUM,  1), ("-",  C_OP, 1)],
        [("1",  C_NUM,  1), ("2",  C_NUM,  1), ("3",  C_NUM,  1), ("+",  C_OP, 1)],
        [("0",  C_NUM,  2), (".",  C_NUM,  1), ("=",  C_EQ,  1)],
    )

    def _create_content(self):
        base_y = self.content_y  # 34

        # -- 显示栏 --
        disp = lv.obj(self.screen)
        disp.remove_style_all()
        disp.set_size(self._sw, self.DISP_H)
        disp.set_pos(0, base_y)
        disp.set_style_bg_color(lv.color_hex(0x16213E), 0)
        disp.set_style_bg_opa(lv.OPA.COVER, 0)
        disp.set_style_pad_all(4, 0)
        self._refs.append(disp)

        self._expr_label = lv.label(disp)
        self._expr_label.set_text("")
        self._expr_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._expr_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._expr_label.set_pos(4, 4)
        self._refs.append(self._expr_label)

        self._result_label = lv.label(disp)
        self._result_label.set_text("0")
        self._result_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._result_label.set_style_text_color(lv.color_hex(self.C_TXT), 0)
        self._result_label.set_pos(4, 26)
        self._refs.append(self._result_label)

        # -- 按钮网格 --
        grid_y = base_y + self.DISP_H
        for ri, row in enumerate(self._LAYOUT):
            ci = 0
            for text, color, span in row:
                bw = self.COL_W * span
                bh = self.ROW_H
                bx = ci * self.COL_W
                by = grid_y + ri * self.ROW_H

                btn = lv.btn(self.screen)
                btn.set_size(bw, bh)
                btn.set_pos(bx, by)
                btn.set_style_bg_color(lv.color_hex(color), 0)
                btn.set_style_bg_opa(lv.OPA.COVER, 0)
                btn.set_style_radius(2, 0)
                btn.set_style_shadow_width(0, 0)
                btn.set_style_border_width(0, 0)
                btn.set_style_pad_all(0, 0)

                lbl = lv.label(btn)
                lbl.set_text(text)
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(self.C_TXT), 0)
                lbl.center()

                btn.add_event_cb(
                    lambda e, t=text: self._on_btn(t),
                    lv.EVENT.CLICKED, None,
                )
                self._refs.extend((btn, lbl))
                ci += span

        # -- 计算器状态 --
        self._expr = ""
        self._result = "0"
        self._fresh = False  # 刚算完，下次输入覆盖

    # ---------- 按钮处理 ----------

    def _on_btn(self, key):
        if key == "C":
            self._expr = ""
            self._result = "0"
            self._fresh = False
        elif key == "<":
            if self._expr:
                self._expr = self._expr[:-1]
        elif key == "=":
            self._calc()
            return
        elif key == "%":
            self._percent()
        elif key in "+-*/":
            if self._fresh:
                self._expr = self._result
                self._fresh = False
            # 防止连续运算符
            if self._expr and self._expr[-1] in "+-*/":
                self._expr = self._expr[:-1]
            self._expr += key
        else:  # 数字 / 小数点
            if self._fresh:
                self._expr = ""
                self._fresh = False
            # 防止多个小数点
            if key == ".":
                parts = self._expr.replace("+", "#").replace("-", "#") \
                                   .replace("*", "#").replace("/", "#").split("#")
                if "." in parts[-1]:
                    return
            self._expr += key

        self._update_display()

    def _calc(self):
        if not self._expr:
            return
        try:
            val = eval(self._expr)
            # 整数不显示小数点
            if isinstance(val, float) and val == int(val):
                self._result = str(int(val))
            else:
                self._result = str(val)
        except Exception:
            self._result = "Error"
        self._expr_label.set_text(self._expr + " =")
        self._result_label.set_text(self._result)
        self._fresh = True

    def _percent(self):
        if not self._expr:
            return
        # 提取末尾数字并除以 100
        i = len(self._expr)
        while i > 0 and (self._expr[i - 1].isdigit() or self._expr[i - 1] == "."):
            i -= 1
        num_str = self._expr[i:]
        if num_str:
            try:
                val = float(num_str) / 100
                self._expr = self._expr[:i] + str(val)
            except ValueError:
                pass
        self._update_display()

    def _update_display(self):
        self._expr_label.set_text(self._expr)
        if not self._expr:
            self._result_label.set_text("0")
        elif not self._fresh:
            self._result_label.set_text("")


