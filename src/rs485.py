# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class Rs485Page(AppPage):
    """RS485 差分总线监控终端（带键盘输入）。"""
    KB_H = 128

    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        kb_y = self._sh - self.KB_H

        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(w, 17)
        bar.set_pos(0, base_y)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        self._refs.append(bar)

        for tx, t, col in ((6, "RS485:9600-8-N-1 A/B", 0x00BCD4),):
            lbl = lv.label(self.screen)
            lbl.set_text(t)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(col), 0)
            lbl.set_pos(tx, base_y + 1)
            self._refs.append(lbl)

        log_y = base_y + 17
        log_h = 100
        term = lv.obj(self.screen)
        term.remove_style_all()
        term.set_size(w, log_h)
        term.set_pos(0, log_y)
        term.set_style_bg_color(lv.color_hex(0x0D1117), 0)
        term.set_style_bg_opa(lv.OPA.COVER, 0)
        term.set_style_pad_all(0, 0)
        term.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(term)

        rows = (("TX>", "[01][03][00][00][00][01][84][0A]", 0x00BCD4),
                ("RX<", "[01][03][02][00][7F][F8][50]", 0x4CAF50),
                ("TX>", "[02][06][00][01][00][03][98][7B]", 0x00BCD4),
                ("RX<", "[02][06][00][01][00][03][98][7B]", 0x4CAF50),
                ("---", "Bus Idle", 0x888888),
                ("TX>", "[03][03][00][02][00][02][65][ED]", 0x00BCD4))
        line_h = 17
        for i, (tag, data, col) in enumerate(rows):
            ry = log_y + 3 + i * line_h
            for tx, txt, c in ((4, tag, col), (44, data, 0xCCCCCC)):
                lbl = lv.label(self.screen)
                lbl.set_text(txt)
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(c), 0)
                lbl.set_pos(tx, ry)
                self._refs.append(lbl)

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
        self._ta.set_placeholder_text("> Modbus RTU / RAW ...")
        self._refs.append(self._ta)

        by = ta_y + 2
        self._mk_cmd_btn(w - 122, by, 52, "Send", 0x00BCD4, 0x000000)
        self._mk_cmd_btn(w - 64, by, 52, "Clear", 0x334466, 0xFFFFFF)

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
        btn.add_event_cb(lambda e: print("[RS485] Send:", self._ta.get_text()), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))


# =======================================================
#  以太网二级界面 + 子页面
# =======================================================

