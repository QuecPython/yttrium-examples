# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class EthInfoPage(AppPage):
    """网络信息页面（真实以太网初始化）。"""
    def _create_content(self):
        base_y = self.content_y
        w = self._sw

        # 动态值标签（key 固定，value 可更新）
        self._info_keys = ("MAC", "IP", "Mask", "GW", "DNS1", "DNS2", "Status")
        self._info_vals = {}  # key → lv.label
        for i, key in enumerate(self._info_keys):
            ry = base_y + 4 + i * 26
            kl = lv.label(self.screen)
            kl.set_text(key)
            kl.set_style_text_font(lv.font_montserrat_14, 0)
            kl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            kl.set_pos(16, ry)
            self._refs.append(kl)

            vl = lv.label(self.screen)
            vl.set_text("...")
            vl.set_style_text_font(lv.font_montserrat_14, 0)
            vl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            vl.set_pos(80, ry)
            self._refs.append(vl)
            self._info_vals[key] = vl

        # 按钮行
        btn_y = base_y + self.content_h - 36
        self._mk_btn(16, btn_y, 72, "Init",   0x1565C0, 0xFFFFFF, self._do_init)
        self._mk_btn(96, btn_y, 72, "Refresh", 0x0277BD, 0xFFFFFF, self._do_refresh)
        self._mk_btn(176, btn_y, 72, "DHCP",   0x00838F, 0xFFFFFF, self._do_dhcp)

        # 初始化以太网
        self._nic = None
        self._do_init()

    # -- 以太网操作 --

    def _do_init(self):
        """初始化 W5500 网卡。"""
        try:
            import ethernet
            mac = b'\x00\x11\x22\x33\x44\x55'
            # 使用默认引脚配置（-1 沿用上次/默认值）
            self._nic = ethernet.W5500(mac, '', '', '', -1, -1, -1, -1, 0)
            self._set_val("Status", "Init OK")
            self._do_refresh()
        except ImportError:
            self._set_val("Status", "No ethernet module")
        except Exception as ex:
            self._set_val("Status", "Init err: {}".format(ex))

    def _do_refresh(self):
        """读取 ipconfig 并更新显示。"""
        if self._nic is None:
            return
        try:
            info = self._nic.ipconfig()
            if info and len(info) >= 2:
                # info[0] = (mac, hostname)
                # info[1] = (iptype, ip, subnet, gateway, dns1, dns2)
                mac_host = info[0]
                net = info[1]
                self._set_val("MAC", mac_host[0])
                self._set_val("IP", net[1] if net[1] else "(none)")
                self._set_val("Mask", net[2] if net[2] else "(none)")
                self._set_val("GW", net[3] if net[3] else "(none)")
                self._set_val("DNS1", net[4] if net[4] else "(none)")
                self._set_val("DNS2", net[5] if net[5] else "(none)")
                self._set_val("Status", "OK  " + mac_host[1])
        except Exception as ex:
            self._set_val("Status", "Read err: {}".format(ex))

    def _do_dhcp(self):
        """DHCP 获取 IP。"""
        if self._nic is None:
            return
        try:
            self._set_val("Status", "DHCP...")
            ret = self._nic.dhcp()
            if ret == 0:
                self._set_val("Status", "DHCP OK")
                self._nic.set_up()
                self._do_refresh()
            else:
                self._set_val("Status", "DHCP fail ({})".format(ret))
        except Exception as ex:
            self._set_val("Status", "DHCP err: {}".format(ex))

    # -- UI 辅助 --

    def _set_val(self, key, text):
        lbl = self._info_vals.get(key)
        if lbl:
            lbl.set_text(str(text))

    def _mk_btn(self, x, y, w, text, bg, fg, cb):
        btn = lv.btn(self.screen)
        btn.set_size(w, 28)
        btn.set_pos(x, y)
        btn.set_style_bg_color(lv.color_hex(bg), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(4, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_pad_all(0, 0)
        btn.add_event_cb(lambda e: cb(), lv.EVENT.CLICKED, None)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(lv.font_montserrat_14, 0)
        lbl.set_style_text_color(lv.color_hex(fg), 0)
        lbl.center()
        self._refs.extend((btn, lbl))


