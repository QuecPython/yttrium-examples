"""
Yttrium（EC718） 480x320 大屏主应用（完全自包含）
================================================
- LCD 驱动内联（来自 python_biglcd）：面板为 320x480 物理竖屏（ST7796），LVGL
  软件旋转（sw_rotate + 270 度）后得到 480x320 横屏逻辑分辨率。
- UI 由 test_ext_img.py 内联而来：AppPage 基类 + 15 个 App 页面 + PAGE_MAP
  + MainScreen 主桌面（状态栏 + 5x3 图标网格 + 导航）。
- 触摸使用 ft6x36（irq=40, reset=39, group=1）；若新板触摸 IC / 引脚不同，改 YttriumApp._init_touch。

部署：本文件 + icons/ 放到设备 U:/ 同目录，直接运行本文件（不再需要 python_lcd.py）。
"""

import utime
import _thread
import lvgl as lv
# import voiceCall
from machine import LCD, Pin
from tp import ft6x36 as Ft6x36


class AppPage:
    """应用页面基类。子类重写 _create_content() 实现各自功能。

    子类只需关心内容区域，标题栏和返回按钮由基类自动创建。
    """

    TITLE_BAR_H = 30

    def __init__(self, screen_w, screen_h, title, back_cb):
        """
        Args:
            screen_w: 屏幕宽度
            screen_h: 屏幕高度
            title: 页面标题（显示在标题栏）
            back_cb: 返回主界面的回调函数
        """
        self._sw = screen_w
        self._sh = screen_h
        self._back_cb = back_cb
        self._refs = []  # 防止 GC 回收

        # 创建页面
        self.screen = lv.obj()
        self.screen.remove_style_all()
        self.screen.set_size(screen_w, screen_h)
        self.screen.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        self.screen.set_style_bg_opa(lv.OPA.COVER, 0)
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen.clear_flag(lv.obj.FLAG.SCROLLABLE)   # 关掉滚动：避免键盘/输入框聚焦时屏幕滚动把内容挤出

        self._create_title_bar(title)
        self._create_content()

    def _create_title_bar(self, title):
        """创建顶部标题栏 + 返回按钮。"""
        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(self._sw, self.TITLE_BAR_H)
        bar.set_pos(0, 0)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)

        # 返回按钮
        back_btn = lv.btn(bar)
        back_btn.set_size(50, 24)
        back_btn.set_pos(4, 3)
        back_btn.set_style_bg_color(lv.color_hex(0x334466), 0)
        back_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        back_btn.set_style_radius(4, 0)
        back_btn.set_style_shadow_width(0, 0)
        back_btn.set_style_border_width(0, 0)

        back_lbl = lv.label(back_btn)
        back_lbl.set_text("< Back")
        back_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        back_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        back_lbl.center()

        # 页面标题
        title_lbl = lv.label(bar)
        title_lbl.set_text(title)
        title_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        title_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        title_lbl.set_pos(60, 7)

        back_btn.add_event_cb(
            self._on_back,
            lv.EVENT.CLICKED, None,
        )
        self._refs.extend((bar, back_btn, back_lbl, title_lbl))

    def _create_content(self):
        """创建页面内容。子类重写此方法。"""
        hint = lv.label(self.screen)
        hint.set_text("TODO")
        hint.set_style_text_font(lv.font_montserrat_14, 0)
        hint.set_style_text_color(lv.color_hex(0x555555), 0)
        hint.set_pos(self._sw // 2 - 20, self._sh // 2 - 7)
        self._refs.append(hint)

    def _on_back(self, e=None):
        """返回按钮回调。"""
        print("[PAGE] back")
        self._back_cb()

    @property
    def content_y(self):
        """内容区域起始 Y 坐标（标题栏下方）。"""
        return self.TITLE_BAR_H + 4

    @property
    def content_h(self):
        """内容区域可用高度。"""
        return self._sh - self.TITLE_BAR_H - 4


# =======================================================
#  各 App 页面（后续在此添加具体功能）
# =======================================================

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
        self._led_info.set_style_text_color(lv.color_hex(0x888888), 0)
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


class ClockPage(AppPage):
    """实时时钟 + 秒表。"""

    DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    def _create_content(self):
        base_y = self.content_y

        # ====== 左半区：时钟 ======

        # 时间 - 大字
        self._time_lbl = lv.label(self.screen)
        self._time_lbl.set_text("00:00:00")
        self._time_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._time_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
        self._time_lbl.set_pos(20, base_y + 20)
        self._refs.append(self._time_lbl)

        # 日期
        self._date_lbl = lv.label(self.screen)
        self._date_lbl.set_text("----/--/-- ---")
        self._date_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._date_lbl.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        self._date_lbl.set_pos(20, base_y + 50)
        self._refs.append(self._date_lbl)

        # 分隔线
        sep = lv.obj(self.screen)
        sep.remove_style_all()
        sep.set_size(1, self.content_h - 20)
        sep.set_pos(140, base_y + 10)
        sep.set_style_bg_color(lv.color_hex(0x334466), 0)
        sep.set_style_bg_opa(lv.OPA.COVER, 0)
        self._refs.append(sep)

        # ====== 右半区：秒表 ======

        rx = 160

        # 秒表标题
        sw_title = lv.label(self.screen)
        sw_title.set_text("Stopwatch")
        sw_title.set_style_text_font(lv.font_montserrat_14, 0)
        sw_title.set_style_text_color(lv.color_hex(0x888888), 0)
        sw_title.set_pos(rx, base_y + 5)
        self._refs.append(sw_title)

        # 秒表数值
        self._sw_lbl = lv.label(self.screen)
        self._sw_lbl.set_text("00:00.00")
        self._sw_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._sw_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._sw_lbl.set_pos(rx, base_y + 30)
        self._refs.append(self._sw_lbl)

        # 计次列表（最多显示 3 条）
        self._lap_labels = []
        for i in range(3):
            lbl = lv.label(self.screen)
            lbl.set_text("")
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0x666666), 0)
            lbl.set_pos(rx, base_y + 55 + i * 16)
            self._lap_labels.append(lbl)
            self._refs.append(lbl)

        # 按钮行
        btn_y = base_y + self.content_h - 42
        btn_w = 54
        btn_h = 30

        # Start / Stop
        self._btn_ss = lv.btn(self.screen)
        self._btn_ss.set_size(btn_w, btn_h)
        self._btn_ss.set_pos(rx, btn_y)
        self._btn_ss.set_style_bg_color(lv.color_hex(0x00E676), 0)
        self._btn_ss.set_style_bg_opa(lv.OPA.COVER, 0)
        self._btn_ss.set_style_radius(4, 0)
        self._btn_ss.set_style_shadow_width(0, 0)
        self._btn_ss.set_style_border_width(0, 0)
        self._btn_ss.add_event_cb(lambda e: self._sw_toggle(), lv.EVENT.CLICKED, None)
        self._btn_ss_lbl = lv.label(self._btn_ss)
        self._btn_ss_lbl.set_text("Start")
        self._btn_ss_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._btn_ss_lbl.set_style_text_color(lv.color_hex(0x000000), 0)
        self._btn_ss_lbl.center()

        # Lap / Reset
        self._btn_lr = lv.btn(self.screen)
        self._btn_lr.set_size(btn_w, btn_h)
        self._btn_lr.set_pos(rx + btn_w + 8, btn_y)
        self._btn_lr.set_style_bg_color(lv.color_hex(0x334466), 0)
        self._btn_lr.set_style_bg_opa(lv.OPA.COVER, 0)
        self._btn_lr.set_style_radius(4, 0)
        self._btn_lr.set_style_shadow_width(0, 0)
        self._btn_lr.set_style_border_width(0, 0)
        self._btn_lr.add_event_cb(lambda e: self._sw_lap_reset(), lv.EVENT.CLICKED, None)
        self._btn_lr_lbl = lv.label(self._btn_lr)
        self._btn_lr_lbl.set_text("Lap")
        self._btn_lr_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._btn_lr_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._btn_lr_lbl.center()

        self._refs.extend((sw_title, self._sw_lbl, self._btn_ss, self._btn_ss_lbl,
                           self._btn_lr, self._btn_lr_lbl, sep))

        # -- 秒表状态 --
        self._sw_running = False
        self._sw_start_ms = 0
        self._sw_elapsed = 0       # 累计毫秒
        self._sw_laps = []
        self._update_running = False

        # -- 启动更新线程 --
        self._update_running = True
        _thread.start_new_thread(self._update_loop, ())
        self._update_clock()

    # ---------- 时钟 ----------

    def _update_clock(self):
        t = utime.localtime()
        self._time_lbl.set_text("{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
        self._date_lbl.set_text("{:04d}/{:02d}/{:02d} {}".format(
            t[0], t[1], t[2], self.DAYS[t[6]]))

    # ---------- 秒表 ----------

    def _sw_toggle(self):
        if self._sw_running:
            # Stop
            self._sw_running = False
            self._sw_elapsed += utime.ticks_ms() - self._sw_start_ms
            self._btn_ss_lbl.set_text("Start")
            self._btn_ss.set_style_bg_color(lv.color_hex(0x00E676), 0)
            self._btn_lr_lbl.set_text("Reset")
        else:
            # Start
            self._sw_start_ms = utime.ticks_ms()
            self._sw_running = True
            self._btn_ss_lbl.set_text("Stop")
            self._btn_ss.set_style_bg_color(lv.color_hex(0xFF5252), 0)
            self._btn_lr_lbl.set_text("Lap")

    def _sw_lap_reset(self):
        if self._sw_running:
            # 记录计次
            total = self._sw_elapsed + (utime.ticks_ms() - self._sw_start_ms)
            self._sw_laps.append(total)
            if len(self._sw_laps) > 3:
                self._sw_laps = self._sw_laps[-3:]
            self._render_laps()
        else:
            # 重置
            self._sw_elapsed = 0
            self._sw_laps = []
            self._sw_lbl.set_text("00:00.00")
            for lbl in self._lap_labels:
                lbl.set_text("")
            self._btn_lr_lbl.set_text("Lap")

    def _render_sw(self):
        total = self._sw_elapsed
        if self._sw_running:
            total += utime.ticks_ms() - self._sw_start_ms
        self._sw_lbl.set_text(self._format_ms(total))

    def _render_laps(self):
        for i, lbl in enumerate(self._lap_labels):
            idx = len(self._sw_laps) - len(self._lap_labels) + i
            if 0 <= idx < len(self._sw_laps):
                lbl.set_text("Lap{}: {}".format(idx + 1,
                    self._format_ms(self._sw_laps[idx])))
            else:
                lbl.set_text("")

    @staticmethod
    def _format_ms(ms):
        cs = (ms // 10) % 100
        s = (ms // 1000) % 60
        m = (ms // 60000) % 60
        return "{:02d}:{:02d}.{:02d}".format(m, s, cs)

    # ---------- 更新线程 ----------

    def _update_loop(self):
        while self._update_running:
            utime.sleep_ms(200)
            try:
                self._update_clock()
                if self._sw_running:
                    self._render_sw()
            except Exception:
                pass

    # ---------- 退出清理 ----------

    def _on_back(self, e=None):
        self._update_running = False
        self._sw_running = False
        utime.sleep_ms(250)
        super()._on_back(e)


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
        unit.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        unit.set_pos(cx - 24, cy + 44)
        self._refs.append(unit)

        # 刻度标签
        for tx, t in ((cx - R, "0V"), (cx - 14, "1.65V"), (cx + R - 18, "3.3V")):
            lbl = lv.label(self.screen)
            lbl.set_text(t)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0x666666), 0)
            lbl.set_pos(tx, cy + R + 6)
            self._refs.append(lbl)

        # 通道信息
        info = lv.label(self.screen)
        info.set_text("ADC0  Raw: 1483 / 4095")
        info.set_style_text_font(lv.font_montserrat_14, 0)
        info.set_style_text_color(lv.color_hex(0x888888), 0)
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


class CalcPage(AppPage):
    """基础计算器 -- 四则运算，5x4 按钮网格。"""

    # -- 颜色 --
    C_NUM   = 0x334466
    C_OP    = 0x0F3460
    C_FUNC  = 0x2C3E50
    C_EQ    = 0x00E676
    C_TXT   = 0xFFFFFF

    # -- 布局（内容区 480x286）--
    DISP_H  = 48          # 显示栏高度
    COLS    = 4
    ROWS    = 5
    COL_W   = 120         # 480 // 4，满宽
    ROW_H   = 47          # (286 - 48) // 5

    # (文字, 颜色, 列跨度)
    _LAYOUT = (
        [("C",  C_FUNC, 1), ("<",  C_FUNC, 1), ("%",  C_FUNC, 1), ("/",  C_OP, 1)],
        [("7",  C_NUM,  1), ("8",  C_NUM,  1), ("9",  C_NUM,  1), ("*",  C_OP, 1)],
        [("4",  C_NUM,  1), ("5",  C_NUM,  1), ("6",  C_NUM,  1), ("-",  C_OP, 1)],
        [("1",  C_NUM,  1), ("2",  C_NUM,  1), ("3",  C_NUM,  1), ("+",  C_OP, 1)],
        [("0",  C_NUM,  2), (".",  C_NUM,  1), ("=",  C_EQ,  1)],
    )

    def _create_content(self):
        base_y = self.content_y  # 34

        # -- 显示栏 --
        disp = lv.obj(self.screen)
        disp.remove_style_all()
        disp.set_size(self._sw, self.DISP_H)
        disp.set_pos(0, base_y)
        disp.set_style_bg_color(lv.color_hex(0x16213E), 0)
        disp.set_style_bg_opa(lv.OPA.COVER, 0)
        disp.set_style_pad_all(4, 0)
        self._refs.append(disp)

        self._expr_label = lv.label(disp)
        self._expr_label.set_text("")
        self._expr_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._expr_label.set_style_text_color(lv.color_hex(0x888888), 0)
        self._expr_label.set_pos(4, 4)
        self._refs.append(self._expr_label)

        self._result_label = lv.label(disp)
        self._result_label.set_text("0")
        self._result_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._result_label.set_style_text_color(lv.color_hex(self.C_TXT), 0)
        self._result_label.set_pos(4, 26)
        self._refs.append(self._result_label)

        # -- 按钮网格 --
        grid_y = base_y + self.DISP_H
        for ri, row in enumerate(self._LAYOUT):
            ci = 0
            for text, color, span in row:
                bw = self.COL_W * span
                bh = self.ROW_H
                bx = ci * self.COL_W
                by = grid_y + ri * self.ROW_H

                btn = lv.btn(self.screen)
                btn.set_size(bw, bh)
                btn.set_pos(bx, by)
                btn.set_style_bg_color(lv.color_hex(color), 0)
                btn.set_style_bg_opa(lv.OPA.COVER, 0)
                btn.set_style_radius(2, 0)
                btn.set_style_shadow_width(0, 0)
                btn.set_style_border_width(0, 0)
                btn.set_style_pad_all(0, 0)

                lbl = lv.label(btn)
                lbl.set_text(text)
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(self.C_TXT), 0)
                lbl.center()

                btn.add_event_cb(
                    lambda e, t=text: self._on_btn(t),
                    lv.EVENT.CLICKED, None,
                )
                self._refs.extend((btn, lbl))
                ci += span

        # -- 计算器状态 --
        self._expr = ""
        self._result = "0"
        self._fresh = False  # 刚算完，下次输入覆盖

    # ---------- 按钮处理 ----------

    def _on_btn(self, key):
        if key == "C":
            self._expr = ""
            self._result = "0"
            self._fresh = False
        elif key == "<":
            if self._expr:
                self._expr = self._expr[:-1]
        elif key == "=":
            self._calc()
            return
        elif key == "%":
            self._percent()
        elif key in "+-*/":
            if self._fresh:
                self._expr = self._result
                self._fresh = False
            # 防止连续运算符
            if self._expr and self._expr[-1] in "+-*/":
                self._expr = self._expr[:-1]
            self._expr += key
        else:  # 数字 / 小数点
            if self._fresh:
                self._expr = ""
                self._fresh = False
            # 防止多个小数点
            if key == ".":
                parts = self._expr.replace("+", "#").replace("-", "#") \
                                   .replace("*", "#").replace("/", "#").split("#")
                if "." in parts[-1]:
                    return
            self._expr += key

        self._update_display()

    def _calc(self):
        if not self._expr:
            return
        try:
            val = eval(self._expr)
            # 整数不显示小数点
            if isinstance(val, float) and val == int(val):
                self._result = str(int(val))
            else:
                self._result = str(val)
        except Exception:
            self._result = "Error"
        self._expr_label.set_text(self._expr + " =")
        self._result_label.set_text(self._result)
        self._fresh = True

    def _percent(self):
        if not self._expr:
            return
        # 提取末尾数字并除以 100
        i = len(self._expr)
        while i > 0 and (self._expr[i - 1].isdigit() or self._expr[i - 1] == "."):
            i -= 1
        num_str = self._expr[i:]
        if num_str:
            try:
                val = float(num_str) / 100
                self._expr = self._expr[:i] + str(val)
            except ValueError:
                pass
        self._update_display()

    def _update_display(self):
        self._expr_label.set_text(self._expr)
        if not self._expr:
            self._result_label.set_text("0")
        elif not self._fresh:
            self._result_label.set_text("")


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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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


class CameraPage(AppPage):
    """摄像头实时预览。"""
    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        cx = w // 2

        # 取景框
        vf = lv.obj(self.screen)
        vf.remove_style_all()
        vf.set_size(w - 12, 150)
        vf.set_pos(6, base_y + 4)
        vf.set_style_bg_color(lv.color_hex(0x000000), 0)
        vf.set_style_bg_opa(lv.OPA.COVER, 0)
        vf.set_style_radius(6, 0)
        vf.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(vf)

        # 占位提示（真实画面需 Camera 固件）
        ph = lv.label(vf)
        ph.set_text("Camera\nPreview")
        ph.set_style_text_font(lv.font_montserrat_14, 0)
        ph.set_style_text_color(lv.color_hex(0x334466), 0)
        ph.center()
        self._refs.append(ph)

        # 十字准星
        ch = base_y + 4 + 75
        for ww, hh, xx, yy in ((24, 2, cx - 12, ch - 1), (2, 24, cx - 1, ch - 12)):
            seg = lv.obj(self.screen)
            seg.remove_style_all()
            seg.set_size(ww, hh)
            seg.set_pos(xx, yy)
            seg.set_style_bg_color(lv.color_hex(0x00E676), 0)
            seg.set_style_bg_opa(lv.OPA.COVER, 0)
            seg.clear_flag(lv.obj.FLAG.CLICKABLE)
            self._refs.append(seg)
        ring = lv.obj(self.screen)
        ring.remove_style_all()
        ring.set_size(36, 36)
        ring.set_pos(cx - 18, ch - 18)
        ring.set_style_bg_opa(lv.OPA.TRANSP, 0)
        ring.set_style_border_width(1, 0)
        ring.set_style_border_color(lv.color_hex(0x00E676), 0)
        ring.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(ring)

        # REC 指示 + 型号
        rec = lv.obj(self.screen)
        rec.remove_style_all()
        rec.set_size(6, 6)
        rec.set_pos(w - 34, base_y + 15)
        rec.set_style_bg_color(lv.color_hex(0xFF5252), 0)
        rec.set_style_bg_opa(lv.OPA.COVER, 0)
        rec.set_style_radius(3, 0)
        self._refs.append(rec)
        rec_lbl = lv.label(self.screen)
        rec_lbl.set_text("REC")
        rec_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        rec_lbl.set_style_text_color(lv.color_hex(0xFF5252), 0)
        rec_lbl.set_pos(w - 64, base_y + 11)
        self._refs.append(rec_lbl)
        model = lv.label(self.screen)
        model.set_text("GC0308")
        model.set_style_text_font(lv.font_montserrat_14, 0)
        model.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        model.set_pos(12, base_y + 11)
        self._refs.append(model)

        # 信息栏
        info_y = base_y + 158
        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(w, 48)
        bar.set_pos(0, info_y)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        self._refs.append(bar)
        for tx, cap, val, col in ((12, "Resolution", "240x240", 0xFFFFFF),
                                  (104, "FPS", "15", 0x00E676),
                                  (154, "Format", "RGB565", 0xFFFFFF)):
            c1 = lv.label(self.screen)
            c1.set_text(cap)
            c1.set_style_text_font(lv.font_montserrat_14, 0)
            c1.set_style_text_color(lv.color_hex(0x888888), 0)
            c1.set_pos(tx, info_y + 6)
            self._refs.append(c1)
            c2 = lv.label(self.screen)
            c2.set_text(val)
            c2.set_style_text_font(lv.font_montserrat_14, 0)
            c2.set_style_text_color(lv.color_hex(col), 0)
            c2.set_pos(tx, info_y + 22)
            self._refs.append(c2)

        # 快门键
        sh = lv.btn(self.screen)
        sh.set_size(30, 30)
        sh.set_pos(w - 60, info_y + 10)
        sh.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        sh.set_style_bg_opa(lv.OPA.COVER, 0)
        sh.set_style_radius(15, 0)
        sh.set_style_shadow_width(0, 0)
        sh.set_style_border_width(3, 0)
        sh.set_style_border_color(lv.color_hex(0x2C2C46), 0)
        sh.add_event_cb(lambda e: print("[CAM] capture (TODO)"), lv.EVENT.CLICKED, None)
        self._refs.append(sh)
        # TODO: 接入摄像头预览（需 Camera 固件）


class QrPage(AppPage):
    """Drink Shop -> Pay -> QR."""
    TAB_H = 28
    COLS = 4
    TAB_COFFEE = 0
    TAB_TEA = 1

    COFFEE = (
        ("U:/images/coconut.jpg", "Coconut", "$18"),
        ("U:/images/americano.jpg", "Americano", "$15"),
        ("U:/images/Mint.jpg", "Mint", "$20"),
        ("U:/images/hazelnut.jpg", "Hazelnut", "$22"),
    )
    TEA = (
        ("U:/images/bubble.jpg", "Bubble", "$14"),
        ("U:/images/pudding.jpg", "Pudding", "$16"),
        ("U:/images/Brown_sugar.jpg", "Brown Sugar", "$15"),
        ("U:/images/taro_bobo.jpg", "Taro Bobo", "$18"),
    )

    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        tab_y = base_y
        self._tab_coffee = self._mk_tab(0, tab_y, w // 2, self.TAB_H,
                                         "Coffee", 0x6F4E37, True)
        self._tab_tea    = self._mk_tab(w // 2, tab_y, w // 2, self.TAB_H,
                                         "Milk Tea", 0xC4956A, False)
        self._active_tab = self.TAB_COFFEE

        self._grid_base_y = tab_y + self.TAB_H + 4
        self._card_w = 108
        self._card_h = 118
        self._selected = set()
        self._product_refs = []

        btn_y = self._sh - self.TITLE_BAR_H - 4 - 34
        self._total_lbl = lv.label(self.screen)
        self._total_lbl.set_text("Total: $0")
        self._total_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._total_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._total_lbl.set_pos(6, btn_y + 6)
        self._refs.append(self._total_lbl)

        pay_btn = lv.btn(self.screen)
        pay_btn.set_size(120, 30)
        pay_btn.set_pos(w - 130, btn_y)
        pay_btn.set_style_bg_color(lv.color_hex(0x00E676), 0)
        pay_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        pay_btn.set_style_radius(6, 0)
        pay_btn.set_style_shadow_width(0, 0)
        pay_btn.set_style_border_width(0, 0)
        pay_btn.add_event_cb(lambda e: self._do_pay(), lv.EVENT.CLICKED, None)
        pay_lbl = lv.label(pay_btn)
        pay_lbl.set_text("Pay")
        pay_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        pay_lbl.set_style_text_color(lv.color_hex(0x000000), 0)
        pay_lbl.center()
        self._refs.extend((pay_btn, pay_lbl))

        self._show_products(self.COFFEE)

    def _mk_tab(self, x, y, w, h, text, color, active):
        btn = lv.btn(self.screen)
        btn.set_size(w, h)
        btn.set_pos(x, y)
        bg = color if active else 0x334466
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(4, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e, tab=text: self._on_tab(tab), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        lbl.center()
        self._refs.extend((btn, lbl))
        return btn

    def _on_tab(self, tab):
        if tab == "Coffee" and self._active_tab != self.TAB_COFFEE:
            self._active_tab = self.TAB_COFFEE
            self._tab_coffee.set_style_bg_color(lv.color_hex(0x6F4E37), 0)
            self._tab_tea.set_style_bg_color(lv.color_hex(0x334466), 0)
            self._pending_items = self.COFFEE
            lv.timer_create(lambda t: self._do_switch(), 50, None)
        elif tab == "Milk Tea" and self._active_tab != self.TAB_TEA:
            self._active_tab = self.TAB_TEA
            self._tab_tea.set_style_bg_color(lv.color_hex(0xC4956A), 0)
            self._tab_coffee.set_style_bg_color(lv.color_hex(0x334466), 0)
            self._pending_items = self.TEA
            lv.timer_create(lambda t: self._do_switch(), 50, None)

    def _do_switch(self):
        if hasattr(self, '_pending_items') and self._pending_items is not None:
            items = self._pending_items
            self._pending_items = None
            self._show_products(items)

    def _show_products(self, items):
        # 只删卡片本身（card.delete() 会递归删子控件）
        for refs in self._product_refs:
            if refs:
                try: refs[0].delete()
                except: pass
        self._product_refs = []
        self._selected = set()
        self._update_total()

        gap_x = (self._sw - self.COLS * self._card_w) // (self.COLS + 1)
        gap_y = 6
        for i, (img_path, name, price) in enumerate(items):
            col = i % self.COLS
            row = i // self.COLS
            cx = gap_x + col * (self._card_w + gap_x)
            cy = self._grid_base_y + row * (self._card_h + gap_y)
            refs = self._mk_card(cx, cy, self._card_w, self._card_h,
                                 img_path, name, price, i)
            self._product_refs.append(refs)

    def _mk_card(self, x, y, w, h, img_path, name, price, idx):
        refs = []
        card = lv.obj(self.screen)
        card.remove_style_all()
        card.set_size(w, h)
        card.set_pos(x, y)
        card.set_style_bg_color(lv.color_hex(0x16213E), 0)
        card.set_style_bg_opa(lv.OPA.COVER, 0)
        card.set_style_radius(6, 0)
        card.set_style_pad_all(0, 0)
        card.clear_flag(lv.obj.FLAG.SCROLLABLE)
        refs.append(card)

        # 图片区
        img_h = h - 44
        ic = lv.img(card)
        ic.set_src(img_path)
        ic.set_size(w - 8, img_h - 4)
        ic.set_pos(4, 4)
        ic.set_style_radius(4, 0)
        refs.append(ic)

        # 名称（图片下方）
        name_lbl = lv.label(card)
        name_lbl.set_text(name)
        name_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        name_lbl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
        name_lbl.set_pos(6, img_h + 6)
        refs.append(name_lbl)

        # 价格（左下）+ 勾选圆（右下）
        price_lbl = lv.label(card)
        price_lbl.set_text(price)
        price_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        price_lbl.set_style_text_color(lv.color_hex(0xFF9800), 0)
        price_lbl.set_pos(6, img_h + 24)
        refs.append(price_lbl)

        sel_btn = lv.btn(card)
        sel_btn.set_size(18, 18)
        sel_btn.set_pos(w - 22, img_h + 22)
        sel_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        sel_btn.set_style_shadow_width(0, 0)
        sel_btn.set_style_border_width(2, 0)
        sel_btn.set_style_border_color(lv.color_hex(0x888888), 0)
        sel_btn.set_style_radius(9, 0)
        sel_btn.set_style_pad_all(0, 0)
        sel_btn.add_event_cb(lambda e, i=idx: self._on_select(i, e.get_target()),
                             lv.EVENT.CLICKED, None)
        sel_lbl = lv.label(sel_btn)
        sel_lbl.set_text("")
        sel_lbl.center()
        refs.extend((sel_btn, sel_lbl))
        return refs

    def _on_select(self, idx, btn):
        if idx in self._selected:
            self._selected.discard(idx)
            btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            btn.set_style_border_color(lv.color_hex(0x888888), 0)
        else:
            self._selected.add(idx)
            btn.set_style_bg_color(lv.color_hex(0x00E676), 0)
            btn.set_style_bg_opa(lv.OPA.COVER, 0)
            btn.set_style_border_color(lv.color_hex(0x00E676), 0)
        self._update_total()

    def _update_total(self):
        items = self.COFFEE if self._active_tab == self.TAB_COFFEE else self.TEA
        total = 0
        for idx in self._selected:
            total += int(items[idx][2].replace("$", ""))
        self._total_lbl.set_text("Total: $" + str(total))

    def _do_pay(self):
        if not self._selected:
            return
        items = self.COFFEE if self._active_tab == self.TAB_COFFEE else self.TEA
        total = 0
        order = []
        for idx in self._selected:
            _, name, price_str = items[idx]
            total += int(price_str.replace("$", ""))
            order.append(name)

        pay_text = "YttriumPay\nTotal:${}\n{}".format(total, ",".join(order))

        # 保存当前 shop 页面引用，切到新 screen 释放内存
        self._shop_screen = self.screen
        pay_screen = lv.obj()
        pay_screen.remove_style_all()
        pay_screen.set_size(self._sw, self._sh)
        pay_screen.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        pay_screen.set_style_bg_opa(lv.OPA.COVER, 0)
        pay_screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        pay_screen.clear_flag(lv.obj.FLAG.SCROLLABLE)
        lv.scr_load(pay_screen)

        self._show_pay_screen(pay_screen, total, order, pay_text)

    def _show_pay_screen(self, screen, total, order, pay_text):
        w, h = self._sw, self._sh

        # 返回按钮（左上角）
        back_btn = lv.btn(screen)
        back_btn.set_size(60, 24)
        back_btn.set_pos(8, 6)
        back_btn.set_style_bg_color(lv.color_hex(0x334466), 0)
        back_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        back_btn.set_style_radius(4, 0)
        back_btn.set_style_shadow_width(0, 0)
        back_btn.set_style_border_width(0, 0)
        back_lbl = lv.label(back_btn)
        back_lbl.set_text("< Back")
        back_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        back_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        back_lbl.center()

        # 白底面板
        pw, ph = 240, 250
        panel = lv.obj(screen)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((w - pw) // 2, (h - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
        panel.set_style_bg_opa(lv.OPA.COVER, 0)
        panel.set_style_radius(12, 0)
        panel.set_style_pad_all(0, 0)

        title = lv.label(panel)
        title.set_text("Scan to Pay")
        title.set_style_text_font(lv.font_montserrat_14, 0)
        title.set_style_text_color(lv.color_hex(0x000000), 0)
        title.set_pos((pw - 100) // 2, 8)

        # QR 区
        qr_size = 120
        qr_x = (pw - qr_size) // 2
        qr_y = 28
        qr_bg = lv.obj(panel)
        qr_bg.remove_style_all()
        qr_bg.set_size(qr_size, qr_size)
        qr_bg.set_pos(qr_x, qr_y)
        qr_bg.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
        qr_bg.set_style_bg_opa(lv.OPA.COVER, 0)
        qr_bg.set_style_radius(4, 0)
        qr_bg.set_style_pad_all(0, 0)
        qr_bg.clear_flag(lv.obj.FLAG.CLICKABLE)

        # 真二维码（旧 QrPage 同款方块法，独立 screen 内存充足）
        n, matrix = self._pay_qr_matrix(pay_text, max_n=21)
        cell = qr_size // n
        off = (qr_size - cell * n) // 2
        for r in range(n):
            for c in range(n):
                if not matrix[r][c]:
                    continue
                box = lv.obj(qr_bg)
                box.remove_style_all()
                box.set_size(cell, cell)
                box.set_pos(off + c * cell, off + r * cell)
                box.set_style_bg_color(lv.color_hex(0x000000), 0)
                box.set_style_bg_opa(lv.OPA.COVER, 0)
                box.clear_flag(lv.obj.FLAG.CLICKABLE)

        # 总价 + 明细
        total_lbl = lv.label(panel)
        total_lbl.set_text("Total: ${}".format(total))
        total_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        total_lbl.set_style_text_color(lv.color_hex(0x000000), 0)
        total_lbl.set_pos(10, qr_y + qr_size + 8)

        detail = lv.label(panel)
        detail.set_text(", ".join(order[:4]))
        detail.set_style_text_font(lv.font_montserrat_14, 0)
        detail.set_style_text_color(lv.color_hex(0x888888), 0)
        detail.set_pos(10, qr_y + qr_size + 26)

        # 返回按钮事件
        back_btn.add_event_cb(lambda e: self._back_to_shop(screen), lv.EVENT.CLICKED, None)

    def _pay_qr_matrix(self, text, max_n=21):
        """生成二维码矩阵。有 qrcode 模块用真码，否则占位。"""
        try:
            import qrcode
            result = qrcode.getQRData(text, 1, 0xFFFF, 0x0000)
            if result != -1:
                side, data = result
                if side > 0:
                    if side > max_n:
                        ratio = side // max_n + 1
                        side = max_n
                    else:
                        ratio = 1
                    mat = [[False] * side for _ in range(side)]
                    for py in range(side):
                        for px in range(side):
                            sy = py * ratio
                            sx = px * ratio
                            si = (sy * (side * ratio) + sx) * 2
                            if si + 1 < len(data):
                                pixel = (data[si] << 8) | data[si + 1]
                                mat[py][px] = (pixel == 0)
                    return side, mat
        except Exception:
            pass
        n = max_n
        finder = [(0, 0), (0, n - 7), (n - 7, 0)]
        mat = [[False] * n for _ in range(n)]
        st = (hash(text) & 0xFFFFFFFF) or 12345
        for r in range(n):
            for c in range(n):
                st = (st * 1103515245 + 12345) & 0x7FFFFFFF
                on = (st / 0x7FFFFFFF) > 0.52
                for fr, fc in finder:
                    if fr <= r < fr + 7 and fc <= c < fc + 7:
                        on = (r == fr or r == fr + 6 or c == fc or
                              c == fc + 6 or
                              (fr + 2 <= r <= fr + 4 and fc + 2 <= c <= fc + 4))
                mat[r][c] = on
        return n, mat

    def _back_to_shop(self, pay_screen):
        lv.scr_load(self._shop_screen)
        # 恢复商品卡片
        items = self.COFFEE if self._active_tab == self.TAB_COFFEE else self.TEA
        self._show_products(items)

class AudioPage(AppPage):
    """录音与播放控制。"""
    def _create_content(self):
        import math
        base_y = self.content_y
        w = self._sw
        cx = w // 2

        # 文件名
        fn = lv.label(self.screen)
        fn.set_text("rec_001.wav")
        fn.set_style_text_font(lv.font_montserrat_14, 0)
        fn.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        fn.set_pos(cx - 45, base_y + 14)
        self._refs.append(fn)

        # 波形区
        wf = lv.obj(self.screen)
        wf.remove_style_all()
        wf.set_size(w - 16, 90)
        wf.set_pos(8, base_y + 34)
        wf.set_style_bg_color(lv.color_hex(0x0D1117), 0)
        wf.set_style_bg_opa(lv.OPA.COVER, 0)
        wf.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(wf)

        # 波形柱（已播放绿 / 未播放灰）
        bars = 56
        bw = (w - 16) / bars
        played = int(bars * 0.55)
        for i in range(bars):
            h = int(8 + 36 * abs(math.sin(i * 0.5)) * (0.5 + 0.5 * math.cos(i * 0.17)))
            col = 0x00E676 if i < played else 0x334466
            x = 8 + i * bw
            y0 = base_y + 34 + (90 - h) // 2
            bar = lv.obj(self.screen)
            bar.remove_style_all()
            bar.set_size(max(1, int(bw) - 1), h)
            bar.set_pos(int(x), int(y0))
            bar.set_style_bg_color(lv.color_hex(col), 0)
            bar.set_style_bg_opa(lv.OPA.COVER, 0)
            bar.clear_flag(lv.obj.FLAG.CLICKABLE)
            self._refs.append(bar)

        # 进度线
        px = 8 + int(played * bw)
        prog = lv.obj(self.screen)
        prog.remove_style_all()
        prog.set_size(2, 90)
        prog.set_pos(px, base_y + 34)
        prog.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        prog.set_style_bg_opa(lv.OPA.COVER, 0)
        prog.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(prog)

        # 时间
        for tx, t in ((10, "00:08"), (w - 40, "00:15")):
            tlbl = lv.label(self.screen)
            tlbl.set_text(t)
            tlbl.set_style_text_font(lv.font_montserrat_14, 0)
            tlbl.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
            tlbl.set_pos(tx, base_y + 128)
            self._refs.append(tlbl)

        # Rec / Play / Stop
        by = base_y + 158
        bw_btn = 76
        gap = (w - bw_btn * 3) // 4
        self._mk_audio_btn(gap, by, bw_btn, "Rec", 0xFF5252, 0xFFFFFF)
        self._mk_audio_btn(gap * 2 + bw_btn, by, bw_btn, "Play", 0x00E676, 0x000000)
        self._mk_audio_btn(gap * 3 + bw_btn * 2, by, bw_btn, "Stop", 0x334466, 0xFFFFFF)
        # TODO: 接入录音/播放（audio 模块）

    def _mk_audio_btn(self, x, y, w, text, bg, fg):
        btn = lv.btn(self.screen)
        btn.set_size(w, 34)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(4, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: print("[AUDIO]", text, "(TODO)"), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))


class UsbPage(AppPage):
    """USB U盘文件浏览器。"""
    FILES = (
        ("[DIR]", "music", 0x4CAF50, True),
        ("[DIR]", "photos", 0x4CAF50, True),
        ("WAV", "rec_001.wav", 0xFF9800, False),
        ("WAV", "voice_03.wav", 0xFF9800, False),
        ("TXT", "notes.txt", 0x2196F3, False),
        ("BIN", "firmware.bin", 0x9C27B0, False),
        ("PNG", "logo.png", 0x00BCD4, False),
        ("CSV", "log_0624.csv", 0x00E676, False),
    )

    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # 路径栏
        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(w, 22)
        bar.set_pos(0, base_y)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        self._refs.append(bar)

        p1 = lv.label(self.screen)
        p1.set_text("U:/")
        p1.set_style_text_font(lv.font_montserrat_14, 0)
        p1.set_style_text_color(lv.color_hex(0x00E676), 0)
        p1.set_pos(6, base_y + 3)
        self._refs.append(p1)
        p2 = lv.label(self.screen)
        p2.set_text("8.2 GB free / 14.9 GB")
        p2.set_style_text_font(lv.font_montserrat_14, 0)
        p2.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        p2.set_pos(92, base_y + 4)
        self._refs.append(p2)

        # 文件列表
        item_h = 18
        for i, (ext, name, col, is_dir) in enumerate(self.FILES):
            ry = base_y + 24 + i * item_h
            if i == 0:  # 选中高亮
                sel = lv.obj(self.screen)
                sel.remove_style_all()
                sel.set_size(w, item_h)
                sel.set_pos(0, ry - 1)
                sel.set_style_bg_color(lv.color_hex(0x334466), 0)
                sel.set_style_bg_opa(lv.OPA.COVER, 0)
                sel.clear_flag(lv.obj.FLAG.CLICKABLE)
                self._refs.append(sel)
            le = lv.label(self.screen)
            le.set_text(ext)
            le.set_style_text_font(lv.font_montserrat_14, 0)
            le.set_style_text_color(lv.color_hex(col), 0)
            le.set_pos(8, ry + 1)
            self._refs.append(le)
            ln = lv.label(self.screen)
            ln.set_text(name)
            ln.set_style_text_font(lv.font_montserrat_14, 0)
            ln.set_style_text_color(lv.color_hex(0x2C2C46), 0)
            ln.set_pos(50, ry + 1)
            self._refs.append(ln)
            if is_dir:
                la = lv.label(self.screen)
                la.set_text(">")
                la.set_style_text_font(lv.font_montserrat_14, 0)
                la.set_style_text_color(lv.color_hex(0x666666), 0)
                la.set_pos(w - 14, ry + 1)
                self._refs.append(la)

        # 翻页
        pg = lv.label(self.screen)
        pg.set_text("1 / 3")
        pg.set_style_text_font(lv.font_montserrat_14, 0)
        pg.set_style_text_color(lv.color_hex(0x555555), 0)
        pg.set_pos(w // 2 - 14, base_y + 206)
        self._refs.append(pg)
        # TODO: 读取 U:/ 真实文件列表


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
        self._num_label.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        del_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        self._call_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        self._back_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._back_lbl.center()
        self._refs.extend((self._back_btn, self._back_lbl))

        # -- 状态 --
        self._phone_number = ""
        self._state = "IDLE"

        # -- 注册通话回调 --
        # voiceCall.setCallback(self._call_callback)

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

    # def _on_call(self):
    #     if self._state == "IDLE":
    #         if not self._phone_number:
    #             return
    #         voiceCall.callStart(self._phone_number)
    #         self._state = "CALLING"
    #         self._update_ui()
    #     elif self._state == "INCOMING":
    #         voiceCall.callAnswer()
    #         self._state = "ACTIVE"
    #         self._update_ui()

    # def _on_back_btn(self):
    #     if self._state in ("CALLING", "ACTIVE", "INCOMING"):
    #         voiceCall.callEnd()
    #         self._state = "IDLE"
    #         self._update_ui()
    #     else:
    #         self._on_back()

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


class SnakePage(AppPage):
    """贪吃蛇游戏 -- 34x20 网格，触摸滑动操控。"""

    CELL = 14
    COLS = 34
    ROWS = 20
    OX = 2                     # 网格 X 偏移（34*14=476，居中于 480）
    OY = 3                     # 网格 Y 偏移（20*14=280，居中于 286）
    BASE_TICK = 150             # 初始帧间隔 ms

    COL_EMPTY = 0x16213E
    COL_HEAD  = 0x00E676
    COL_BODY  = 0x4CAF50
    COL_FOOD  = 0xFF5252

    def _create_content(self):
        # -- 游戏容器 --
        gc = lv.obj(self.screen)
        gc.remove_style_all()
        gc.set_size(self._sw, self.content_h)
        gc.set_pos(0, self.content_y)
        gc.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        gc.set_style_bg_opa(lv.OPA.COVER, 0)
        gc.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        gc.set_style_pad_all(0, 0)
        gc.clear_flag(lv.obj.FLAG.SCROLLABLE)
        gc.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(gc)
        self._gc = gc

        # -- 网格 --
        self._cells = []
        for r in range(self.ROWS):
            row = []
            for c in range(self.COLS):
                cell = lv.obj(gc)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(self.OX + c * self.CELL,
                             self.OY + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)  # 穿透触摸到 gc
                row.append(cell)
                self._refs.append(cell)
            self._cells.append(row)

        # -- 分数（标题栏右侧）--
        self._score_label = lv.label(self.screen)
        self._score_label.set_text("Score: 0")
        self._score_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_label.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._score_label.set_pos(self._sw - 80, 7)
        self._refs.append(self._score_label)

        # -- 提示遮罩 --
        pw, ph = 180, 60
        panel = lv.obj(gc)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((self._sw - pw) // 2,
                       (self.content_h - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0x000000), 0)
        panel.set_style_bg_opa(lv.OPA._60, 0)
        panel.set_style_radius(8, 0)
        panel.clear_flag(lv.obj.FLAG.CLICKABLE)   # 穿透触摸到 gc
        self._refs.append(panel)
        self._panel = panel

        self._overlay = lv.label(panel)
        self._overlay.set_text("Tap to Start")
        self._overlay.set_style_text_font(lv.font_montserrat_14, 0)
        self._overlay.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._overlay.center()
        self._refs.append(self._overlay)

        # -- 游戏状态 --
        self._state = "WAITING"
        self._snake = []
        self._direction = (1, 0)
        self._next_dir = (1, 0)
        self._food = None
        self._score = 0
        self._running = False
        self._touch_start = None
        # tick 用 lv.timer 驱动（回调在 task_handler/主线程里执行），不再开子线程碰 LVGL
        self._tick_timer = lv.timer_create(self._on_tick, self.BASE_TICK, None)

    # ---------- 游戏启动 ----------

    def _start_game(self):
        self._snake = [
            (self.COLS // 2, self.ROWS // 2),
            (self.COLS // 2 - 1, self.ROWS // 2),
            (self.COLS // 2 - 2, self.ROWS // 2),
        ]
        self._direction = (1, 0)
        self._next_dir = (1, 0)
        self._score = 0
        self._score_label.set_text("Score: 0")

        # 清空网格 -> 画初始蛇
        for r in range(self.ROWS):
            for c in range(self.COLS):
                self._cells[r][c].set_style_bg_color(
                    lv.color_hex(self.COL_EMPTY), 0)
        for i, (c, r) in enumerate(self._snake):
            col = self.COL_HEAD if i == 0 else self.COL_BODY
            self._cells[r][c].set_style_bg_color(lv.color_hex(col), 0)

        self._spawn_food()

        self._state = "PLAYING"
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")

        self._running = True
        # tick 由 lv.timer 驱动（主线程），不再开子线程
        if self._tick_timer:
            self._tick_timer.set_period(self._tick_period())

    # ---------- 食物 ----------

    def _spawn_food(self):
        import urandom
        snake_set = set(self._snake)
        empty = []
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if (c, r) not in snake_set:
                    empty.append((c, r))
        if not empty:
            self._end_game()
            return
        self._food = empty[urandom.getrandbits(10) % len(empty)]
        fc, fr = self._food
        self._cells[fr][fc].set_style_bg_color(
            lv.color_hex(self.COL_FOOD), 0)

    # ---------- 游戏循环 ----------

    def _tick_period(self):
        return max(80, self.BASE_TICK - self._score * 2)

    def _on_tick(self, timer):
        """lv.timer 回调（跑在主线程 task_handler 里）：推进一步；顺手按分数刷新周期。"""
        try:
            if self._state == "PLAYING":
                self._game_tick()
            timer.set_period(self._tick_period())
        except Exception as e:
            print("[SNAKE] tick error:", e)

    def _game_tick(self):
        self._direction = self._next_dir
        hx, hy = self._snake[0]
        nx = hx + self._direction[0]
        ny = hy + self._direction[1]

        # 碰墙
        if nx < 0 or nx >= self.COLS or ny < 0 or ny >= self.ROWS:
            self._end_game()
            return
        # 碰自身
        if (nx, ny) in self._snake:
            self._end_game()
            return

        self._snake.insert(0, (nx, ny))

        old_tail = None
        if (nx, ny) == self._food:
            self._score += 1
            self._score_label.set_text("Score: {}".format(self._score))
            self._spawn_food()
        else:
            old_tail = self._snake.pop()
            tc, tr = old_tail
            self._cells[tr][tc].set_style_bg_color(
                lv.color_hex(self.COL_EMPTY), 0)

        # 增量渲染
        self._cells[ny][nx].set_style_bg_color(
            lv.color_hex(self.COL_HEAD), 0)
        if len(self._snake) > 1:
            bx, by = self._snake[1]
            self._cells[by][bx].set_style_bg_color(
                lv.color_hex(self.COL_BODY), 0)

    # ---------- 游戏结束 ----------

    def _end_game(self):
        self._state = "GAME_OVER"
        self._running = False
        self._panel.set_style_bg_opa(lv.OPA._60, 0)
        self._overlay.set_text("Game Over!\nScore: {}\nTap to restart".format(
            self._score))
        self._overlay.center()

    # ---------- 触摸输入 ----------

    def _get_touch_pos(self):
        """通过活动 indev 获取当前触摸坐标。"""
        indev = lv.indev_get_act()
        if indev:
            pt = lv.point_t()
            indev.get_point(pt)
            return (pt.x, pt.y)
        return None

    def _on_touch(self, e):
        code = e.get_code()

        if code == lv.EVENT.PRESSED:
            pos = self._get_touch_pos()
            if pos:
                self._touch_start = pos
            return

        if code != lv.EVENT.RELEASED:
            return

        # 点击（短按）-> 开始 / 重新开始
        if self._state in ("WAITING", "GAME_OVER"):
            self._start_game()
            return

        # 滑动 -> 改变方向
        if self._state == "PLAYING" and self._touch_start:
            pos = self._get_touch_pos()
            if not pos:
                return
            dx = pos[0] - self._touch_start[0]
            dy = pos[1] - self._touch_start[1]
            if abs(dx) < 10 and abs(dy) < 10:
                return
            if abs(dx) > abs(dy):
                nd = (1, 0) if dx > 0 else (-1, 0)
            else:
                nd = (0, 1) if dy > 0 else (0, -1)
            cur = self._direction
            if (nd[0] + cur[0], nd[1] + cur[1]) != (0, 0):
                self._next_dir = nd

    # ---------- 退出清理 ----------

    def _on_back(self, e=None):
        print("[SNAKE] cleaning up...")
        self._running = False
        self._state = "GAME_OVER"
        utime.sleep_ms(self.BASE_TICK + 20)
        super()._on_back(e)


class Game2048Page(AppPage):
    """2048 游戏 -- 4x4 网格，滑动合并。"""

    SIZE = 4
    CELL = 48
    GAP = 4
    # [诊断] 设 False：方块只变色、不显示数字，用来排查"网格倾斜"是否跟数字渲染有关
    SHOW_NUMBERS = True
    # (背景色, 文字色)
    TILE_COLORS = {
        0:    (0x1A1A2E, 0x1A1A2E),
        2:    (0x334466, 0xFFFFFF),
        4:    (0x3D5A80, 0xFFFFFF),
        8:    (0xE07020, 0xFFFFFF),
        16:   (0xE85D20, 0xFFFFFF),
        32:   (0xE84420, 0xFFFFFF),
        64:   (0xE82C20, 0xFFFFFF),
        128:  (0xEDCF72, 0x1A1A2E),
        256:  (0xEDCC61, 0x1A1A2E),
        512:  (0xEDC850, 0x1A1A2E),
        1024: (0xEDC53F, 0x1A1A2E),
        2048: (0xEDC22E, 0x1A1A2E),
    }

    def _create_content(self):
        base_y = self.content_y
        grid_total = self.SIZE * self.CELL + (self.SIZE + 1) * self.GAP  # 212
        grid_x = (self._sw - grid_total) // 2
        grid_y = base_y + (self.content_h - grid_total) // 2

        # -- 分数栏 --
        self._score_lbl = lv.label(self.screen)
        self._score_lbl.set_text("Score: 0")
        self._score_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._score_lbl.set_pos(10, base_y + 4)
        self._refs.append(self._score_lbl)

        self._best_lbl = lv.label(self.screen)
        self._best_lbl.set_text("Best: 0")
        self._best_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._best_lbl.set_style_text_color(lv.color_hex(0x888888), 0)
        self._best_lbl.set_pos(self._sw - 75, base_y + 4)
        self._refs.append(self._best_lbl)

        # -- 网格背景 --
        bg = lv.obj(self.screen)
        bg.remove_style_all()
        bg.set_size(grid_total, grid_total)
        bg.set_pos(grid_x, grid_y)
        bg.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        bg.set_style_bg_opa(lv.OPA.COVER, 0)
        bg.set_style_radius(6, 0)
        bg.add_flag(lv.obj.FLAG.CLICKABLE)
        bg.clear_flag(lv.obj.FLAG.SCROLLABLE)
        bg.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(bg)

        # -- 4x4 格子 --
        self._cells = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._labels = [[None] * self.SIZE for _ in range(self.SIZE)]
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                x = grid_x + self.GAP + c * (self.CELL + self.GAP)
                y = grid_y + self.GAP + r * (self.CELL + self.GAP)

                cell = lv.obj(self.screen)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(x, y)
                cell.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(4, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)
                self._cells[r][c] = cell

                lbl = lv.label(cell)
                lbl.set_text("")
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
                lbl.center()
                self._labels[r][c] = lbl

                self._refs.extend((cell, lbl))

        # -- 遮罩 --
        pw, ph = 160, 50
        panel = lv.obj(bg)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((grid_total - pw) // 2, (grid_total - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0x000000), 0)
        panel.set_style_bg_opa(lv.OPA._60, 0)
        panel.set_style_radius(8, 0)
        panel.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(panel)
        self._panel = panel

        self._overlay = lv.label(panel)
        self._overlay.set_text("Tap to Start")
        self._overlay.set_style_text_font(lv.font_montserrat_14, 0)
        self._overlay.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._overlay.center()
        self._refs.append(self._overlay)

        # -- 状态 --
        self._grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self._score = 0
        self._best = 0
        self._state = "WAITING"
        self._touch_start = None

    # ---------- 游戏逻辑 ----------

    def _start_game(self):
        self._grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self._score = 0
        self._state = "PLAYING"
        self._spawn()
        self._spawn()
        self._render_all()
        self._update_score()
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")

    def _spawn(self):
        """随机空位生成 2(90%) 或 4(10%)。"""
        import urandom
        empty = [(r, c) for r in range(self.SIZE)
                 for c in range(self.SIZE) if self._grid[r][c] == 0]
        if not empty:
            return
        r, c = empty[urandom.getrandbits(8) % len(empty)]
        self._grid[r][c] = 2 if urandom.getrandbits(8) % 10 != 0 else 4

    def _slide_row_left(self, row):
        """左滑一行，返回 (新行, 得分)。"""
        # 去零压缩
        nums = [x for x in row if x != 0]
        # 合并
        merged = []
        score = 0
        skip = False
        for i in range(len(nums)):
            if skip:
                skip = False
                continue
            if i + 1 < len(nums) and nums[i] == nums[i + 1]:
                val = nums[i] * 2
                merged.append(val)
                score += val
                skip = True
            else:
                merged.append(nums[i])
        # 补零
        merged += [0] * (self.SIZE - len(merged))
        return merged, score

    def _move(self, direction):
        """执行移动。direction: 0=左 1=右 2=上 3=下。"""
        old = [row[:] for row in self._grid]
        total_score = 0

        if direction == 0:  # 左
            for r in range(self.SIZE):
                self._grid[r], s = self._slide_row_left(self._grid[r])
                total_score += s
        elif direction == 1:  # 右
            for r in range(self.SIZE):
                rev = self._grid[r][::-1]
                self._grid[r], s = self._slide_row_left(rev)
                self._grid[r] = self._grid[r][::-1]
                total_score += s
        elif direction == 2:  # 上
            for c in range(self.SIZE):
                col = [self._grid[r][c] for r in range(self.SIZE)]
                new_col, s = self._slide_row_left(col)
                total_score += s
                for r in range(self.SIZE):
                    self._grid[r][c] = new_col[r]
        elif direction == 3:  # 下
            for c in range(self.SIZE):
                col = [self._grid[r][c] for r in range(self.SIZE)][::-1]
                new_col, s = self._slide_row_left(col)
                new_col.reverse()
                total_score += s
                for r in range(self.SIZE):
                    self._grid[r][c] = new_col[r]

        # 是否有变化
        if self._grid == old:
            return

        self._score += total_score
        self._spawn()
        self._render_all()
        self._update_score()

        # 检查胜负
        if self._check_win():
            self._state = "WON"
            self._panel.set_style_bg_opa(lv.OPA._60, 0)
            self._overlay.set_text("You Win! 2048\nTap to continue")
            self._overlay.center()
        elif self._check_game_over():
            self._state = "GAME_OVER"
            self._panel.set_style_bg_opa(lv.OPA._60, 0)
            self._overlay.set_text(
                "Game Over!\nScore: {}\nTap to restart".format(self._score))
            self._overlay.center()

    def _check_win(self):
        return any(self._grid[r][c] == 2048
                   for r in range(self.SIZE) for c in range(self.SIZE))

    def _check_game_over(self):
        # 有空位就没结束
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self._grid[r][c] == 0:
                    return False
        # 有相邻相同就没结束
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                v = self._grid[r][c]
                if c + 1 < self.SIZE and self._grid[r][c + 1] == v:
                    return False
                if r + 1 < self.SIZE and self._grid[r + 1][c] == v:
                    return False
        return True

    # ---------- 渲染 ----------

    def _render_all(self):
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                v = self._grid[r][c]
                bg_col, txt_col = self.TILE_COLORS.get(
                    v, (0x00E676, 0x000000))
                self._cells[r][c].set_style_bg_color(lv.color_hex(bg_col), 0)
                if v and self.SHOW_NUMBERS:
                    self._labels[r][c].set_text(str(v))
                    self._labels[r][c].set_style_text_color(
                        lv.color_hex(txt_col), 0)
                else:
                    self._labels[r][c].set_text("")

    def _update_score(self):
        self._score_lbl.set_text("Score: {}".format(self._score))
        if self._score > self._best:
            self._best = self._score
        self._best_lbl.set_text("Best: {}".format(self._best))

    # ---------- 触摸输入 ----------

    def _get_touch_pos(self):
        indev = lv.indev_get_act()
        if indev:
            pt = lv.point_t()
            indev.get_point(pt)
            return (pt.x, pt.y)
        return None

    def _on_touch(self, e):
        code = e.get_code()

        if code == lv.EVENT.PRESSED:
            pos = self._get_touch_pos()
            if pos:
                self._touch_start = pos
            return

        if code != lv.EVENT.RELEASED:
            return

        # 点击 -> 开始 / 继续 / 重启
        if self._state == "WAITING":
            self._start_game()
            return
        if self._state == "WON":
            # 继续玩
            self._state = "PLAYING"
            self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
            self._overlay.set_text("")
            return
        if self._state == "GAME_OVER":
            self._start_game()
            return

        # 滑动 -> 移动
        if self._state == "PLAYING" and self._touch_start:
            pos = self._get_touch_pos()
            if not pos:
                return
            dx = pos[0] - self._touch_start[0]
            dy = pos[1] - self._touch_start[1]
            if abs(dx) < 15 and abs(dy) < 15:
                return
            if abs(dx) > abs(dy):
                self._move(0 if dx < 0 else 1)
            else:
                self._move(2 if dy < 0 else 3)


class TetrisPage(AppPage):
    """俄罗斯方块 -- 10x20 网格，触摸滑动操控。"""

    CELL = 14
    COLS = 10
    ROWS = 20
    GAME_X = 2          # 游戏区 X 偏移（容器内）
    GAME_Y = 3          # 游戏区 Y 偏移（容器内）
    BASE_TICK = 500
    COL_EMPTY = 0x16213E

    # 7 种方块: (矩阵, 颜色)
    SHAPES = (
        ([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], 0x00BCD4),  # I 青
        ([[1,1],[1,1]],                              0xFFEB3B),  # O 黄
        ([[0,1,0],[1,1,1],[0,0,0]],                  0x9C27B0),  # T 紫
        ([[0,1,1],[1,1,0],[0,0,0]],                  0x4CAF50),  # S 绿
        ([[1,1,0],[0,1,1],[0,0,0]],                  0xFF5252),  # Z 红
        ([[1,0,0],[1,1,1],[0,0,0]],                  0xFF9800),  # L 橙
        ([[0,0,1],[1,1,1],[0,0,0]],                  0x2196F3),  # J 蓝
    )

    # 消行计分: 0行=0, 1行=100, 2行=300, 3行=500, 4行=800
    LINE_SCORES = (0, 100, 300, 500, 800)

    def _create_content(self):
        base_y = self.content_y

        # -- 游戏区容器（板子 + 右侧信息栏 整体水平居中于内容区宽度）--
        board_w = self.COLS * self.CELL + 4
        board_h = self.ROWS * self.CELL + 6
        info_w = 4 * self.CELL + 24
        left = (self._sw - (board_w + 12 + info_w)) // 2
        if left < 2:
            left = 2

        gc = lv.obj(self.screen)
        gc.remove_style_all()
        gc.set_size(board_w, board_h)
        gc.set_pos(left, base_y)
        gc.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        gc.set_style_bg_opa(lv.OPA.COVER, 0)
        gc.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        gc.set_style_pad_all(0, 0)
        gc.clear_flag(lv.obj.FLAG.SCROLLABLE)
        gc.add_flag(lv.obj.FLAG.CLICKABLE)
        gc.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(gc)
        self._gc = gc

        # -- 游戏区网格 10x20 --
        self._cells = []
        for r in range(self.ROWS):
            row = []
            for c in range(self.COLS):
                cell = lv.obj(gc)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(self.GAME_X + c * self.CELL,
                             self.GAME_Y + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)
                row.append(cell)
                self._refs.append(cell)
            self._cells.append(row)

        # -- 信息栏（右侧）--
        info_x = left + board_w + 12

        # "Next" 标签
        lbl_next = lv.label(self.screen)
        lbl_next.set_text("Next:")
        lbl_next.set_style_text_font(lv.font_montserrat_14, 0)
        lbl_next.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        lbl_next.set_pos(info_x, base_y + 4)
        self._refs.append(lbl_next)

        # 预览区 4x4 网格
        pv_ox = info_x + 8
        pv_oy = base_y + 22
        self._pv_cells = []
        for r in range(4):
            for c in range(4):
                cell = lv.obj(self.screen)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(pv_ox + c * self.CELL, pv_oy + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                self._pv_cells.append(cell)
                self._refs.append(cell)

        # 分数 / 消行 / 等级（排在预览下方）
        info_y = pv_oy + 4 * self.CELL + 10
        self._score_lbl = lv.label(self.screen)
        self._score_lbl.set_text("Score: 0")
        self._score_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._score_lbl.set_pos(info_x, info_y)
        self._refs.append(self._score_lbl)

        self._lines_lbl = lv.label(self.screen)
        self._lines_lbl.set_text("Lines: 0")
        self._lines_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._lines_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._lines_lbl.set_pos(info_x, info_y + 20)
        self._refs.append(self._lines_lbl)

        self._level_lbl = lv.label(self.screen)
        self._level_lbl.set_text("Level: 1")
        self._level_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._level_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._level_lbl.set_pos(info_x, info_y + 40)
        self._refs.append(self._level_lbl)

        # -- 提示遮罩（铺满板子宽度，竖直居中）--
        pw, ph = board_w, 60
        panel = lv.obj(gc)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((board_w - pw) // 2, (board_h - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0x000000), 0)
        panel.set_style_bg_opa(lv.OPA._60, 0)
        panel.set_style_radius(8, 0)
        panel.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(panel)
        self._panel = panel

        self._overlay = lv.label(panel)
        self._overlay.set_text("Tap to Start")
        self._overlay.set_style_text_font(lv.font_montserrat_14, 0)
        self._overlay.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._overlay.center()
        self._refs.append(self._overlay)

        # -- 游戏状态 --
        self._state = "WAITING"
        self._board = [[0] * self.COLS for _ in range(self.ROWS)]
        self._piece = None
        self._next_idx = 0
        self._bag = []
        self._score = 0
        self._lines = 0
        self._level = 1
        self._running = False
        self._touch_start = None
        # tick 用 lv.timer 驱动（回调在 task_handler/主线程里执行），不再开子线程碰 LVGL
        self._tick_timer = lv.timer_create(self._on_tick, self.BASE_TICK, None)

    # ---------- 方块逻辑 ----------

    def _rot_matrix(self, mat):
        """顺时针旋转矩阵。"""
        rows = len(mat)
        cols = len(mat[0])
        return [[mat[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]

    def _get_shape(self, idx, rot):
        """获取第 idx 种方块旋转 rot 次后的矩阵和颜色。"""
        mat, color = self.SHAPES[idx]
        for _ in range(rot % 4):
            mat = self._rot_matrix(mat)
        return mat, color

    def _bag_next(self):
        """7-bag 随机发生器。"""
        import urandom
        if not self._bag:
            self._bag = list(range(7))
            # Fisher-Yates shuffle
            for i in range(6, 0, -1):
                j = urandom.getrandbits(8) % (i + 1)
                self._bag[i], self._bag[j] = self._bag[j], self._bag[i]
        return self._bag.pop()

    def _cell_coords(self, mat, px, py):
        """返回方块占用的 (col, row) 列表。"""
        coords = []
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    coords.append((px + c, py + r))
        return coords

    def _fits(self, mat, px, py):
        """检查方块在 (px, py) 是否合法。"""
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = px + c, py + r
                    if x < 0 or x >= self.COLS or y >= self.ROWS:
                        return False
                    if y >= 0 and self._board[y][x]:
                        return False
        return True

    # ---------- 游戏控制 ----------

    def _start_game(self):
        self._board = [[0] * self.COLS for _ in range(self.ROWS)]
        self._score = 0
        self._lines = 0
        self._level = 1
        self._bag = []
        self._render_board()

        self._next_idx = self._bag_next()
        self._spawn_piece()

        self._state = "PLAYING"
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")
        self._update_info()

        self._running = True
        # tick 由 lv.timer 驱动（主线程），不再开子线程
        if self._tick_timer:
            self._tick_timer.set_period(self._tick_period())

    def _spawn_piece(self):
        idx = self._next_idx
        self._next_idx = self._bag_next()
        mat, color = self._get_shape(idx, 0)
        px = (self.COLS - len(mat[0])) // 2
        py = 0
        # 如果顶部放不下，游戏结束
        if not self._fits(mat, px, py):
            self._end_game()
            return
        self._piece = {'idx': idx, 'rot': 0, 'x': px, 'y': py}
        self._render_piece()
        self._render_preview()

    def _move(self, dx, dy):
        if not self._piece or self._state != "PLAYING":
            return False
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        if self._fits(mat, p['x'] + dx, p['y'] + dy):
            self._clear_piece()
            p['x'] += dx
            p['y'] += dy
            self._render_piece()
            return True
        return False

    def _rotate_piece(self):
        if not self._piece or self._state != "PLAYING":
            return
        p = self._piece
        new_rot = (p['rot'] + 1) % 4
        mat, _ = self._get_shape(p['idx'], new_rot)
        # 尝试原位、左移1、右移1、上移1（wall kick）
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]:
            if self._fits(mat, p['x'] + dx, p['y'] + dy):
                self._clear_piece()
                p['rot'] = new_rot
                p['x'] += dx
                p['y'] += dy
                self._render_piece()
                return

    def _hard_drop(self):
        if not self._piece:
            return
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        dy = 0
        while self._fits(mat, p['x'], p['y'] + dy + 1):
            dy += 1
        self._clear_piece()
        p['y'] += dy
        self._render_piece()
        self._score += dy * 2  # 硬降加分
        self._lock()

    def _lock(self):
        """锁定当前方块到 board，检查消行。"""
        p = self._piece
        mat, color = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    bx, by = p['x'] + c, p['y'] + r
                    if 0 <= by < self.ROWS and 0 <= bx < self.COLS:
                        self._board[by][bx] = color

        self._piece = None
        cleared = self._clear_lines()
        if cleared:
            self._lines += cleared
            self._score += self.LINE_SCORES[min(cleared, 4)] * self._level
            self._level = self._lines // 10 + 1
            self._update_info()
            self._render_board()

        self._spawn_piece()

    def _clear_lines(self):
        """消除满行，返回消除行数。"""
        full = [r for r in range(self.ROWS)
                if all(self._board[r][c] for c in range(self.COLS))]
        if not full:
            return 0
        for r in sorted(full):
            del self._board[r]
            self._board.insert(0, [0] * self.COLS)
        return len(full)

    # ---------- 渲染 ----------

    def _render_board(self):
        for r in range(self.ROWS):
            for c in range(self.COLS):
                col = self._board[r][c] or self.COL_EMPTY
                self._cells[r][c].set_style_bg_color(lv.color_hex(col), 0)

    def _render_piece(self):
        if not self._piece:
            return
        p = self._piece
        mat, color = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = p['x'] + c, p['y'] + r
                    if 0 <= y < self.ROWS and 0 <= x < self.COLS:
                        self._cells[y][x].set_style_bg_color(
                            lv.color_hex(color), 0)

    def _clear_piece(self):
        if not self._piece:
            return
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = p['x'] + c, p['y'] + r
                    if 0 <= y < self.ROWS and 0 <= x < self.COLS:
                        col = self._board[y][x] or self.COL_EMPTY
                        self._cells[y][x].set_style_bg_color(
                            lv.color_hex(col), 0)

    def _render_preview(self):
        mat, color = self._get_shape(self._next_idx, 0)
        # 居中预览
        ox = (4 - len(mat[0])) // 2
        oy = (4 - len(mat)) // 2
        for r in range(4):
            for c in range(4):
                idx = r * 4 + c
                mr, mc = r - oy, c - ox
                if 0 <= mr < len(mat) and 0 <= mc < len(mat[0]) and mat[mr][mc]:
                    self._pv_cells[idx].set_style_bg_color(
                        lv.color_hex(color), 0)
                else:
                    self._pv_cells[idx].set_style_bg_color(
                        lv.color_hex(self.COL_EMPTY), 0)

    def _update_info(self):
        self._score_lbl.set_text("Score: {}".format(self._score))
        self._lines_lbl.set_text("Lines: {}".format(self._lines))
        self._level_lbl.set_text("Level: {}".format(self._level))

    # ---------- 游戏循环 ----------

    def _tick_period(self):
        return max(100, self.BASE_TICK - (self._level - 1) * 50)

    def _on_tick(self, timer):
        """lv.timer 回调（跑在主线程 task_handler 里）：每次下一格，碰底锁定；顺手按等级刷新周期。"""
        try:
            if self._state == "PLAYING" and self._piece:
                if not self._move(0, 1):
                    self._lock()
            timer.set_period(self._tick_period())
        except Exception as e:
            print("[TETRIS] tick error:", e)

    # ---------- 游戏结束 ----------

    def _end_game(self):
        self._state = "GAME_OVER"
        self._running = False
        self._panel.set_style_bg_opa(lv.OPA._60, 0)
        self._overlay.set_text("Game Over!\nScore: {}\nTap to restart".format(
            self._score))
        self._overlay.center()

    # ---------- 触摸输入 ----------

    def _get_touch_pos(self):
        indev = lv.indev_get_act()
        if indev:
            pt = lv.point_t()
            indev.get_point(pt)
            return (pt.x, pt.y)
        return None

    def _on_touch(self, e):
        code = e.get_code()

        if code == lv.EVENT.PRESSED:
            pos = self._get_touch_pos()
            if pos:
                self._touch_start = pos
            return

        if code == lv.EVENT.RELEASED:
            if self._state in ("WAITING", "GAME_OVER"):
                self._start_game()
                return

            if self._state == "PLAYING" and self._touch_start:
                pos = self._get_touch_pos()
                if not pos:
                    return
                dx = pos[0] - self._touch_start[0]
                dy = pos[1] - self._touch_start[1]
                if abs(dx) < 10 and abs(dy) < 10:
                    self._rotate_piece()  # 点击 -> 旋转
                    return
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self._move(1, 0)
                    else:
                        self._move(-1, 0)
                else:
                    if dy > 20:
                        self._hard_drop()  # 长下滑 -> 硬降
                    else:
                        self._move(0, 1)
            return

        if code == lv.EVENT.PRESSING and self._state == "PLAYING":
            # 长按下 -> 软降加速
            pos = self._get_touch_pos()
            if pos and self._touch_start:
                dy = pos[1] - self._touch_start[1]
                if dy > 30:
                    self._move(0, 1)

    # ---------- 退出清理 ----------

    def _on_back(self, e=None):
        print("[TETRIS] cleaning up...")
        self._running = False
        self._state = "GAME_OVER"
        utime.sleep_ms(self.BASE_TICK + 20)
        super()._on_back(e)


class ScanPage(AppPage):
    """条码/二维码扫描。"""
    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        cx = w // 2

        # 取景画面
        vf = lv.obj(self.screen)
        vf.remove_style_all()
        vf.set_size(w - 12, 198)
        vf.set_pos(6, base_y + 4)
        vf.set_style_bg_color(lv.color_hex(0x0D1117), 0)
        vf.set_style_bg_opa(lv.OPA.COVER, 0)
        vf.clear_flag(lv.obj.FLAG.SCROLLABLE)
        self._refs.append(vf)

        # 扫描框四角（L 形，细矩形拼）
        box = 150
        bx = (w - box) // 2
        by = base_y + 30
        ln = 18
        corners = (
            (bx, by, ln, 3), (bx, by, 3, ln),
            (bx + box - ln, by, ln, 3), (bx + box, by, 3, ln),
            (bx, by + box - 3, ln, 3), (bx, by + box - ln, 3, ln),
            (bx + box - ln, by + box - 3, ln, 3), (bx + box, by + box - ln, 3, ln),
        )
        for xx, yy, ww, hh in corners:
            seg = lv.obj(self.screen)
            seg.remove_style_all()
            seg.set_size(ww, hh)
            seg.set_pos(xx, yy)
            seg.set_style_bg_color(lv.color_hex(0x00E676), 0)
            seg.set_style_bg_opa(lv.OPA.COVER, 0)
            seg.clear_flag(lv.obj.FLAG.CLICKABLE)
            self._refs.append(seg)

        # 扫描线
        sl = lv.obj(self.screen)
        sl.remove_style_all()
        sl.set_size(box - 8, 2)
        sl.set_pos(bx + 4, by + box // 2)
        sl.set_style_bg_color(lv.color_hex(0x00E676), 0)
        sl.set_style_bg_opa(lv.OPA.COVER, 0)
        sl.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(sl)

        # 提示
        hint = lv.label(self.screen)
        hint.set_text("Align QR code within frame")
        hint.set_style_text_font(lv.font_montserrat_14, 0)
        hint.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
        hint.set_pos(cx - 80, by + box + 12)
        self._refs.append(hint)
        # TODO: 接入摄像头解码（需 Camera 固件）


# =======================================================
#  蜂鸣器 / 天气
# =======================================================

class BuzzerPage(AppPage):
    """蜂鸣器：Beep 短响 / On-Off 持续响。脚位确认后填 PIN_BUZZER 即可真响。"""
    PIN_BUZZER = None    # TODO: 确认 BEEP/LED 网络对应的模块引脚号后填，如 Pin.GPIOxx

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
        self._buz_title.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        self._buz_lbl.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._buz_lbl.center()
        b2.add_event_cb(self._on_toggle, lv.EVENT.CLICKED, None)

        self._refs.extend((card, b1, l1, b2, self._buz_lbl))

        # 底部提示
        hint = lv.label(self.screen)
        hint.set_text("Beep = short tone    On/Off = sustained")
        hint.set_style_text_font(lv.font_montserrat_14, 0)
        hint.set_style_text_color(lv.color_hex(0x666666), 0)
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


class WeatherPage(AppPage):
    """天气：展示卡片式界面。真实数据需联网 + HTTP API（下一步接），现为占位布局。"""
    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # ---- 主卡片：当前天气 ----
        card = lv.obj(self.screen)
        card.remove_style_all()
        card.set_size(w - 24, 150)
        card.set_pos(12, base_y + 4)
        card.set_style_bg_color(lv.color_hex(0x16213E), 0)
        card.set_style_bg_opa(lv.OPA.COVER, 0)
        card.set_style_radius(12, 0)
        card.set_style_pad_all(0, 0)
        card.set_style_border_width(0, 0)
        card.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(card)

        # 城市
        city = lv.label(card)
        city.set_text("Shanghai")
        city.set_style_text_font(lv.font_montserrat_14, 0)
        city.set_style_text_color(lv.color_hex(0xAAAAAA), 0)
        city.set_pos(20, 14)
        self._refs.append(city)

        # 大温度
        temp = lv.label(card)
        temp.set_text("--℃")
        temp.set_style_text_font(lv.font_montserrat_14, 0)
        temp.set_style_text_color(lv.color_hex(0x00E676), 0)
        temp.set_pos(20, 44)
        self._refs.append(temp)

        # 天气描述
        desc = lv.label(card)
        desc.set_text("--")
        desc.set_style_text_font(lv.font_montserrat_14, 0)
        desc.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        desc.set_pos(20, 110)
        self._refs.append(desc)

        # 右上角"图标"占位（云/太阳用文字近似）
        ic = lv.label(card)
        ic.set_text("~")
        ic.set_style_text_font(lv.font_montserrat_14, 0)
        ic.set_style_text_color(lv.color_hex(0xFFEB3B), 0)
        ic.set_pos(w - 24 - 40, 14)
        self._refs.append(ic)

        # ---- 三个小信息卡：湿度 / 风速 / 体感 ----
        info_y = base_y + 162
        info_h = 60
        gap = 8
        cw = (w - 24 - 2 * gap) // 3
        infos = (("Humidity", "-- %", 0x2196F3),
                 ("Wind",    "-- km/h", 0x9C27B0),
                 ("Feels",   "--℃", 0xFF9800))
        for i, (cap, val, col) in enumerate(infos):
            x = 12 + i * (cw + gap)
            c = lv.obj(self.screen)
            c.remove_style_all()
            c.set_size(cw, info_h)
            c.set_pos(x, info_y)
            c.set_style_bg_color(lv.color_hex(0x16213E), 0)
            c.set_style_bg_opa(lv.OPA.COVER, 0)
            c.set_style_radius(8, 0)
            c.set_style_pad_all(0, 0)
            c.set_style_border_width(0, 0)
            c.clear_flag(lv.obj.FLAG.CLICKABLE)
            cap_lbl = lv.label(c)
            cap_lbl.set_text(cap)
            cap_lbl.set_style_text_font(lv.font_montserrat_14, 0)
            cap_lbl.set_style_text_color(lv.color_hex(0x888888), 0)
            cap_lbl.set_pos(8, 6)
            val_lbl = lv.label(c)
            val_lbl.set_text(val)
            val_lbl.set_style_text_font(lv.font_montserrat_14, 0)
            val_lbl.set_style_text_color(lv.color_hex(col), 0)
            val_lbl.set_pos(8, 30)
            self._refs.extend((c, cap_lbl, val_lbl))

        # 底部提示
        hint = lv.label(self.screen)
        hint.set_text("Demo layout — live data needs network + HTTP API")
        hint.set_style_text_font(lv.font_montserrat_14, 0)
        hint.set_style_text_color(lv.color_hex(0x555555), 0)
        hint.set_pos((w - 260) // 2, info_y + info_h + 8)
        self._refs.append(hint)


# =======================================================
#  游戏二级界面（主桌面点 Game 进来，再选具体游戏）
# =======================================================

class GameHubPage(AppPage):
    """游戏二级界面：自带标题栏(返回主界面) + 3 个游戏图标。
    点具体游戏 -> 打开该游戏页，游戏页的返回 -> 回到本二级界面。"""
    GAMES = (
        ("U:/icons/demo-snake-game.png", "Snake"),
        ("U:/icons/demo-2048.png",       "2048"),
        ("U:/icons/demo-tetris.png",     "Tetris"),
    )

    def _create_content(self):
        self._sub_page = None
        n = len(self.GAMES)
        block_w = 120
        icon_size = 56
        ox = (self._sw - n * block_w) // 2          # 整体水平居中
        cy = self.content_y + (self.content_h - (icon_size + 24)) // 2

        for i, (icon_path, name) in enumerate(self.GAMES):
            bx = ox + i * block_w + (block_w - icon_size) // 2
            btn = lv.btn(self.screen)
            btn.set_size(icon_size, icon_size)
            btn.set_pos(bx, cy)
            btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_radius(8, 0)
            btn.set_style_pad_all(0, 0)
            btn.set_style_bg_opa(lv.OPA.COVER, lv.STATE.PRESSED)
            btn.set_style_bg_color(lv.color_hex(0x334466), lv.STATE.PRESSED)
            ic = lv.img(btn)
            ic.set_src(icon_path)
            ic.center()
            lbl = lv.label(self.screen)
            lbl.set_text(name)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            lbl.set_pos(bx + (icon_size - 44) // 2, cy + icon_size + 4)
            btn.add_event_cb(lambda e, nm=name: self._open_game(nm),
                             lv.EVENT.CLICKED, None)
            self._refs.extend((btn, ic, lbl))

    def _open_game(self, name):
        """打开具体游戏；游戏的返回 -> 回到本二级界面。"""
        print("[NAV] open game:", name)
        page_cls = PAGE_MAP.get(name)
        if page_cls is None:
            return
        self._sub_page = page_cls(self._sw, self._sh, name, self._back_to_hub)
        lv.scr_load(self._sub_page.screen)

    def _back_to_hub(self, e=None):
        lv.scr_load(self.screen)
        self._sub_page = None


# =======================================================
#  通信协议二级界面（主桌面点 Comm 进来，再选具体协议）
# =======================================================

class CommHubPage(AppPage):
    """通信协议二级界面：自带标题栏(返回主界面) + 4 个协议图标。
    点具体图标 -> 打开对应页面，子页的返回 -> 回到本二级界面。"""
    PROTOCOLS = (
        ("U:/icons/new-uart.png",  "UART"),
        ("U:/icons/new-can.png",   "CAN"),
        ("U:/icons/new-at.png",    "AT"),
        ("U:/icons/new-rs485.png", "RS485"),
    )

    def _create_content(self):
        self._sub_page = None
        n = len(self.PROTOCOLS)
        block_w = 96
        icon_size = 56
        ox = (self._sw - n * block_w) // 2
        cy = self.content_y + (self.content_h - (icon_size + 24)) // 2

        for i, (icon_path, name) in enumerate(self.PROTOCOLS):
            bx = ox + i * block_w + (block_w - icon_size) // 2
            btn = lv.btn(self.screen)
            btn.set_size(icon_size, icon_size)
            btn.set_pos(bx, cy)
            btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_radius(8, 0)
            btn.set_style_pad_all(0, 0)
            btn.set_style_bg_opa(lv.OPA.COVER, lv.STATE.PRESSED)
            btn.set_style_bg_color(lv.color_hex(0x334466), lv.STATE.PRESSED)
            ic = lv.img(btn)
            ic.set_src(icon_path)
            ic.center()
            lbl = lv.label(self.screen)
            lbl.set_text(name)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            lbl.set_pos(bx + (icon_size - 44) // 2, cy + icon_size + 4)
            btn.add_event_cb(lambda e, nm=name: self._open_proto(nm),
                             lv.EVENT.CLICKED, None)
            self._refs.extend((btn, ic, lbl))

    def _open_proto(self, name):
        """打开具体协议页面；返回 -> 回到本二级界面。"""
        print("[NAV] open proto:", name)
        page_cls = PAGE_MAP.get(name)
        if page_cls is None:
            return
        self._sub_page = page_cls(self._sw, self._sh, name, self._back_to_hub)
        lv.scr_load(self._sub_page.screen)

    def _back_to_hub(self, e=None):
        lv.scr_load(self.screen)
        self._sub_page = None


# =======================================================
#  各协议子页面（UART / AT / RS485）
# =======================================================

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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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
            cl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            cl.set_pos(44, ry)
            self._log_labels.append(cl)

    def _on_back(self, e=None):
        self._rx_active = False
        utime.sleep_ms(300)
        super()._on_back(e)


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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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
            cl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            cl.set_pos(44, ry)
            self._log_labels.append(cl)


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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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

class EthHubPage(AppPage):
    """以太网二级界面：3 个功能入口。"""
    ITEMS = (
        ("U:/icons/new-eth-info.png",  "IP"),
        ("U:/icons/new-eth-ping.png",  "PING"),
        ("U:/icons/new-eth-tcp.png",   "TCP"),
    )

    def _create_content(self):
        self._sub_page = None
        n = len(self.ITEMS)
        block_w = 120
        icon_size = 56
        ox = (self._sw - n * block_w) // 2
        cy = self.content_y + (self.content_h - (icon_size + 24)) // 2

        for i, (icon_path, name) in enumerate(self.ITEMS):
            bx = ox + i * block_w + (block_w - icon_size) // 2
            btn = lv.btn(self.screen)
            btn.set_size(icon_size, icon_size)
            btn.set_pos(bx, cy)
            btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_radius(8, 0)
            btn.set_style_pad_all(0, 0)
            btn.set_style_bg_opa(lv.OPA.COVER, lv.STATE.PRESSED)
            btn.set_style_bg_color(lv.color_hex(0x334466), lv.STATE.PRESSED)
            ic = lv.img(btn)
            ic.set_src(icon_path)
            ic.center()
            lbl = lv.label(self.screen)
            lbl.set_text(name)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            lbl.set_pos(bx + (icon_size - 44) // 2, cy + icon_size + 4)
            btn.add_event_cb(lambda e, nm=name: self._open(nm),
                             lv.EVENT.CLICKED, None)
            self._refs.extend((btn, ic, lbl))

    def _open(self, name):
        print("[NAV] open eth:", name)
        page_cls = PAGE_MAP.get(name)
        if page_cls is None:
            return
        self._sub_page = page_cls(self._sw, self._sh, name, self._back_to_hub)
        lv.scr_load(self._sub_page.screen)

    def _back_to_hub(self, e=None):
        lv.scr_load(self.screen)
        self._sub_page = None


class EthInfoPage(AppPage):
    """网络信息页面（真实以太网初始化）。"""
    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # 动态值标签（key 固定，value 可更新）
        self._info_keys = ("MAC", "IP", "Mask", "GW", "DNS1", "DNS2", "Status")
        self._info_vals = {}  # key → lv.label
        for i, key in enumerate(self._info_keys):
            ry = base_y + 4 + i * 26
            kl = lv.label(self.screen)
            kl.set_text(key)
            kl.set_style_text_font(lv.font_montserrat_14, 0)
            kl.set_style_text_color(lv.color_hex(0x888888), 0)
            kl.set_pos(16, ry)
            self._refs.append(kl)

            vl = lv.label(self.screen)
            vl.set_text("...")
            vl.set_style_text_font(lv.font_montserrat_14, 0)
            vl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            vl.set_pos(80, ry)
            self._refs.append(vl)
            self._info_vals[key] = vl

        # 按钮行
        btn_y = base_y + self.content_h - 36
        self._mk_btn(16, btn_y, 72, "Init",   0x1565C0, 0xFFFFFF, self._do_init)
        self._mk_btn(96, btn_y, 72, "Refresh", 0x0277BD, 0xFFFFFF, self._do_refresh)
        self._mk_btn(176, btn_y, 72, "DHCP",   0x00838F, 0xFFFFFF, self._do_dhcp)

        # 初始化以太网
        self._nic = None
        self._do_init()

    # -- 以太网操作 --

    def _do_init(self):
        """初始化 W5500 网卡。"""
        try:
            import ethernet
            mac = b'\x00\x11\x22\x33\x44\x55'
            # 使用默认引脚配置（-1 沿用上次/默认值）
            self._nic = ethernet.W5500(mac, '', '', '', -1, -1, -1, -1, 0)
            self._set_val("Status", "Init OK")
            self._do_refresh()
        except ImportError:
            self._set_val("Status", "No ethernet module")
        except Exception as ex:
            self._set_val("Status", "Init err: {}".format(ex))

    def _do_refresh(self):
        """读取 ipconfig 并更新显示。"""
        if self._nic is None:
            return
        try:
            info = self._nic.ipconfig()
            if info and len(info) >= 2:
                # info[0] = (mac, hostname)
                # info[1] = (iptype, ip, subnet, gateway, dns1, dns2)
                mac_host = info[0]
                net = info[1]
                self._set_val("MAC", mac_host[0])
                self._set_val("IP", net[1] if net[1] else "(none)")
                self._set_val("Mask", net[2] if net[2] else "(none)")
                self._set_val("GW", net[3] if net[3] else "(none)")
                self._set_val("DNS1", net[4] if net[4] else "(none)")
                self._set_val("DNS2", net[5] if net[5] else "(none)")
                self._set_val("Status", "OK  " + mac_host[1])
        except Exception as ex:
            self._set_val("Status", "Read err: {}".format(ex))

    def _do_dhcp(self):
        """DHCP 获取 IP。"""
        if self._nic is None:
            return
        try:
            self._set_val("Status", "DHCP...")
            ret = self._nic.dhcp()
            if ret == 0:
                self._set_val("Status", "DHCP OK")
                self._nic.set_up()
                self._do_refresh()
            else:
                self._set_val("Status", "DHCP fail ({})".format(ret))
        except Exception as ex:
            self._set_val("Status", "DHCP err: {}".format(ex))

    # -- UI 辅助 --

    def _set_val(self, key, text):
        lbl = self._info_vals.get(key)
        if lbl:
            lbl.set_text(str(text))

    def _mk_btn(self, x, y, w, text, bg, fg, cb):
        btn = lv.btn(self.screen)
        btn.set_size(w, 28)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(4, 0)
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


class PingPage(AppPage):
    """Ping 网络诊断页面（带键盘输入）。"""
    KB_H = 128
    MAX_LOG = 6

    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        kb_y = self._sh - self.KB_H

        self._status_lbl = lv.label(self.screen)
        self._status_lbl.set_text("Ping")
        self._status_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_lbl.set_style_text_color(lv.color_hex(0x00E676), 0)
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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._ta.set_style_text_font(lv.font_montserrat_14, 0)
        self._ta.set_placeholder_text("> IP or domain ...")
        self._ta.set_text("8.8.8.8")
        self._refs.append(self._ta)

        by = ta_y + 2
        self._mk_btn(w - 110, by, 48, "Ping", 0x00838F, 0xFFFFFF, self._do_ping)
        self._mk_btn(w - 56, by, 48, "Clear", 0x334466, 0xFFFFFF, self._do_clear)

        kb = lv.keyboard(self.screen)
        kb.set_textarea(self._ta)
        kb.set_size(w, self.KB_H)
        kb.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        kb.set_style_bg_opa(lv.OPA.COVER, 0)
        kb.set_style_bg_color(lv.color_hex(0x334466), lv.PART.ITEMS)
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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

    def _do_ping(self):
        target = self._ta.get_text().strip()
        if not target:
            return
        self._add_log("PING", target, 0x00BCD4)
        self._status_lbl.set_text("Pinging...")
        try:
            import uping
            # uping.ping(target, count=4) 返回 (sent, received, times)
            result = uping.ping(target, 4, 1000)
            if result:
                sent, recv, times = result
                self._add_log("DONE", "{}/{} received, {}ms".format(recv, sent, times[0] if times else "?"), 0x4CAF50)
                self._status_lbl.set_text("{}: {}/{} ok".format(target, recv, sent))
            else:
                self._add_log("FAIL", "no response", 0xFF5252)
                self._status_lbl.set_text("{}: timeout".format(target))
        except ImportError:
            self._add_log("ERR", "uping module not available", 0xFF5252)
            self._status_lbl.set_text("uping N/A")
        except Exception as ex:
            self._add_log("ERR", str(ex), 0xFF5252)
            self._status_lbl.set_text("Error")

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
            cl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
            cl.set_pos(54, ry)
            self._log_labels.append(cl)


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
        self._ta.set_style_text_color(lv.color_hex(0x2C2C46), 0)
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
        kb.set_style_text_color(lv.color_hex(0x2C2C46), lv.PART.ITEMS)
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
            cl.set_style_text_color(lv.color_hex(0xCCCCCC), 0)
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

PAGE_MAP = {
    "LED":    LedPage,
    "Game":   GameHubPage,
    "Clock":  ClockPage,
    "Weather": WeatherPage,
    "Buzzer": BuzzerPage,
    "ADC":    AdcPage,
    "Calc":   CalcPage,
    "Comm":   CommHubPage,
    "UART":   UartPage,
    "CAN":    CanPage,
    "AT":     AtPage,
    "RS485":  Rs485Page,
    "ETH":    EthHubPage,
    "IP":     EthInfoPage,
    "PING":   PingPage,
    "TCP":    TcpPage,
    "Key":    KeyboardPage,
    "Camera": CameraPage,
    "QR":     QrPage,
    "Audio":  AudioPage,
    "USB":    UsbPage,
    "Phone":  PhonePage,
    "Snake":  SnakePage,
    "2048":   Game2048Page,
    "Tetris": TetrisPage,
    "Scan":   ScanPage,
}


# =======================================================
#  主屏幕：状态栏 + 5x3 图标网格
# =======================================================

class MainScreen:
    """5列x3行应用图标主桌面，含顶部状态栏。"""

    STATUS_BAR_H = 22
    COLS = 5
    ROWS = 3
    CELL_W = 56
    CELL_H = 70
    BTN_PAD = 4

    APP_GRID = (
        ("U:/icons/demo-led-slider.png",       "LED"),
        ("U:/icons/demo-clock.png",            "Clock"),
        ("U:/icons/demo-adc-gauge.png",        "ADC"),
        ("U:/icons/demo-calculator.png",       "Calc"),
        ("U:/icons/demo-communication.png",    "Comm"),

        ("U:/icons/demo-keyboard.png",         "Key"),
        ("U:/icons/demo-camera.png",           "Camera"),
        ("U:/icons/demo-qr-generate.png",      "QR"),
        ("U:/icons/demo-audio-record.png",     "Audio"),
        ("U:/icons/demo-usb-browser.png",      "USB"),

        ("U:/icons/demo-phone-dialer.png",     "Phone"),
        ("U:/icons/demo-game.png",             "Game"),
        ("U:/icons/new-eth.png",               "ETH"),
        ("U:/icons/task-buzzer.png",           "Buzzer"),
        ("U:/icons/partly-cloudy-day.png",     "Weather"),
    )

    def __init__(self, screen_w, screen_h):
        self._sw = screen_w
        self._sh = screen_h
        self._btn_refs = []
        self._current_page = None

        self.screen = lv.obj()
        self.screen.remove_style_all()
        self.screen.set_size(screen_w, screen_h)
        self.screen.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
        self.screen.set_style_bg_opa(lv.OPA.COVER, 0)
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen.clear_flag(lv.obj.FLAG.SCROLLABLE)   # 关掉滚动：避免键盘/输入框聚焦时屏幕滚动把内容挤出
        lv.scr_load(self.screen)

        self._create_status_bar()
        self._create_app_grid()

    # -- 状态栏 --

    def _create_status_bar(self):
        bar = lv.obj(self.screen)
        bar.remove_style_all()
        bar.set_size(self._sw, self.STATUS_BAR_H)
        bar.set_pos(0, 0)
        bar.set_style_bg_color(lv.color_hex(0x16213E), 0)
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        ic_set = lv.img(bar)
        ic_set.set_src("U:/icons/settings.png")
        ic_set.set_pos(4, 3)

        self._time_label = lv.label(bar)
        t = utime.localtime()
        self._time_label.set_text("{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
        self._time_label.set_style_text_color(lv.color_hex(0x2C2C46), 0)
        self._time_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._time_label.set_pos((self._sw - 60) // 2, 3)
        _thread.start_new_thread(self._time_tick, ())

        ic_wifi = lv.img(bar)
        ic_wifi.set_src("U:/icons/wifi.png")
        ic_wifi.set_pos(self._sw - 38, 3)

        ic_bat = lv.img(bar)
        ic_bat.set_src("U:/icons/battery.png")
        ic_bat.set_pos(self._sw - 18, 3)

    # -- 图标网格 --

    def _create_app_grid(self):
        grid_w = self.COLS * self.CELL_W
        grid_h = self.ROWS * self.CELL_H
        offset_x = (self._sw - grid_w) // 2
        offset_y = self.STATUS_BAR_H + (self._sh - self.STATUS_BAR_H - grid_h) // 2

        for idx, (icon_path, label_text) in enumerate(self.APP_GRID):
            col = idx % self.COLS
            row = idx // self.COLS
            cx = offset_x + col * self.CELL_W + self.CELL_W // 2
            cy = offset_y + row * self.CELL_H

            btn_size = 48 + self.BTN_PAD
            btn = lv.btn(self.screen)
            btn.set_size(btn_size, btn_size)
            btn.set_pos(cx - btn_size // 2, cy)
            btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_radius(6, 0)
            btn.set_style_pad_all(0, 0)
            btn.set_style_bg_opa(lv.OPA.COVER, lv.STATE.PRESSED)
            btn.set_style_bg_color(lv.color_hex(0x334466), lv.STATE.PRESSED)

            ic = lv.img(btn)
            ic.set_src(icon_path)
            ic.center()

            btn.add_event_cb(
                self._on_icon_clicked,
                lv.EVENT.CLICKED, None,
            )
            self._btn_refs.append((btn, ic, label_text))

    def _on_icon_clicked(self, e):
        """图标点击事件回调。"""
        target = e.get_target()
        for btn, _ic, name in self._btn_refs:
            if btn == target:
                self._open_page(name)
                return

    # -- 页面导航 --

    def _open_page(self, app_name):
        """根据 app_name 查找 PAGE_MAP，创建对应页面。"""
        print("[NAV] open:", app_name)
        page_cls = PAGE_MAP.get(app_name, AppPage)
        self._current_page = page_cls(
            self._sw, self._sh, app_name, self._go_back
        )
        lv.scr_load(self._current_page.screen)

    def _go_back(self, e=None):
        """返回主界面，释放子页面。"""
        print("[NAV] back to main")
        lv.scr_load(self.screen)
        self._current_page = None

    def _time_tick(self):
        """每秒更新状态栏时间。"""
        while True:
            utime.sleep_ms(1000)
            try:
                t = utime.localtime()
                self._time_label.set_text(
                    "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
            except Exception:
                pass

    def set_time(self, text):
        self._time_label.set_text(text)


# =======================================================
#  LCD + 触摸 + LVGL 驱动（320x240 横屏，自包含）
# =======================================================


class YttriumApp:
    """320x240 横屏主应用：内联 LCD 初始化 + LVGL 软件旋转 + ft6x36 触摸。"""

    # -- 屏幕 / 引脚 --
    LCD_PHYS_W = 320          # 面板物理宽（竖屏）—— python_biglcd
    LCD_PHYS_H = 480          # 面板物理高（竖屏）
    SCREEN_W = 480            # LVGL 逻辑宽（旋转后的横屏）
    SCREEN_H = 320            # LVGL 逻辑高

    # -- 触摸 ft6x36 引脚（按板子原理图，示例：ft6x36(irq=40, reset=39, group=1)）--
    PIN_TP_IRQ = 40           # ft6x36 中断引脚
    PIN_TP_RESET = 39         # ft6x36 复位引脚
    TP_I2C_GROUP = 1          # I2C 组号
    # 注：本板背光已默认导通（屏幕能亮），无需单独拉脚；
    # GPIO40 是触摸 IRQ，切勿当背光拉成输出，否则触摸失效。

    # -- 区域参数（硬件旋转后横屏：X:0~479, Y:0~319）--
    XSTART_H = 0x00
    XSTART_L = 0x00
    YSTART_H = 0x00
    YSTART_L = 0x00
    XEND_H = 0x01
    XEND_L = 0xDF     # 0x01DF = 479
    YEND_H = 0x01
    YEND_L = 0x3F     # 0x013F = 319

    # -- 面板初始化序列（320x480 ST7796，来自 python_biglcd）--
    LCD_INIT_DATA = bytes((
        2, 0, 120,
        0, 1, 0xF0,
        1, 1, 0xC3,
        0, 1, 0xF0,
        1, 1, 0x96,
        0, 1, 0x36,
        1, 1, 0x20,   # MADCTL: MV（硬件旋转成横屏）
        0, 1, 0x3A,
        1, 1, 0x05,
        0, 1, 0xB0,
        1, 1, 0x80,
        0, 2, 0xB6,
        1, 1, 0x00,
        1, 1, 0x02,
        0, 4, 0xB5,
        1, 1, 0x02,
        1, 1, 0x03,
        1, 1, 0x00,
        1, 1, 0x04,
        0, 2, 0xB1,
        1, 1, 0x80,
        1, 1, 0x10,
        0, 1, 0xB4,
        1, 1, 0x00,
        0, 1, 0xB7,
        1, 1, 0xC6,
        0, 1, 0xC5,
        1, 1, 0x1C,
        0, 1, 0xE4,
        1, 1, 0x31,
        0, 8, 0xE8,
        1, 1, 0x40,
        1, 1, 0x8A,
        1, 1, 0x00,
        1, 1, 0x00,
        1, 1, 0x29,
        1, 1, 0x19,
        1, 1, 0xA5,
        1, 1, 0x33,
        0, 0, 0xC2,
        0, 0, 0xA7,
        0, 14, 0xE0,
        1, 1, 0xF0, 1, 1, 0x09, 1, 1, 0x13, 1, 1, 0x12, 1, 1, 0x12,
        1, 1, 0x2B, 1, 1, 0x3C, 1, 1, 0x44, 1, 1, 0x4B, 1, 1, 0x1B,
        1, 1, 0x18, 1, 1, 0x17, 1, 1, 0x1D, 1, 1, 0x21,
        0, 14, 0xE1,
        1, 1, 0xF0, 1, 1, 0x09, 1, 1, 0x13, 1, 1, 0x0C, 1, 1, 0x0D,
        1, 1, 0x27, 1, 1, 0x3B, 1, 1, 0x44, 1, 1, 0x4D, 1, 1, 0x0B,
        1, 1, 0x17, 1, 1, 0x17, 1, 1, 0x1D, 1, 1, 0x21,
        0, 1, 0xF0,
        1, 1, 0x3C,
        0, 1, 0xF0,
        1, 1, 0x69,
        0, 0, 0x13,
        0, 0, 0x11,
        0, 0, 0x29,
    ))
    LCD_DISPLAY_ON = bytes((0, 0, 0x11, 2, 0, 20, 0, 0, 0x29))
    LCD_DISPLAY_OFF = bytes((0, 0, 0x28, 2, 0, 120, 0, 0, 0x10))
    LCD_INVALID = bytes((
        0, 4, 0x2a,
        1, 1, XSTART_H, 1, 1, XSTART_L, 1, 1, XEND_H, 1, 1, XEND_L,
        0, 4, 0x2b,
        1, 1, YSTART_H, 1, 1, YSTART_L, 1, 1, YEND_H, 1, 1, YEND_L,
        0, 0, 0x2c,
    ))

    def __init__(self):
        self._tp = None
        self._init_lcd()
        self._init_pins()
        self._init_touch()        # 真实 ft6x36 触摸
        self._init_lvgl()
        self.main_screen = MainScreen(self.SCREEN_W, self.SCREEN_H)
        # 不在这里启动渲染子线程：task_handler 改由 __main__ 的主线程循环跑，
        # 这样 read_cb/_ft_read 里的 read_xy 就在主线程执行（ft6x36 只在主线程读得到坐标）。
        self._init_sim_touch()   # 假指针 indev（REPL 调试用；主线程循环跑时 REPL 不可用）

    # ---------------------- LCD 面板初始化 ----------------------
    def _init_lcd(self):
        print("[LCD] init ...")
        Pin(Pin.GPIO37, Pin.OUT, Pin.PULL_DISABLE, 1)  # LCD_VDD_EN 供电
        self._lcd = LCD()
        self._lcd.lcd_init(
            self.LCD_INIT_DATA, self.LCD_PHYS_W, self.LCD_PHYS_H,
            26000, 1, 4, 0,   # SPI 时钟 26MHz
            self.LCD_INVALID, self.LCD_DISPLAY_ON, self.LCD_DISPLAY_OFF, None,
        )

    # ---------------------- 引脚 ----------------------
    def _init_pins(self):
        # GPIO37 LCD 供电已在 _init_lcd 置高。
        # 背光本板默认导通（屏幕能亮）；GPIO40 是触摸 IRQ、GPIO39 是触摸 RESET，
        # 由 ft6x36 自行管理，这里不能动它们，否则触摸失效。
        pass

    # ---------------------- 触摸（ft6x36）----------------------
    def _init_touch(self):
        print("[TP] init ft6x36 ...")
        try:
            # width/height/i2c_mode 是关键（参照 _main(2).py）：传物理面板尺寸 + i2c_mode=1
            self._tp = Ft6x36(irq=self.PIN_TP_IRQ,
                              reset=self.PIN_TP_RESET,
                              group=self.TP_I2C_GROUP,
                              width=self.LCD_PHYS_W, height=self.LCD_PHYS_H,
                              i2c_mode=1)
            self._tp.activate()
            self._tp.init()
            self._tp_lock = _thread.allocate_lock()
            print("[TP] ft6x36 ready")
        except Exception as e:
            print("[TP] init failed（触摸不可用）:", e)
            self._tp = None

    # ---------------------- LVGL 显示 / 输入驱动 ----------------------
    def _init_lvgl(self):
        print("[LVGL] init ...")
        lv.init()

        # 显示缓冲（半屏双缓冲，按逻辑横屏 480x320 算，每次刷半屏 = 480x160）
        self._disp_buf = lv.disp_draw_buf_t()
        # 整屏单缓冲：半屏双缓冲在整屏重绘（切屏）时分上下两半刷、有明显的"半屏切"接缝；
        # 整屏一次刷完，切屏干净。总 RAM 与原来两块半屏相同（~300KB）。
        self._buf1 = bytearray(self.SCREEN_W * self.SCREEN_H * 2)
        self._disp_buf.init(self._buf1, None, len(self._buf1) // 2)

        # 显示驱动：硬件旋转后逻辑横屏 480x320，LVGL 不做软件旋转
        self._disp_drv = lv.disp_drv_t()
        self._disp_drv.init()
        self._disp_drv.draw_buf = self._disp_buf
        self._disp_drv.flush_cb = self._lcd.lcd_write
        self._disp_drv.hor_res = self.SCREEN_W     # 480（逻辑横屏）
        self._disp_drv.ver_res = self.SCREEN_H     # 320
        self._disp_drv.sw_rotate = 0
        self._disp_drv.register()

        # 触摸输入设备：read_cb 用 _ft_read（read_xy + 旋转）。
        # 现在没有手动渲染线程了，只有 lvgl 自己的内部线程调 task_handler，不会有两个线程抢 task_handler
        # 的冲突；read_xy 在这个内部线程里跑（和主线程一样是“对的上下文”）。
        if self._tp is not None:
            self._indev_drv = lv.indev_drv_t()
            self._indev_drv.init()
            self._indev_drv.type = lv.INDEV_TYPE.POINTER
            self._indev_drv.read_cb = self._ft_read
            self._indev_drv.register()

    def _ft_read(self, drv, data):
        """LVGL read_cb：read_xy() + 硬件旋转翻转（参照 _main(2).py）。跑在主线程。"""
        self._tp_lock.acquire()
        try:
            xy = self._tp.read_xy()
            if xy is not None and len(xy) >= 2:
                raw_x, raw_y = int(xy[0]), int(xy[1])
                if raw_x == 0 and raw_y == 0:
                    data.state = lv.INDEV_STATE.RELEASED
                    return
                # 硬件 MADCTL=0x20 (MV=1)：物理竖屏 320x480 → 逻辑横屏 480x320
                # logic_x = raw_y, logic_y = LCD_PHYS_W - 1 - raw_x
                logic_x = raw_y
                logic_y = self.LCD_PHYS_W - 1 - raw_x
                if logic_x < 0:
                    logic_x = 0
                elif logic_x >= self.SCREEN_W:
                    logic_x = self.SCREEN_W - 1
                if logic_y < 0:
                    logic_y = 0
                elif logic_y >= self.SCREEN_H:
                    logic_y = self.SCREEN_H - 1
                data.point.x = logic_x
                data.point.y = logic_y
                data.state = lv.INDEV_STATE.PRESSED
            else:
                data.state = lv.INDEV_STATE.RELEASED
        except Exception as e:
            print("[TP] err", e)
            data.state = lv.INDEV_STATE.RELEASED
        finally:
            self._tp_lock.release()

    def _start_render_thread(self):
        print("[THREAD] starting LVGL render thread ...")
        _thread.start_new_thread(self._render_loop, ())

    def _render_loop(self):
        """渲染线程：只跑 LVGL task_handler。触摸读取在 _ft_read（LVGL 回调）里。"""
        while True:
            lv.tick_inc(20)
            lv.task_handler()
            utime.sleep_ms(20)

    # ---------------------- 模拟触摸（tp 未就绪时用）----------------------
    def _init_sim_touch(self):
        """注册一个假指针 indev，由渲染线程驱动点击状态机。

        tp 固件就绪后：取消 __init__ 里的 self._init_touch() 注释，
        并把本方法调用注释掉即可。

        机制：sim_tap() 在主线程里把一次点击排入 self._sim_queue；
        _sim_read() 在渲染线程每次被调用时，按队列推进
        PRESSED(若干轮) -> RELEASED(若干轮)，从而稳定地让 LVGL 识别为
        一次完整的点击并触发 CLICKED。时序完全跑在渲染线程的 LVGL 上下文里，
        避免主线程连击时与渲染线程竞争导致“要点好几次才生效”。
        """
        self._sim_queue = []          # 待执行的点击任务队列
        self._sim_cur = None          # 当前正在执行的任务

        self._sim_indev = lv.indev_drv_t()
        self._sim_indev.init()
        self._sim_indev.type = lv.INDEV_TYPE.POINTER
        self._sim_indev.read_cb = self._sim_read
        self._sim_indev.register()

    def _sim_read(self, drv, data):
        """indev read 回调（渲染线程每 ~5ms 调一次）：推进点击状态机。"""
        # 当前任务跑完则取下一个
        if self._sim_cur is None and self._sim_queue:
            self._sim_cur = self._sim_queue.pop(0)

        cur = self._sim_cur
        if cur is None:
            data.state = 0   # 空闲：松开
            return

        # cur = {"rx":.., "ry":.., "press_left":N, "release_left":N}
        if cur["press_left"] > 0:
            data.point.x = cur["rx"]
            data.point.y = cur["ry"]
            data.state = 1   # PRESSED
            cur["press_left"] -= 1
        elif cur["release_left"] > 0:
            data.state = 0   # RELEASED
            cur["release_left"] -= 1
        else:
            self._sim_cur = None
            data.state = 0

    def sim_tap(self, lx, ly, press_rounds=6, release_rounds=6):
        """点逻辑屏幕坐标 (lx, ly)，触发一次 CLICKED。

        横屏由面板 MADCTL 硬件旋转完成，LVGL 看到的就是逻辑 480x320，
        所以直接用逻辑坐标即可（不再需要物理反算）。

        实现：把一次点击（press_rounds 轮 PRESSED + release_rounds 轮 RELEASED）
        排入队列，由主循环 task_handler 在 _sim_read 里推进。本方法给一个最大等待时间，
        到点即返回；点击会在主循环里继续完成、触发 CLICKED。
        连击安全：多次 sim_tap 依次排队、顺序执行，不会互相覆盖。
        """
        rx, ry = lx, ly
        self._sim_queue.append({
            "rx": rx, "ry": ry,
            "press_left": press_rounds,
            "release_left": release_rounds,
        })
        # 给渲染线程足够时间消费这一帧（press+release 共 12 轮，每轮~5ms≈60ms，
        # 留足余量到 300ms）。用较长 sleep 让步，避免主线程忙等饿死渲染线程。
        # 到时仍未消费完也不强等——点击照样会在后台完成。
        for _ in range(30):
            utime.sleep_ms(10)
            if not self._sim_queue and self._sim_cur is None:
                break


if __name__ == "__main__":
    app = YttriumApp()
    print("Yttrium 480x320 (hardware-rotate) main screen ready!")

    # ---------------------- REPL 模拟点击（调试用，真实触摸也可同时用）----------------------
    def tap(lx, ly):
        app.sim_tap(lx, ly)

    def tap_grid(col, row):
        CELL_W, CELL_H = 56, 70
        offset_x = (app.SCREEN_W - 5 * CELL_W) // 2
        offset_y = 22 + (app.SCREEN_H - 22 - 3 * CELL_H) // 2
        cx = offset_x + col * CELL_W + CELL_W // 2
        cy = offset_y + row * CELL_H + CELL_H // 2
        app.sim_tap(cx, cy)

    def back():
        app.sim_tap(29, 15)

    # ---------------------- 主线程跑 task_handler（真实触摸的关键）----------------------
    # ft6x36 的 read_xy 只在主线程读得到坐标，所以 task_handler 必须放主线程，
    # 这样 _ft_read 里的 read_xy 才在主线程执行。
    # 代价：运行时 REPL 被占用（不回 >>>）；Ctrl-C 中断回 REPL 调试。
    # 想用上面 tap_grid 调试（无真实触摸）：注释掉下面这个 while、重启。
    print("running on main thread (REPL busy; Ctrl-C to debug)")
    while True:
        lv.tick_inc(20)
        lv.task_handler()
        utime.sleep_ms(20)
