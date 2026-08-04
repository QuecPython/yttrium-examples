# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class UartPage(AppPage):
    """UART 串口终端（带键盘输入，真实收发）。"""
    KB_H = 128
    MAX_LOG = 6
    # UART 配置
    UART_PORT = 2          # UART2
    UART_BAUD = 115200
    UART_BITS = 8
    UART_PARITY = 0
    UART_STOP = 1
    UART_FLOW = 0          # 0=无流控

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

        cfg = "UART{}:{}".format(self.UART_PORT, self.UART_BAUD)
        self._status_lbl = lv.label(self.screen)
        self._status_lbl.set_text(cfg)
        self._status_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._status_lbl.set_pos(6, base_y + 1)
        self._refs.append(self._status_lbl)

        # 日志区
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

        self._log_lines = []
        self._log_labels = []
        self._log_y = log_y + 2
        self._line_h = 16

        # 输入区
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
        self._ta.set_placeholder_text("> send hex or text ...")
        self._refs.append(self._ta)

        by = ta_y + 2
        self._mk_send_btn(w - 122, by, 52, "Send", 0x00E676, 0x000000)
        self._mk_clear_btn(w - 64, by, 52, "Clear", 0x334466, 0xFFFFFF)

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

        # 初始化 UART
        self._uart = None
        try:
            from machine import UART
            self._uart = UART(self.UART_PORT, self.UART_BAUD,
                              self.UART_BITS, self.UART_PARITY,
                              self.UART_STOP, self.UART_FLOW)
            self._status_lbl.set_text("{}  Open".format(cfg))
            self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
        except Exception as ex:
            self._add_log("ERR", "UART init: {}".format(ex), 0xFF5252)
            self._status_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)

        # 启动 RX 轮询
        self._rx_active = True
        self._rx_timer = lv.timer_create(self._poll_rx, 200, None)

    # ---------- 轮询接收 ----------

    def _poll_rx(self, timer):
        if not self._rx_active or self._uart is None:
            return
        try:
            n = self._uart.any()
            if n > 0:
                data = self._uart.read(min(n, 128))
                if data:
                    hex_str = " ".join("{:02X}".format(b) for b in data)
                    self._add_log("RX<", hex_str, 0x4CAF50)
        except Exception:
            pass

    # ---------- Send ----------

    def _mk_send_btn(self, x, y, w, text, bg, fg):
        btn = lv.btn(self.screen)
        btn.set_size(w, 24)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(3, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: self._do_send(), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))

    def _do_send(self):
        if self._uart is None:
            self._add_log("ERR", "UART not open", 0xFF5252)
            return
        text = self._ta.get_text()
        if not text:
            return
        try:
            data = text.encode('utf-8')
            self._uart.write(data)
            hex_str = " ".join("{:02X}".format(b) for b in data)
            self._add_log("TX>", hex_str, 0x00E676)
        except Exception as ex:
            self._add_log("ERR", str(ex), 0xFF5252)
        self._ta.set_text("")

    # ---------- Clear ----------

    def _mk_clear_btn(self, x, y, w, text, bg, fg):
        btn = lv.btn(self.screen)
        btn.set_size(w, 24)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(3, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: self._do_clear(), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))

    def _do_clear(self):
        self._log_lines = []
        for lbl in self._log_labels:
            try:
                lbl.delete()
            except Exception:
                pass
        self._log_labels = []

    # ---------- 日志 ----------

    def _add_log(self, tag, text, color):
        self._log_lines.append((tag, text, color))
        if len(self._log_lines) > self.MAX_LOG:
            self._log_lines.pop(0)
        self._render_log()

    def _render_log(self):
        for lbl in self._log_labels:
            try:
                lbl.delete()
            except Exception:
                pass
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
            cl.set_text(text[:40])
            cl.set_style_text_font(lv.font_montserrat_14, 0)
            cl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            cl.set_pos(44, ry)
            self._log_labels.append(cl)

    def _on_back(self, e=None):
        self._rx_active = False
        utime.sleep_ms(300)
        super()._on_back(e)


