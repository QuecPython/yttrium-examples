# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class SnakePage(AppPage):
    """贪吃蛇游戏 -- 34x20 网格，触摸滑动操控。"""

    CELL = 14
    COLS = 34
    ROWS = 20
    OX = 2                     # 网格 X 偏移（34*14=476，居中于 480）
    OY = 3                     # 网格 Y 偏移（20*14=280，居中于 286）
    BASE_TICK = 150             # 初始帧间隔 ms

    COL_EMPTY = 0x16213E
    COL_HEAD  = 0x00E676
    COL_BODY  = 0x4CAF50
    COL_FOOD  = 0xFF5252

    def _create_content(self):
        # -- 游戏容器 --
        gc = lv.obj(self.screen)
        gc.remove_style_all()
        gc.set_size(self._sw, self.content_h)
        gc.set_pos(0, self.content_y)
        gc.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        gc.set_style_bg_opa(lv.OPA.COVER, 0)
        gc.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        gc.set_style_pad_all(0, 0)
        gc.clear_flag(lv.obj.FLAG.SCROLLABLE)
        gc.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(gc)
        self._gc = gc

        # -- 网格 --
        self._cells = []
        for r in range(self.ROWS):
            row = []
            for c in range(self.COLS):
                cell = lv.obj(gc)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(self.OX + c * self.CELL,
                             self.OY + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)  # 穿透触摸到 gc
                row.append(cell)
                self._refs.append(cell)
            self._cells.append(row)

        # -- 分数（标题栏右侧）--
        self._score_label = lv.label(self.screen)
        self._score_label.set_text("Score: 0")
        self._score_label.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._score_label.set_pos(self._sw - 80, 7)
        self._refs.append(self._score_label)

        # -- 提示遮罩 --
        pw, ph = 180, 60
        panel = lv.obj(gc)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((self._sw - pw) // 2,
                       (self.content_h - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0x000000), 0)
        panel.set_style_bg_opa(lv.OPA._60, 0)
        panel.set_style_radius(8, 0)
        panel.clear_flag(lv.obj.FLAG.CLICKABLE)   # 穿透触摸到 gc
        self._refs.append(panel)
        self._panel = panel

        self._overlay = lv.label(panel)
        self._overlay.set_text("Tap to Start")
        self._overlay.set_style_text_font(lv.font_montserrat_14, 0)
        self._overlay.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._overlay.center()
        self._refs.append(self._overlay)

        # -- 游戏状态 --
        self._state = "WAITING"
        self._snake = []
        self._direction = (1, 0)
        self._next_dir = (1, 0)
        self._food = None
        self._score = 0
        self._running = False
        self._touch_start = None
        # tick 用 lv.timer 驱动（回调在 task_handler/主线程里执行），不再开子线程碰 LVGL
        self._tick_timer = lv.timer_create(self._on_tick, self.BASE_TICK, None)

    # ---------- 游戏启动 ----------

    def _start_game(self):
        self._snake = [
            (self.COLS // 2, self.ROWS // 2),
            (self.COLS // 2 - 1, self.ROWS // 2),
            (self.COLS // 2 - 2, self.ROWS // 2),
        ]
        self._direction = (1, 0)
        self._next_dir = (1, 0)
        self._score = 0
        self._score_label.set_text("Score: 0")

        # 清空网格 -> 画初始蛇
        for r in range(self.ROWS):
            for c in range(self.COLS):
                self._cells[r][c].set_style_bg_color(
                    lv.color_hex(self.COL_EMPTY), 0)
        for i, (c, r) in enumerate(self._snake):
            col = self.COL_HEAD if i == 0 else self.COL_BODY
            self._cells[r][c].set_style_bg_color(lv.color_hex(col), 0)

        self._spawn_food()

        self._state = "PLAYING"
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")

        self._running = True
        # tick 由 lv.timer 驱动（主线程），不再开子线程
        if self._tick_timer:
            self._tick_timer.set_period(self._tick_period())

    # ---------- 食物 ----------

    def _spawn_food(self):
        import urandom
        snake_set = set(self._snake)
        empty = []
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if (c, r) not in snake_set:
                    empty.append((c, r))
        if not empty:
            self._end_game()
            return
        self._food = empty[urandom.getrandbits(10) % len(empty)]
        fc, fr = self._food
        self._cells[fr][fc].set_style_bg_color(
            lv.color_hex(self.COL_FOOD), 0)

    # ---------- 游戏循环 ----------

    def _tick_period(self):
        return max(80, self.BASE_TICK - self._score * 2)

    def _on_tick(self, timer):
        """lv.timer 回调（跑在主线程 task_handler 里）：推进一步；顺手按分数刷新周期。"""
        try:
            if self._state == "PLAYING":
                self._game_tick()
            timer.set_period(self._tick_period())
        except Exception as e:
            print("[SNAKE] tick error:", e)

    def _game_tick(self):
        self._direction = self._next_dir
        hx, hy = self._snake[0]
        nx = hx + self._direction[0]
        ny = hy + self._direction[1]

        # 碰墙
        if nx < 0 or nx >= self.COLS or ny < 0 or ny >= self.ROWS:
            self._end_game()
            return
        # 碰自身
        if (nx, ny) in self._snake:
            self._end_game()
            return

        self._snake.insert(0, (nx, ny))

        old_tail = None
        if (nx, ny) == self._food:
            self._score += 1
            self._score_label.set_text("Score: {}".format(self._score))
            self._spawn_food()
        else:
            old_tail = self._snake.pop()
            tc, tr = old_tail
            self._cells[tr][tc].set_style_bg_color(
                lv.color_hex(self.COL_EMPTY), 0)

        # 增量渲染
        self._cells[ny][nx].set_style_bg_color(
            lv.color_hex(self.COL_HEAD), 0)
        if len(self._snake) > 1:
            bx, by = self._snake[1]
            self._cells[by][bx].set_style_bg_color(
                lv.color_hex(self.COL_BODY), 0)

    # ---------- 游戏结束 ----------

    def _end_game(self):
        self._state = "GAME_OVER"
        self._running = False
        self._panel.set_style_bg_opa(lv.OPA._60, 0)
        self._overlay.set_text("Game Over!\nScore: {}\nTap to restart".format(
            self._score))
        self._overlay.center()

    # ---------- 触摸输入 ----------

    def _get_touch_pos(self):
        """通过活动 indev 获取当前触摸坐标。"""
        indev = lv.indev_get_act()
        if indev:
            pt = lv.point_t()
            indev.get_point(pt)
            return (pt.x, pt.y)
        return None

    def _on_touch(self, e):
        code = e.get_code()

        if code == lv.EVENT.PRESSED:
            pos = self._get_touch_pos()
            if pos:
                self._touch_start = pos
            return

        if code != lv.EVENT.RELEASED:
            return

        # 点击（短按）-> 开始 / 重新开始
        if self._state in ("WAITING", "GAME_OVER"):
            self._start_game()
            return

        # 滑动 -> 改变方向
        if self._state == "PLAYING" and self._touch_start:
            pos = self._get_touch_pos()
            if not pos:
                return
            dx = pos[0] - self._touch_start[0]
            dy = pos[1] - self._touch_start[1]
            if abs(dx) < 10 and abs(dy) < 10:
                return
            if abs(dx) > abs(dy):
                nd = (1, 0) if dx > 0 else (-1, 0)
            else:
                nd = (0, 1) if dy > 0 else (0, -1)
            cur = self._direction
            if (nd[0] + cur[0], nd[1] + cur[1]) != (0, 0):
                self._next_dir = nd

    # ---------- 退出清理 ----------

    def _on_back(self, e=None):
        print("[SNAKE] cleaning up...")
        self._running = False
        self._state = "GAME_OVER"
        utime.sleep_ms(self.BASE_TICK + 20)
        super()._on_back(e)


