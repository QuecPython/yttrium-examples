# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

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
        self._total_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        name_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        back_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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
        detail.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
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

