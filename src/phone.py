# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage
try:
    import voiceCall
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False

class PhonePage(AppPage):
    """电话拨号 -- 拨号/来电/通话/挂断。"""

    ROW_H = 47                 # 6 行 × 47 = 282，落进内容高 286
    COL_W = 160                # 480 // 3，3 列满宽
    COL_W_LAST = 160           # 480 - 2*160

    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # ====== Row 0: 号码显示 + Del ======
        display_w = (w * 6) // 9  # 189
        del_w = w - display_w - (w // 9)  # 63

        self._num_label = lv.label(self.screen)
        self._num_label.set_text("")
        self._num_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._num_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._num_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self._num_label.set_size(display_w, self.ROW_H)
        self._num_label.set_pos(w // 9, base_y)
        self._refs.append(self._num_label)

        # 通话状态标签（覆盖号码区域）
        self._status_label = lv.label(self.screen)
        self._status_label.set_text("")
        self._status_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_label.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._status_label.set_pos(w // 9, base_y)
        self._refs.append(self._status_label)

        # Del 按钮
        del_btn = lv.btn(self.screen)
        del_btn.set_size(del_w, self.ROW_H)
        del_btn.set_pos(display_w + w // 9, base_y)
        del_btn.set_style_bg_color(lv.color_hex(0xFF6B6B), 0)
        del_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        del_btn.set_style_radius(2, 0)
        del_btn.set_style_shadow_width(0, 0)
        del_btn.set_style_border_width(0, 0)
        del_btn.add_event_cb(lambda e: self._on_del(), lv.EVENT.CLICKED, None)
        del_lbl = lv.label(del_btn)
        del_lbl.set_text("Del")
        del_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        del_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        del_lbl.center()
        self._refs.extend((del_btn, del_lbl))
        self._del_btn = del_btn

        # ====== Row 1-4: 数字键盘 ======
        digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        for i, d in enumerate(digits):
            ri = i // 3 + 1
            ci = i % 3
            bw = self.COL_W_LAST if ci == 2 else self.COL_W
            bx = ci * self.COL_W
            by = base_y + ri * self.ROW_H

            btn = lv.btn(self.screen)
            btn.set_size(bw, self.ROW_H)
            btn.set_pos(bx, by)
            btn.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
            btn.set_style_bg_opa(lv.OPA.COVER, 0)
            btn.set_style_radius(2, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(1, 0)
            btn.set_style_border_color(lv.color_hex(0xCCCCCC), 0)
            btn.set_style_pad_all(0, 0)
            btn.add_event_cb(
                lambda e, digit=d: self._on_digit(digit),
                lv.EVENT.CLICKED, None)
            lbl = lv.label(btn)
            lbl.set_text(d)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0x000000), 0)
            lbl.center()
            self._refs.extend((btn, lbl))

        # ====== Row 5: CALL / BACK ======
        row5_y = base_y + 5 * self.ROW_H

        self._call_btn = lv.btn(self.screen)
        self._call_btn.set_size(self.COL_W, self.ROW_H)
        self._call_btn.set_pos(self.COL_W, row5_y)
        self._call_btn.set_style_bg_color(lv.color_hex(0x4CAF50), 0)
        self._call_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        self._call_btn.set_style_radius(4, 0)
        self._call_btn.set_style_shadow_width(0, 0)
        self._call_btn.set_style_border_width(0, 0)
        self._call_btn.add_event_cb(lambda e: self._on_call(), lv.EVENT.CLICKED, None)
        self._call_lbl = lv.label(self._call_btn)
        self._call_lbl.set_text("CALL")
        self._call_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._call_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._call_lbl.center()
        self._refs.extend((self._call_btn, self._call_lbl))

        self._back_btn = lv.btn(self.screen)
        self._back_btn.set_size(self.COL_W_LAST, self.ROW_H)
        self._back_btn.set_pos(2 * self.COL_W, row5_y)
        self._back_btn.set_style_bg_color(lv.color_hex(0x9E9E9E), 0)
        self._back_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        self._back_btn.set_style_radius(4, 0)
        self._back_btn.set_style_shadow_width(0, 0)
        self._back_btn.set_style_border_width(0, 0)
        self._back_btn.add_event_cb(lambda e: self._on_back_btn(), lv.EVENT.CLICKED, None)
        self._back_lbl = lv.label(self._back_btn)
        self._back_lbl.set_text("Back")
        self._back_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._back_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._back_lbl.center()
        self._refs.extend((self._back_btn, self._back_lbl))

        # -- 状态 --
        self._phone_number = ""
        self._state = "IDLE"

        # -- 注册通话回调 --
        if HAS_VOICE:
            voiceCall.setCallback(self._call_callback)

    # ---------- 按钮处理 ----------

    def _on_digit(self, d):
        if self._state != "IDLE":
            return
        self._phone_number += d
        self._num_label.set_text(self._phone_number)

    def _on_del(self):
        if self._state != "IDLE":
            return
        if self._phone_number:
            self._phone_number = self._phone_number[:-1]
            self._num_label.set_text(self._phone_number)

    def _on_call(self):
        if self._state == "IDLE":
            if not self._phone_number:
                return
            print("[PHONE] call:", self._phone_number)
            if HAS_VOICE:
                voiceCall.callStart(self._phone_number)
            self._state = "CALLING"
            self._update_ui()
        elif self._state == "INCOMING":
            print("[PHONE] answer")
            if HAS_VOICE:
                voiceCall.callAnswer()
            self._state = "ACTIVE"
            self._update_ui()

    def _on_back_btn(self):
        if self._state in ("CALLING", "ACTIVE", "INCOMING"):
            print("[PHONE] hangup")
            if HAS_VOICE:
                voiceCall.callEnd()
            self._state = "IDLE"
            self._phone_number = ""
            self._update_ui()
        else:
            self._on_back()

    # ---------- 通话回调 ----------

    def _call_callback(self, args):
        call_info = args[0]
        try:
            number = args[6] if len(args) > 6 else ""
        except Exception:
            number = ""

        if call_info == 10:  # 来电
            self._phone_number = number
            self._state = "INCOMING"
            self._update_ui()
        elif call_info == 11:  # 接通
            self._state = "ACTIVE"
            self._update_ui()
        elif call_info == 12:  # 挂断
            self._state = "IDLE"
            self._phone_number = ""
            self._update_ui()

    # ---------- UI 更新 ----------

    def _update_ui(self):
        if self._state == "IDLE":
            self._status_label.set_text("")
            self._num_label.set_text(self._phone_number)
            self._call_lbl.set_text("CALL")
            self._call_btn.set_style_bg_color(lv.color_hex(0x4CAF50), 0)
            self._back_lbl.set_text("Back")
            self._back_btn.set_style_bg_color(lv.color_hex(0x9E9E9E), 0)
            self._del_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        elif self._state == "CALLING":
            self._status_label.set_text("Calling...")
            self._num_label.set_text(self._phone_number)
            self._call_btn.set_style_bg_opa(lv.OPA._50, 0)
            self._back_lbl.set_text("Hangup")
            self._back_btn.set_style_bg_color(lv.color_hex(0xFF5252), 0)
            self._del_btn.set_style_bg_opa(lv.OPA._50, 0)
        elif self._state == "ACTIVE":
            self._status_label.set_text("Connected")
            self._num_label.set_text(self._phone_number)
            self._call_btn.set_style_bg_opa(lv.OPA._50, 0)
            self._back_lbl.set_text("Hangup")
            self._back_btn.set_style_bg_color(lv.color_hex(0xFF5252), 0)
            self._del_btn.set_style_bg_opa(lv.OPA._50, 0)
        elif self._state == "INCOMING":
            self._status_label.set_text("Incoming:")
            self._num_label.set_text(self._phone_number)
            self._call_lbl.set_text("Answer")
            self._call_btn.set_style_bg_color(lv.color_hex(0x4CAF50), 0)
            self._call_btn.set_style_bg_opa(lv.OPA.COVER, 0)
            self._back_lbl.set_text("Reject")
            self._back_btn.set_style_bg_color(lv.color_hex(0xFF5252), 0)
            self._del_btn.set_style_bg_opa(lv.OPA._50, 0)


