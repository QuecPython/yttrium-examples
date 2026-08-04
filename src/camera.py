# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        model.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
            c1.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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


