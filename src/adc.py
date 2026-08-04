# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from misc import ADC
import math
from app_base import AppPage

class AdcPage(AppPage):
    """ADC 电压仪表盘。"""
    def _create_content(self):
        import math
        base_y = self.content_y
        cx = self._sw // 2
        cy = base_y + 78
        R = 60

        # 三色弧段（半圆，开口朝下）
        for a0, a1, col in ((180, 240, 0x00E676), (240, 300, 0xFFEB3B), (300, 360, 0xFF5252)):
            a = lv.arc(self.screen)
            a.set_size(R * 2, R * 2)
            a.set_pos(cx - R, cy - R)
            a.set_bg_angles(a0, a1)
            a.set_range(0, 100)
            a.set_value(100)
            a.set_style_arc_color(lv.color_hex(0x16213E), lv.PART.MAIN)      # 背景弧
            a.set_style_arc_width(12, lv.PART.MAIN)
            a.set_style_arc_color(lv.color_hex(col), lv.PART.INDICATOR)      # 前景（进度）弧
            a.set_style_arc_width(12, lv.PART.INDICATOR)
            a.remove_style(None, lv.PART.KNOB)
            a.clear_flag(lv.obj.FLAG.CLICKABLE)
            self._refs.append(a)

        # 指针（lv.line，静态指向 ~1.85V）
        ang = math.radians(281)
        px = cx + (R - 16) * math.cos(ang)
        py = cy + (R - 16) * math.sin(ang)
        p0 = lv.point_t()
        p0.x = cx
        p0.y = cy
        p1 = lv.point_t()
        p1.x = int(px)
        p1.y = int(py)
        needle = lv.line(self.screen)
        needle.set_points([p0, p1], 2)
        needle.set_style_line_color(lv.color_hex(0x2C2C46), 0)
        needle.set_style_line_width(3, 0)
        needle.set_style_line_rounded(True, 0)
        self._refs.append(needle)
        self._needle = needle
        self._p0, self._p1 = p0, p1
        self._cx, self._cy, self._R = cx, cy, R

        # 圆心
        hub = lv.obj(self.screen)
        hub.remove_style_all()
        hub.set_size(8, 8)
        hub.set_pos(cx - 4, cy - 4)
        hub.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        hub.set_style_bg_opa(lv.OPA.COVER, 0)
        hub.set_style_radius(4, 0)
        hub.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(hub)

        # 数值
        self._adc_val = lv.label(self.screen)
        self._adc_val.set_text("1.85")
        self._adc_val.set_style_text_font(lv.font_montserrat_14, 0)
        self._adc_val.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._adc_val.set_pos(cx - 28, cy + 18)
        self._refs.append(self._adc_val)
        unit = lv.label(self.screen)
        unit.set_text("Volts")
        unit.set_style_text_font(lv.font_montserrat_14, 0)
        unit.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        unit.set_pos(cx - 24, cy + 44)
        self._refs.append(unit)

        # 刻度标签
        for tx, t in ((cx - R, "0V"), (cx - 14, "1.65V"), (cx + R - 18, "3.3V")):
            lbl = lv.label(self.screen)
            lbl.set_text(t)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            lbl.set_pos(tx, cy + R + 6)
            self._refs.append(lbl)

        # 通道信息
        info = lv.label(self.screen)
        info.set_text("ADC0  Raw: 1483 / 4095")
        info.set_style_text_font(lv.font_montserrat_14, 0)
        info.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        info.set_pos(cx - 80, base_y + 186)
        self._refs.append(info)
        self._adc_info = info

        # ===== 真实 ADC（lv.timer 在主线程采样，绝不开子线程碰 LVGL）=====
        self._adc = None
        self._adc_chan = 0
        try:
            from misc import ADC
            self._adc = ADC()
            self._adc_chan = ADC.ADC0
            self._adc.open()
            print("[ADC] open ADC0 ok")
        except Exception as e:
            print("[ADC] init failed:", e)
        self._adc_scale = 3.3 / 757.0    # 实测：3.3V 输入 -> raw≈757（板上 ~5.4:1 分压）。用精确 raw 再微调
        self._adc_active = True
        self._adc_timer = lv.timer_create(self._adc_tick, 300, None)
        self._adc_tick(None)            # 立即先读一次

    def _adc_tick(self, timer):
        """lv.timer 回调（主线程）：读 ADC0 -> 电压，更新指针角度 + 数值 + raw。"""
        if not self._adc_active or self._adc is None:
            return
        import math
        try:
            samples = [self._adc.read(self._adc_chan) for _ in range(6)]
        except Exception:
            return
        samples = [s for s in samples if s is not None]
        if not samples:
            return
        raw = sum(samples) // len(samples)   # 6 次采样平均，抑制抖动
        v = raw * self._adc_scale
        self._adc_val.set_text("{:.2f}".format(v))
        self._adc_info.set_text("ADC0  Raw: {} / 4095".format(raw))
        vv = 0.0 if v < 0 else (3.3 if v > 3.3 else v)
        ang = math.radians(180 + (vv / 3.3) * 180)   # 0V=180°, 3.3V=360°
        self._p1.x = int(self._cx + (self._R - 16) * math.cos(ang))
        self._p1.y = int(self._cy + (self._R - 16) * math.sin(ang))
        self._needle.set_points([self._p0, self._p1], 2)

    def _on_back(self, e=None):
        self._adc_active = False    # 停止采样（timer 还在但 no-op）
        super()._on_back(e)


