# Yttrium Demo — main entry point
import sys
import utime
import _thread
import lvgl as lv
from machine import LCD, Pin
from tp import ft6x36 as Ft6x36
try:
    import net
    HAS_NET = True
except ImportError:
    HAS_NET = False

# 确保 /usr/ 在模块搜索路径中（QuecPython 导入其他 .py 文件所需）
sys.path.insert(0, "/usr")

from app_base import AppPage
from led import LedPage
from clock import ClockPage
from adc import AdcPage
from calc import CalcPage
from can import CanPage
from keyboard import KeyboardPage
# from camera import CameraPage
from qr_shop import QrPage
# from audio import AudioPage
from usb_browser import UsbPage
from phone import PhonePage
from snake import SnakePage
from game_2048 import Game2048Page
from tetris import TetrisPage
from scan import ScanPage
from buzzer import BuzzerPage
from weather import WeatherPage
from game_hub import GameHubPage
from comm_hub import CommHubPage
from uart import UartPage
from at import AtPage
from rs485 import Rs485Page
from eth_hub import EthHubPage
from eth_info import EthInfoPage
from ping import PingPage
from tcp import TcpPage

# =======================================================
# 填充页面注册表到 app_base（Hub 文件引用 app_base.PAGE_MAP）
# =======================================================

from app_base import PAGE_MAP
PAGE_MAP.update({
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
    # "Camera": CameraPage,
    "QR":     QrPage,
    # "Audio":  AudioPage,
    "USB":    UsbPage,
    "Phone":  PhonePage,
    "Snake":  SnakePage,
    "2048":   Game2048Page,
    "Tetris": TetrisPage,
    "Scan":   ScanPage,
})


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
        self._time_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._time_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._time_label.set_pos((self._sw - 60) // 2, 3)
        _thread.start_new_thread(self._time_tick, ())

        # 信号强度图标（lv.timer 在主线程轮询，不卡 UI）
        self._sig_icon = lv.img(bar)
        self._sig_icon.set_src("U:/icons/sig_0.png")
        self._sig_icon.set_pos(self._sw - 84, 5)
        if HAS_NET:
            self._sig_timer = lv.timer_create(self._sig_tick, 5000, None)

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

    def _sig_tick(self, timer):
        """lv.timer 回调（主线程）：每 5 秒刷新信号图标。"""
        try:
            csq = net.csqQueryPoll()
            if csq >= 0 and csq <= 31:
                level = min(4, max(0, csq * 5 // 32))
                self._sig_icon.set_src("U:/icons/sig_{}.png".format(level))
            else:
                self._sig_icon.set_src("U:/icons/sig_0.png")
        except Exception:
            self._sig_icon.set_src("U:/icons/sig_0.png")

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
