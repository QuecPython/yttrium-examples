# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class AtPage(AppPage):
    """AT 命令交互终端（带键盘输入，真实 AT 收发）。"""
    KB_H = 128
    MAX_LOG = 6

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

        self._status_lbl = lv.label(self.screen)
        self._status_lbl.set_text("Modem: Ready")
        self._status_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._status_lbl.set_pos(6, base_y + 1)
        self._refs.append(self._status_lbl)

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

        # 动态日志行（最多 MAX_LOG 条）
        self._log_lines = []       # [(tag, text, color), ...]
        self._log_labels = []      # lv.label references
        self._log_y = log_y + 2
        self._line_h = 16

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
        self._ta.set_placeholder_text("> AT+")
        self._refs.append(self._ta)

        by = ta_y + 2
        self._mk_send_btn(w - 122, by, 52, "Send", 0xFF9800, 0x000000)
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
        cmd = self._ta.get_text()
        if not cmd:
            return
        # 确保以 \r\n 结尾
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        self._add_log("TX>", cmd.strip(), 0x00E676)
        self._status_lbl.set_text("Modem: Sending...")
        self._status_lbl.set_style_text_color(lv.color_hex(0xFF9800), 0)

        try:
            import atcmd
            resp = bytearray(256)
            ret = atcmd.sendSync(cmd, resp, '', 10)
            if ret == 0:
                text = resp.decode('utf-8', 'ignore').strip()
                if text:
                    for line in text.split('\r\n'):
                        line = line.strip()
                        if line and line not in ('OK',):
                            self._add_log("RX<", line, 0x4CAF50)
                self._status_lbl.set_text("Modem: OK")
                self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
            else:
                self._add_log("ERR", "Send failed (ret={})".format(ret), 0xFF5252)
                self._status_lbl.set_text("Modem: Error")
                self._status_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)
        except Exception as ex:
            self._add_log("ERR", str(ex), 0xFF5252)
            self._status_lbl.set_text("Modem: Exception")
            self._status_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)

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
        """清空日志区域。"""
        self._log_lines = []
        for lbl in self._log_labels:
            try:
                lbl.delete()
            except Exception:
                pass
        self._log_labels = []

    # ---------- 日志显示 ----------

    def _add_log(self, tag, text, color):
        """追加一行日志到显示区，超出 MAX_LOG 则滚动。"""
        self._log_lines.append((tag, text, color))
        if len(self._log_lines) > self.MAX_LOG:
            self._log_lines.pop(0)
        self._render_log()

    def _render_log(self):
        """根据 _log_lines 重建日志标签。"""
        # 清除旧标签
        for lbl in self._log_labels:
            try:
                lbl.delete()
            except Exception:
                pass
        self._log_labels = []

        for i, (tag, text, color) in enumerate(self._log_lines):
            ry = self._log_y + i * self._line_h
            # tag
            tl = lv.label(self.screen)
            tl.set_text(tag)
            tl.set_style_text_font(lv.font_montserrat_14, 0)
            tl.set_style_text_color(lv.color_hex(color), 0)
            tl.set_pos(4, ry)
            self._log_labels.append(tl)
            # content
            cl = lv.label(self.screen)
            cl.set_text(text[:36])
            cl.set_style_text_font(lv.font_montserrat_14, 0)
            cl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            cl.set_pos(44, ry)
            self._log_labels.append(cl)


