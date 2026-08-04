# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from machine import Pin
from app_base import AppPage

class BuzzerPage(AppPage):
    """蜂鸣器：Beep 短响 / On-Off 持续响。脚位确认后填 PIN_BUZZER 即可真响。"""
    PIN_BUZZER = Pin.GPIO2    # GPIO2 → Q0701 → BUZ0701

    def _create_content(self):
        base_y = self.content_y

        self._buz = None
        try:
            if self.PIN_BUZZER is not None:
                self._buz = Pin(self.PIN_BUZZER, Pin.OUT, Pin.PULL_DISABLE, 0)
        except Exception as e:
            print("[BUZZER] pin init failed:", e)

        # ---- 顶部信息卡 ----
        card = lv.obj(self.screen)
        card.remove_style_all()
        card.set_size(self._sw - 24, 96)
        card.set_pos(12, base_y + 6)
        card.set_style_bg_color(lv.color_hex(0x16213E), 0)
        card.set_style_bg_opa(lv.OPA.COVER, 0)
        card.set_style_radius(10, 0)
        card.set_style_pad_all(0, 0)
        card.set_style_border_width(0, 0)
        card.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(card)

        # 喇叭图标（圆 + 弧线近似）
        icon = lv.label(card)
        icon.set_text(")") if False else icon.set_text(">]")
        icon.set_style_text_font(lv.font_montserrat_14, 0)
        icon.set_style_text_color(lv.color_hex(0xFF9800), 0)
        icon.set_pos(16, 38)
        self._refs.append(icon)

        self._buz_title = lv.label(card)
        self._buz_title.set_text("Buzzer")
        self._buz_title.set_style_text_font(lv.font_montserrat_14, 0)
        self._buz_title.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._buz_title.set_pos(60, 20)
        self._refs.append(self._buz_title)

        self._buz_status = lv.label(card)
        self._buz_status.set_text("Ready" if self._buz else "Pin not configured")
        self._buz_status.set_style_text_font(lv.font_montserrat_14, 0)
        self._buz_status.set_style_text_color(
            lv.color_hex(0x00E676 if self._buz else 0xFF5252), 0)
        self._buz_status.set_pos(60, 56)
        self._refs.append(self._buz_status)

        # ---- 两个大按钮 ----
        bw, bh, gap = 200, 70, 16
        total = bw * 2 + gap
        ox = (self._sw - total) // 2
        by = base_y + 120

        # Beep
        b1 = lv.btn(self.screen)
        b1.set_size(bw, bh)
        b1.set_pos(ox, by)
        b1.set_style_bg_color(lv.color_hex(0x00E676), 0)
        b1.set_style_bg_opa(lv.OPA.COVER, 0)
        b1.set_style_radius(10, 0)
        b1.set_style_shadow_width(0, 0)
        b1.set_style_border_width(0, 0)
        l1 = lv.label(b1)
        l1.set_text("Beep")
        l1.set_style_text_font(lv.font_montserrat_14, 0)
        l1.set_style_text_color(lv.color_hex(0x000000), 0)
        l1.center()
        b1.add_event_cb(self._on_beep, lv.EVENT.CLICKED, None)

        # On / Off
        self._buz_state = False
        b2 = lv.btn(self.screen)
        b2.set_size(bw, bh)
        b2.set_pos(ox + bw + gap, by)
        b2.set_style_bg_color(lv.color_hex(0x334466), 0)
        b2.set_style_bg_opa(lv.OPA.COVER, 0)
        b2.set_style_radius(10, 0)
        b2.set_style_shadow_width(0, 0)
        b2.set_style_border_width(0, 0)
        self._buz_lbl = lv.label(b2)
        self._buz_lbl.set_text("Turn On")
        self._buz_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._buz_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._buz_lbl.center()
        b2.add_event_cb(self._on_toggle, lv.EVENT.CLICKED, None)

        self._refs.extend((card, b1, l1, b2, self._buz_lbl))

        # 底部提示
        hint = lv.label(self.screen)
        hint.set_text("Beep = short tone    On/Off = sustained")
        hint.set_style_text_font(lv.font_montserrat_14, 0)
        hint.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        hint.set_pos((self._sw - 230) // 2, by + bh + 10)
        self._refs.append(hint)

    def _set_status(self, text, col):
        self._buz_status.set_text(text)
        self._buz_status.set_style_text_color(lv.color_hex(col), 0)

    def _beep_on(self):
        if self._buz:
            try:
                self._buz.write(1)
            except Exception:
                pass

    def _beep_off(self):
        if self._buz:
            try:
                self._buz.write(0)
            except Exception:
                pass

    def _on_beep(self, e=None):
        """短响 150ms（主线程事件回调里做，不开子线程）。"""
        print("[BUZZER] beep")
        self._beep_on()
        self._set_status("Beeping...", 0xFF9800)
        utime.sleep_ms(150)
        self._beep_off()
        self._set_status("Ready" if not self._buz_state else "Sustained ON", 0x00E676)

    def _on_toggle(self, e=None):
        self._buz_state = not self._buz_state
        if self._buz_state:
            self._buz_lbl.set_text("Turn Off")
            self._beep_on()
            self._set_status("Sustained ON", 0xFF5252)
        else:
            self._buz_lbl.set_text("Turn On")
            self._beep_off()
            self._set_status("Ready", 0x00E676)

    def _on_back(self, e=None):
        self._beep_off()       # 离开页面确保不响
        super()._on_back(e)


