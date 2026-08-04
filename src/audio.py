# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        fn.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
            tlbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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


