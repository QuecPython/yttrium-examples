# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from misc import PWM
from app_base import AppPage

class LedPage(AppPage):
    """LED 滑块控制亮度。"""
    def _create_content(self):
        base_y = self.content_y
        cx = self._sw // 2

        # 灯泡光晕
        glow = lv.obj(self.screen)
        glow.remove_style_all()
        glow.set_size(92, 92)
        glow.set_pos(cx - 46, base_y + 24)
        glow.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        glow.set_style_bg_opa(lv.OPA.COVER, 0)
        glow.set_style_radius(46, 0)
        glow.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(glow)

        # 灯泡（绿色圆）
        bulb = lv.obj(self.screen)
        bulb.remove_style_all()
        bulb.set_size(52, 52)
        bulb.set_pos(cx - 26, base_y + 30)
        bulb.set_style_bg_color(lv.color_hex(0x00E676), 0)
        bulb.set_style_bg_opa(lv.OPA.COVER, 0)
        bulb.set_style_radius(26, 0)
        bulb.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(bulb)
        self._bulb = bulb

        # 亮度百分比
        self._led_pct = lv.label(self.screen)
        self._led_pct.set_text("75%")
        self._led_pct.set_style_text_font(lv.font_montserrat_14, 0)
        self._led_pct.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._led_pct.set_pos(cx - 24, base_y + 120)
        self._refs.append(self._led_pct)

        # 滑块
        self._slider = lv.slider(self.screen)
        self._slider.set_size(236, 8)
        self._slider.set_pos(cx - 118, base_y + 170)
        self._slider.set_value(75, lv.ANIM.OFF)
        self._slider.set_style_bg_color(lv.color_hex(0x16213E), 0)          # 轨道
        self._slider.set_style_bg_color(lv.color_hex(0x00E676), lv.PART.INDICATOR)  # 已填充段
        self._slider.set_style_bg_color(lv.color_hex(0x2C2C46), lv.PART.KNOB)      # 手柄
        self._slider.add_event_cb(self._on_slider, lv.EVENT.VALUE_CHANGED, None)
        self._refs.append(self._slider)

        # 状态行
        self._led_info = lv.label(self.screen)
        self._led_info.set_text("PWM  CH:11  Duty:75%")
        self._led_info.set_style_text_font(lv.font_montserrat_14, 0)
        self._led_info.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._led_info.set_pos(cx - 70, base_y + 186)
        self._refs.append(self._led_info)

        # ===== 真实 PWM（STATUS 灯 = pin25 / PWM11；实测可硬件调光）=====
        # cycleTime=1000us ≈ 1kHz。highTime = cycle * 占空比/100。
        self._pwm = None
        self._pwm_above = None
        self._pwm_cycle = 1000
        try:
            from misc import PWM
            self._pwm_above = PWM.ABOVE_1US
            self._pwm = PWM(PWM.PWM11, PWM.ABOVE_1US, 750, self._pwm_cycle)  # 默认 75%（对齐滑块）
            self._pwm.open()
            print("[LED] PWM11 open ok (STATUS LED)")
        except Exception as e:
            print("[LED] PWM init failed:", e)
        self._set_brightness(75)

    def _set_brightness(self, v):
        """v: 0~100。更新百分比/状态行 + 灯泡透明度(视觉) + 真实 PWM 占空比。"""
        if v < 0:
            v = 0
        if v > 100:
            v = 100
        self._led_pct.set_text("{}%".format(v))
        self._led_info.set_text("PWM  CH:11  Duty:{}%".format(v))
        try:
            self._bulb.set_style_bg_opa(int(255 * v / 100), 0)   # 屏幕灯泡随亮度
        except Exception:
            pass
        if self._pwm:
            try:
                high = int(self._pwm_cycle * v / 100)
                if high < 1:
                    high = 1            # ABOVE_1US 不接受 0
                self._pwm.open(self._pwm_above, high, self._pwm_cycle)
            except Exception as ex:
                print("[LED] pwm set:", ex)

    def _on_slider(self, e=None):
        self._set_brightness(self._slider.get_value())

    def _on_back(self, e=None):
        if self._pwm:
            try:
                self._pwm.close()
            except Exception:
                pass
        super()._on_back(e)


