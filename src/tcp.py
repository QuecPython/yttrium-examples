# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
import usocket
import ussl
from app_base import AppPage

class TcpPage(AppPage):
    """TCP Client 页面（带键盘输入）。"""
    KB_H = 128
    MAX_LOG = 6

    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        kb_y = self._sh - self.KB_H

        self._status_lbl = lv.label(self.screen)
        self._status_lbl.set_text("TCP: Disconnected")
        self._status_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)
        self._status_lbl.set_pos(6, base_y + 4)
        self._refs.append(self._status_lbl)

        log_y = base_y + 20
        log_h = kb_y - log_y - 32
        term = lv.obj(self.screen)
        term.remove_style_all()
        term.set_size(w, log_h)
        term.set_pos(0, log_y)
        term.set_style_bg_color(lv.color_hex(0x0D1117), 0)
        term.set_style_bg_opa(lv.OPA.COVER, 0)
        term.set_style_pad_all(0, 0)
        term.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(term)

        self._log_lines = []
        self._log_labels = []
        self._log_y = log_y + 2
        self._line_h = 16

        ta_y = log_y + log_h + 2
        ta_h = kb_y - ta_y
        self._ta = lv.textarea(self.screen)
        self._ta.set_size(w - 122, ta_h)
        self._ta.set_pos(6, ta_y)
        self._ta.set_style_bg_color(lv.color_hex(0x16213E), 0)
        self._ta.set_style_bg_opa(lv.OPA.COVER, 0)
        self._ta.set_style_radius(6, 0)
        self._ta.set_style_border_width(1, 0)
        self._ta.set_style_border_color(lv.color_hex(0x334466), 0)
        self._ta.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._ta.set_style_text_font(lv.font_montserrat_14, 0)
        self._ta.set_placeholder_text("> message ...")
        self._refs.append(self._ta)

        by = ta_y + 2
        self._mk_btn(w - 110, by, 48, "Send", 0x2E7D32, 0xFFFFFF, self._do_send)
        self._mk_btn(w - 56, by, 48, "Clear", 0x334466, 0xFFFFFF, self._do_clear)

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

        self._sock = None

    def _do_send(self):
        text = self._ta.get_text()
        if not text:
            return
        self._add_log("TX>", text, 0x2E7D32)
        try:
            if self._sock is None:
                import socket
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(5)
                self._add_log("---", "Connecting...", 0x888888)
                self._sock.connect(("192.168.1.1", 8080))
                self._add_log("---", "Connected", 0x4CAF50)
                self._status_lbl.set_text("TCP: Connected")
                self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
            self._sock.send(text.encode())
        except Exception as ex:
            self._add_log("ERR", str(ex), 0xFF5252)
            self._sock = None
            self._status_lbl.set_text("TCP: Disconnected")
            self._status_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)
        self._ta.set_text("")

    def _mk_btn(self, x, y, w, text, bg, fg, cb):
        btn = lv.btn(self.screen)
        btn.set_size(w, 24)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(3, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: cb(), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))

    def _do_clear(self):
        self._log_lines = []
        for l in self._log_labels:
            try: l.delete()
            except: pass
        self._log_labels = []

    def _add_log(self, tag, text, color):
        self._log_lines.append((tag, text, color))
        if len(self._log_lines) > self.MAX_LOG:
            self._log_lines.pop(0)
        self._render_log()

    def _render_log(self):
        for l in self._log_labels:
            try: l.delete()
            except: pass
        self._log_labels = []
        for i, (tag, text, color) in enumerate(self._log_lines):
            ry = self._log_y + i * self._line_h
            tl = lv.label(self.screen)
            tl.set_text(tag)
            tl.set_style_text_font(lv.font_montserrat_14, 0)
            tl.set_style_text_color(lv.color_hex(color), 0)
            tl.set_pos(4, ry)
            self._log_labels.append(tl)
            cl = lv.label(self.screen)
            cl.set_text(text[:36])
            cl.set_style_text_font(lv.font_montserrat_14, 0)
            cl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            cl.set_pos(54, ry)
            self._log_labels.append(cl)

    def _on_back(self, e=None):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        super()._on_back(e)


# =======================================================
#  页面注册表：标签 -> 页面类
# =======================================================

