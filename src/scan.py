# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        hint.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        hint.set_pos(cx - 80, by + box + 12)
        self._refs.append(hint)
        # TODO: 接入摄像头解码（需 Camera 固件）


# =======================================================
#  蜂鸣器 / 天气
# =======================================================

