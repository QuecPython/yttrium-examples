# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        p2.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
            ln.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            ln.set_pos(50, ry + 1)
            self._refs.append(ln)
            if is_dir:
                la = lv.label(self.screen)
                la.set_text(">")
                la.set_style_text_font(lv.font_montserrat_14, 0)
                la.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                la.set_pos(w - 14, ry + 1)
                self._refs.append(la)

        # 翻页
        pg = lv.label(self.screen)
        pg.set_text("1 / 3")
        pg.set_style_text_font(lv.font_montserrat_14, 0)
        pg.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        pg.set_pos(w // 2 - 14, base_y + 206)
        self._refs.append(pg)
        # TODO: 读取 U:/ 真实文件列表


