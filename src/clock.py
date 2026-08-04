# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        self._date_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        sw_title.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        sw_title.set_pos(rx, base_y + 5)
        self._refs.append(sw_title)

        # 秒表数值
        self._sw_lbl = lv.label(self.screen)
        self._sw_lbl.set_text("00:00.00")
        self._sw_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._sw_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._sw_lbl.set_pos(rx, base_y + 30)
        self._refs.append(self._sw_lbl)

        # 计次列表（最多显示 3 条）
        self._lap_labels = []
        for i in range(3):
            lbl = lv.label(self.screen)
            lbl.set_text("")
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        self._btn_lr_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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


