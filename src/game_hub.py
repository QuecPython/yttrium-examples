# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage, PAGE_MAP

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
            btn.set_style_bg_color(lv.color_hex(0x334466), 0)
            btn.set_style_bg_opa(lv.OPA.COVER, 0)
            btn.set_style_shadow_width(0, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_radius(8, 0)
            btn.set_style_pad_all(0, 0)
            btn.set_style_bg_color(lv.color_hex(0x00E676), lv.STATE.PRESSED)
            ic = lv.img(btn)
            ic.set_src(icon_path)
            ic.center()
            lbl = lv.label(self.screen)
            lbl.set_text(name)
            lbl.set_style_text_font(lv.font_montserrat_14, 0)
            lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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

