# Yttrium Demo — weather page
import utime
import lvgl as lv
from app_base import AppPage

# ============ 配置 ============
CITIES = [
    ("Guilin",   "Guilin"),
    ("Shanghai", "Shanghai"),
    ("Beijing",  "Beijing"),
    ("Guangzhou","Guangzhou"),
    ("Shenzhen", "Shenzhen"),
]
CITY_IDX = 0
CITY, CITY_NAME = CITIES[CITY_IDX]
FETCH_INTERVAL_MS = 900000

WEATHER_ICONS = {
    "113": "weather_sunny", "116": "weather_partly_cloudy",
    "119": "weather_cloudy", "122": "weather_cloudy",
    "143": "weather_foggy", "248": "weather_foggy", "260": "weather_foggy",
    "176": "weather_rainy", "263": "weather_rainy", "266": "weather_rainy",
    "293": "weather_rainy", "296": "weather_rainy", "299": "weather_rainy",
    "302": "weather_rainy", "305": "weather_rainy", "308": "weather_rainy",
    "353": "weather_rainy", "356": "weather_rainy", "359": "weather_rainy",
    "179": "weather_snowy", "227": "weather_snowy", "230": "weather_snowy",
    "323": "weather_snowy", "326": "weather_snowy", "329": "weather_snowy",
    "332": "weather_snowy", "338": "weather_snowy", "368": "weather_snowy",
    "371": "weather_snowy",
    "200": "weather_thunder", "386": "weather_thunder", "389": "weather_thunder",
    "392": "weather_thunder", "395": "weather_thunder",
}


