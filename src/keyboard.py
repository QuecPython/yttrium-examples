# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class KeyboardPage(AppPage):
    """虚拟键盘参数配置（用 LVGL 内置 keyboard 控件）。"""

    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # 输入框
        # 输入框（直接放屏幕上，不要外框、不要 SSID 标签）
        # 高度顶到键盘顶部：base_y(34) → 键盘顶(_sh - 160)，消除中间空隙
        kb_h = 160
        self._ta = lv.textarea(self.screen)
        self._ta.set_text("Yttrium-Dev")
        # 不调 set_one_line(True)，原因：
        #   1) 它内部强制 set_height(字体高+上下pad)，会把高度压回一行，
        #      覆盖 set_size，输入框永远是矮的；
        #   2) 单行模式下 lv_textarea_add_char 直接丢弃 '\n'，键盘回车无法换行。
        # 保持默认多行模式：高度由 set_size 决定，回车可换行。
        self._ta.set_style_bg_color(lv.color_hex(0x16213E), 0)
        self._ta.set_style_bg_opa(lv.OPA.COVER, 0)
        self._ta.set_style_radius(6, 0)
        self._ta.set_style_border_width(1, 0)
        self._ta.set_style_border_color(lv.color_hex(0x334466), 0)
        self._ta.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._ta.set_style_text_font(lv.font_montserrat_14, 0)
        # 高度顶到键盘顶部：base_y(34) → 键盘顶(_sh - kb_h)，消除中间空隙。
        self._ta.set_size(w - 12, self._sh - kb_h - base_y)
        self._ta.set_pos(6, base_y)
        self._refs.append(self._ta)

        # LVGL 内置键盘：固定高度、贴屏底（手机键盘样式），按键接近正方形不被拉长
        kb = lv.keyboard(self.screen)
        kb.set_textarea(self._ta)                # 先联动（这一步会把键盘自动挪位）
        kb.set_size(w, kb_h)
        kb.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        kb.set_style_bg_opa(lv.OPA.COVER, 0)
        kb.set_style_bg_color(lv.color_hex(0x334466), lv.PART.ITEMS)
        kb.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.ITEMS)
        kb.set_style_min_height(0, lv.PART.ITEMS)   # 去掉按键最小高度，4 行才能完整塞进 200
        self._kb = kb
        self._refs.append(kb)
        try:
            self.screen.update_layout()
        except Exception:
            pass
        # set_pos 被键盘内部 align 覆盖（设 120 读到 240），改用底部对齐（align 优先级更高）
        kb.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)
        def _pin_kb(t):
            kb.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)
        self._kb_pin_timer = lv.timer_create(_pin_kb, 250, None)
        print("[KB] _sh=", self._sh, "kb_h=", kb.get_height(), "kb_y=", kb.get_y(),
              "ta_h=", self._ta.get_height(), "ta_y=", self._ta.get_y())


