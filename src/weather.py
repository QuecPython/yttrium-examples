# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        city.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        desc.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
            cap_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        hint.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        hint.set_pos((w - 260) // 2, info_y + info_h + 8)
        self._refs.append(hint)


# =======================================================
#  游戏二级界面（主桌面点 Game 进来，再选具体游戏）
# =======================================================