class WeatherPage(AppPage):

    def _create_content(self):
        base_y = self.content_y
        w = self._sw
        h = self.content_h
        top_h = h * 3 // 5
        bot_h = h - top_h
        cx = w // 2

        # ====== 上半区 ======
        top_card = lv.obj(self.screen)
        top_card.remove_style_all()
        top_card.set_size(w - 16, top_h - 8)
        top_card.set_pos(8, base_y + 4)
        top_card.set_style_bg_color(lv.color_hex(0x16213E), 0)
        top_card.set_style_bg_opa(lv.OPA.COVER, 0)
        top_card.set_style_radius(12, 0)
        top_card.set_style_pad_all(0, 0)
        top_card.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(top_card)

        self._date_lbl = lv.label(top_card)
        self._date_lbl.set_text("----/--/--")
        self._date_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._date_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._date_lbl.set_pos(16, 12)
        self._refs.append(self._date_lbl)

        self._time_lbl = lv.label(top_card)
        self._time_lbl.set_text("--:--:--")
        self._time_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._time_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._time_lbl.set_pos(16, 36)
        self._refs.append(self._time_lbl)

        self._city_btn = lv.btn(top_card)
        self._city_btn.set_size(90, 24)
        self._city_btn.set_pos(14, 56)
        self._city_btn.set_style_bg_color(lv.color_hex(0x334466), 0)
        self._city_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        self._city_btn.set_style_radius(4, 0)
        self._city_btn.set_style_shadow_width(0, 0)
        self._city_btn.set_style_border_width(0, 0)
        self._city_btn.set_style_pad_all(0, 0)
        self._city_btn.add_event_cb(lambda e: self._next_city(), lv.EVENT.CLICKED, None)
        self._city_text = lv.label(self._city_btn)
        self._city_text.set_text(CITY_NAME + " >")
        self._city_text.set_style_text_font(lv.font_montserrat_14, 0)
        self._city_text.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._city_text.center()
        self._refs.extend((self._city_btn, self._city_text))

        self._weather_icon = lv.img(top_card)
        self._weather_icon.set_size(48, 48)
        self._weather_icon.set_pos(w - 16 - 48 - 20, 10)
        self._weather_icon.set_src("U:/icons/weather_sunny.png")
        self._refs.append(self._weather_icon)

        self._temp_lbl = lv.label(top_card)
        self._temp_lbl.set_text("--")
        self._temp_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._temp_lbl.set_style_text_color(lv.color_hex(0xFF9800), 0)
        self._temp_lbl.set_pos(cx + 12, 12)
        self._refs.append(self._temp_lbl)

        self._desc_lbl = lv.label(top_card)
        self._desc_lbl.set_text("--")
        self._desc_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._desc_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._desc_lbl.set_pos(cx + 12, 40)
        self._refs.append(self._desc_lbl)

        self._hum_lbl = lv.label(top_card)
        self._hum_lbl.set_text("--")
        self._hum_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._hum_lbl.set_style_text_color(lv.color_hex(0x4DA6FF), 0)
        self._hum_lbl.set_pos(cx + 12, 64)
        self._refs.append(self._hum_lbl)

        self._status_lbl = lv.label(top_card)
        self._status_lbl.set_text("Wait...")
        self._status_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._status_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._status_lbl.set_pos(16, top_h - 28)
        self._refs.append(self._status_lbl)

        # ====== 下半区：3 张预报卡片 ======
        self._forecast_refs = []
        card_w = (w - 24) // 3
        card_h = bot_h - 8
        days = ("Today", "Tomorrow", "Day+2")
        for i in range(3):
            fx = 8 + i * (card_w + 4)
            fy = base_y + top_h
            f_card = lv.obj(self.screen)
            f_card.remove_style_all()
            f_card.set_size(card_w, card_h)
            f_card.set_pos(fx, fy)
            f_card.set_style_bg_color(lv.color_hex(0x16213E), 0)
            f_card.set_style_bg_opa(lv.OPA.COVER, 0)
            f_card.set_style_radius(10, 0)
            f_card.set_style_pad_all(0, 0)
            f_card.clear_flag(lv.obj.FLAG.CLICKABLE)
            self._refs.append(f_card)

            f_icon = lv.img(f_card)
            f_icon.set_size(48, 48)
            f_icon.set_pos((card_w - 48) // 2, 0)
            f_icon.set_src("U:/icons/weather_sunny.png")
            self._refs.append(f_icon)

            f_day = lv.label(f_card)
            f_day.set_text(days[i])
            f_day.set_style_text_font(lv.font_montserrat_14, 0)
            f_day.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            f_day.set_pos(4, 52)
            self._refs.append(f_day)

            f_temp = lv.label(f_card)
            f_temp.set_text("--")
            f_temp.set_style_text_font(lv.font_montserrat_14, 0)
            f_temp.set_style_text_color(lv.color_hex(0xFF9800), 0)
            f_temp.set_pos(4, card_h - 22)
            self._refs.append(f_temp)

            self._forecast_refs.append((f_icon, f_day, f_temp))

        # ====== Timer ======
        self._tick_count = 0
        self._fetch_interval_ticks = max(1, FETCH_INTERVAL_MS // 1000)
        self._timer_active = True
        self._fetching = False
        self._timer = lv.timer_create(self._tick, 1000, None)

    # ============ Timer ============

    def _tick(self, timer):
        if not self._timer_active:
            return
        self._tick_count += 1
        try:
            t = utime.localtime()
            self._date_lbl.set_text("{:04d}/{:02d}/{:02d}".format(t[0], t[1], t[2]))
            self._time_lbl.set_text("{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))
        except Exception:
            pass

        need = (self._tick_count == 3) or \
               (self._tick_count > 3 and (self._tick_count - 3) % self._fetch_interval_ticks == 0)
        if need and not self._fetching:
            self._fetching = True
            self._fetch_weather()

    # ============ Fetch ============

    def _fetch_weather(self):
        print("[WEATHER] fetch")
        try:
            import request

            url = "http://wttr.in/{}?format=j1".format(CITY)
            print("[WEATHER] GET", url)
            resp = request.get(url)
            data = resp.json()
            resp.close()
            print("[WEATHER] got data")

            cur = data["current_condition"][0]
            self._temp_lbl.set_text("{}".format(cur["temp_C"]))
            self._desc_lbl.set_text(cur["weatherDesc"][0]["value"])
            self._hum_lbl.set_text("{}%".format(cur.get("humidity", "--")))
            ic = WEATHER_ICONS.get(str(cur["weatherCode"]), "weather_partly_cloudy")
            self._weather_icon.set_src("U:/icons/{}.png".format(ic))

            for i, d in enumerate(data["weather"][:3]):
                icon, day_lbl, temp_lbl = self._forecast_refs[i]
                fc_code = d["hourly"][4]["weatherCode"]
                fc_ic = WEATHER_ICONS.get(str(fc_code), "weather_partly_cloudy")
                icon.set_src("U:/icons/{}.png".format(fc_ic))
                temp_lbl.set_text("{}/{}".format(d["maxtempC"], d["mintempC"]))

            self._status_lbl.set_text("OK {:02d}:{:02d}".format(
                utime.localtime()[3], utime.localtime()[4]))

        except Exception as e:
            print("[WEATHER]", e)
            self._status_lbl.set_text("Err")
        self._fetching = False

    # ============ City ============

    def _next_city(self):
        global CITY_IDX, CITY, CITY_NAME
        CITY_IDX = (CITY_IDX + 1) % len(CITIES)
        CITY, CITY_NAME = CITIES[CITY_IDX]
        self._city_text.set_text(CITY_NAME + " >")
        self._status_lbl.set_text("Switch...")
        self._tick_count = 0
        self._fetching = False

    def _on_back(self, e=None):
        self._timer_active = False
        super()._on_back(e)
