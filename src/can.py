# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class CanPage(AppPage):
    """CAN 总线监控终端（带键盘输入）。"""
    KB_H = 128

    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # 键盘贴屏幕底；textarea 填满键盘上方剩余空间（KeyboardPage 同款做法）
        kb_y = self._sh - self.KB_H

        # 状态条
        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(w, 17)
        bar.set_pos(0, base_y)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        self._refs.append(bar)

        for tx, t, col in ((6, "CAN:500kbps", 0x00E676),):
            lbl = lv.label(self.screen)
            lbl.set_text(t)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(col), 0)
            lbl.set_pos(tx, base_y + 1)
            self._refs.append(lbl)

        # 日志区（固定高度，留空间给 textarea + 键盘）
        log_y = base_y + 17
        log_h = 110
        term = lv.obj(self.screen)
        term.remove_style_all()
        term.set_size(w, log_h)
        term.set_pos(0, log_y)
        term.set_style_bg_color(lv.color_hex(0x0D1117), 0)
        term.set_style_bg_opa(lv.OPA.COVER, 0)
        term.set_style_pad_all(0, 0)
        term.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(term)

        rows = (("18FE", "8", "02 1A 4F 00 11 00 7E 90", 0x4CAF50),
                ("0CF0", "8", "7F 00 FF 33 00 00 00 8A", 0x4CAF50),
                ("18EA", "3", "00 00 18 FE 00 00 00 00", 0x4CAF50),
                ("18FE", "8", "EE 01 2B 00 00 00 00 C0", 0xFF9800),
                ("0C01", "8", "55 AA 01 02 03 04 05 06", 0x4CAF50))
        line_h = 17
        for i, (cid, dlc, data, col) in enumerate(rows):
            ry = log_y + 4 + i * line_h
            for tx, txt, c in ((6, cid, col), (54, "[" + dlc + "]", 0x888888), (92, data, 0xCCCCCC)):
                lbl = lv.label(self.screen)
                lbl.set_text(txt)
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(c), 0)
                lbl.set_pos(tx, ry)
                self._refs.append(lbl)

        # textarea 填满日志下方到键盘顶部的全部空间
        ta_y = log_y + log_h + 2
        ta_h = kb_y - ta_y
        self._ta = lv.textarea(self.screen)
        self._ta.set_size(w - 12, ta_h)
        self._ta.set_pos(6, ta_y)
        self._ta.set_style_bg_color(lv.color_hex(0x16213E), 0)
        self._ta.set_style_bg_opa(lv.OPA.COVER, 0)
        self._ta.set_style_radius(6, 0)
        self._ta.set_style_border_width(1, 0)
        self._ta.set_style_border_color(lv.color_hex(0x334466), 0)
        self._ta.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._ta.set_style_text_font(lv.font_montserrat_14, 0)
        self._ta.set_placeholder_text("> 0x18FE ...")
        self._refs.append(self._ta)

        # Send / Clear 浮动在 textarea 右上角
        by = ta_y + 2
        self._mk_cmd_btn(w - 122, by, 52, "Send", 0x00E676, 0x000000)
        self._mk_cmd_btn(w - 64, by, 52, "Clear", 0x334466, 0xFFFFFF)

        # LVGL 键盘：set_textarea 会自动把它放到 textarea 紧下方（= 屏幕底）
        kb = lv.keyboard(self.screen)
        kb.set_textarea(self._ta)
        kb.set_size(w, self.KB_H)
        kb.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        kb.set_style_bg_opa(lv.OPA.COVER, 0)
        kb.set_style_bg_color(lv.color_hex(0x334466), lv.PART.ITEMS)
        kb.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.ITEMS)
        kb.set_style_min_height(0, lv.PART.ITEMS)
        self._kb = kb
        self._refs.append(kb)
        try:
            self.screen.update_layout()
        except Exception:
            pass
        kb.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)
        def _pin_kb(t):
            kb.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)
        self._kb_pin_timer = lv.timer_create(_pin_kb, 250, None)

    def _mk_cmd_btn(self, x, y, w, text, bg, fg):
        btn = lv.btn(self.screen)
        btn.set_size(w, 24)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(3, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: print("[CAN] Send:", self._ta.get_text()), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))


