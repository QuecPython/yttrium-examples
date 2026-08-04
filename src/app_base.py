# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
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
        back_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        back_lbl.center()

        # 页面标题
        title_lbl = lv.label(bar)
        title_lbl.set_text(title)
        title_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        title_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        hint.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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


# 页面注册表 — 由 _main.py 在 import 时填充
PAGE_MAP = {}
