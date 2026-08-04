# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class Game2048Page(AppPage):
    """2048 游戏 -- 4x4 网格，滑动合并。"""

    SIZE = 4
    CELL = 48
    GAP = 4
    # [诊断] 设 False：方块只变色、不显示数字，用来排查"网格倾斜"是否跟数字渲染有关
    SHOW_NUMBERS = True
    # (背景色, 文字色)
    TILE_COLORS = {
        0:    (0x1A1A2E, 0x1A1A2E),
        2:    (0x334466, 0xFFFFFF),
        4:    (0x3D5A80, 0xFFFFFF),
        8:    (0xE07020, 0xFFFFFF),
        16:   (0xE85D20, 0xFFFFFF),
        32:   (0xE84420, 0xFFFFFF),
        64:   (0xE82C20, 0xFFFFFF),
        128:  (0xEDCF72, 0x1A1A2E),
        256:  (0xEDCC61, 0x1A1A2E),
        512:  (0xEDC850, 0x1A1A2E),
        1024: (0xEDC53F, 0x1A1A2E),
        2048: (0xEDC22E, 0x1A1A2E),
    }

    def _create_content(self):
        base_y = self.content_y
        grid_total = self.SIZE * self.CELL + (self.SIZE + 1) * self.GAP  # 212
        grid_x = (self._sw - grid_total) // 2
        grid_y = base_y + (self.content_h - grid_total) // 2

        # -- 分数栏 --
        self._score_lbl = lv.label(self.screen)
        self._score_lbl.set_text("Score: 0")
        self._score_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._score_lbl.set_pos(10, base_y + 4)
        self._refs.append(self._score_lbl)

        self._best_lbl = lv.label(self.screen)
        self._best_lbl.set_text("Best: 0")
        self._best_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._best_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._best_lbl.set_pos(self._sw - 75, base_y + 4)
        self._refs.append(self._best_lbl)

        # -- 网格背景 --
        bg = lv.obj(self.screen)
        bg.remove_style_all()
        bg.set_size(grid_total, grid_total)
        bg.set_pos(grid_x, grid_y)
        bg.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        bg.set_style_bg_opa(lv.OPA.COVER, 0)
        bg.set_style_radius(6, 0)
        bg.add_flag(lv.obj.FLAG.CLICKABLE)
        bg.clear_flag(lv.obj.FLAG.SCROLLABLE)
        bg.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(bg)

        # -- 4x4 格子 --
        self._cells = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._labels = [[None] * self.SIZE for _ in range(self.SIZE)]
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                x = grid_x + self.GAP + c * (self.CELL + self.GAP)
                y = grid_y + self.GAP + r * (self.CELL + self.GAP)

                cell = lv.obj(self.screen)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(x, y)
                cell.set_style_bg_color(lv.color_hex(0x2C2C46), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(4, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)
                self._cells[r][c] = cell

                lbl = lv.label(cell)
                lbl.set_text("")
                lbl.set_style_text_font(lv.font_montserrat_14, 0)
                lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                lbl.center()
                self._labels[r][c] = lbl

                self._refs.extend((cell, lbl))

        # -- 遮罩 --
        pw, ph = 160, 50
        panel = lv.obj(bg)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((grid_total - pw) // 2, (grid_total - ph) // 2)
        panel.set_style_bg_color(lv.color_hex(0x000000), 0)
        panel.set_style_bg_opa(lv.OPA._60, 0)
        panel.set_style_radius(8, 0)
        panel.clear_flag(lv.obj.FLAG.CLICKABLE)
        self._refs.append(panel)
        self._panel = panel

        self._overlay = lv.label(panel)
        self._overlay.set_text("Tap to Start")
        self._overlay.set_style_text_font(lv.font_montserrat_14, 0)
        self._overlay.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._overlay.center()
        self._refs.append(self._overlay)

        # -- 状态 --
        self._grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self._score = 0
        self._best = 0
        self._state = "WAITING"
        self._touch_start = None

    # ---------- 游戏逻辑 ----------

    def _start_game(self):
        self._grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self._score = 0
        self._state = "PLAYING"
        self._spawn()
        self._spawn()
        self._render_all()
        self._update_score()
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")

    def _spawn(self):
        """随机空位生成 2(90%) 或 4(10%)。"""
        import urandom
        empty = [(r, c) for r in range(self.SIZE)
                 for c in range(self.SIZE) if self._grid[r][c] == 0]
        if not empty:
            return
        r, c = empty[urandom.getrandbits(8) % len(empty)]
        self._grid[r][c] = 2 if urandom.getrandbits(8) % 10 != 0 else 4

    def _slide_row_left(self, row):
        """左滑一行，返回 (新行, 得分)。"""
        # 去零压缩
        nums = [x for x in row if x != 0]
        # 合并
        merged = []
        score = 0
        skip = False
        for i in range(len(nums)):
            if skip:
                skip = False
                continue
            if i + 1 < len(nums) and nums[i] == nums[i + 1]:
                val = nums[i] * 2
                merged.append(val)
                score += val
                skip = True
            else:
                merged.append(nums[i])
        # 补零
        merged += [0] * (self.SIZE - len(merged))
        return merged, score

    def _move(self, direction):
        """执行移动。direction: 0=左 1=右 2=上 3=下。"""
        old = [row[:] for row in self._grid]
        total_score = 0

        if direction == 0:  # 左
            for r in range(self.SIZE):
                self._grid[r], s = self._slide_row_left(self._grid[r])
                total_score += s
        elif direction == 1:  # 右
            for r in range(self.SIZE):
                rev = self._grid[r][::-1]
                self._grid[r], s = self._slide_row_left(rev)
                self._grid[r] = self._grid[r][::-1]
                total_score += s
        elif direction == 2:  # 上
            for c in range(self.SIZE):
                col = [self._grid[r][c] for r in range(self.SIZE)]
                new_col, s = self._slide_row_left(col)
                total_score += s
                for r in range(self.SIZE):
                    self._grid[r][c] = new_col[r]
        elif direction == 3:  # 下
            for c in range(self.SIZE):
                col = [self._grid[r][c] for r in range(self.SIZE)][::-1]
                new_col, s = self._slide_row_left(col)
                new_col.reverse()
                total_score += s
                for r in range(self.SIZE):
                    self._grid[r][c] = new_col[r]

        # 是否有变化
        if self._grid == old:
            return

        self._score += total_score
        self._spawn()
        self._render_all()
        self._update_score()

        # 检查胜负
        if self._check_win():
            self._state = "WON"
            self._panel.set_style_bg_opa(lv.OPA._60, 0)
            self._overlay.set_text("You Win! 2048\nTap to continue")
            self._overlay.center()
        elif self._check_game_over():
            self._state = "GAME_OVER"
            self._panel.set_style_bg_opa(lv.OPA._60, 0)
            self._overlay.set_text(
                "Game Over!\nScore: {}\nTap to restart".format(self._score))
            self._overlay.center()

    def _check_win(self):
        return any(self._grid[r][c] == 2048
                   for r in range(self.SIZE) for c in range(self.SIZE))

    def _check_game_over(self):
        # 有空位就没结束
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self._grid[r][c] == 0:
                    return False
        # 有相邻相同就没结束
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                v = self._grid[r][c]
                if c + 1 < self.SIZE and self._grid[r][c + 1] == v:
                    return False
                if r + 1 < self.SIZE and self._grid[r + 1][c] == v:
                    return False
        return True

    # ---------- 渲染 ----------

    def _render_all(self):
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                v = self._grid[r][c]
                bg_col, txt_col = self.TILE_COLORS.get(
                    v, (0x00E676, 0x000000))
                self._cells[r][c].set_style_bg_color(lv.color_hex(bg_col), 0)
                if v and self.SHOW_NUMBERS:
                    self._labels[r][c].set_text(str(v))
                    self._labels[r][c].set_style_text_color(
                        lv.color_hex(txt_col), 0)
                else:
                    self._labels[r][c].set_text("")

    def _update_score(self):
        self._score_lbl.set_text("Score: {}".format(self._score))
        if self._score > self._best:
            self._best = self._score
        self._best_lbl.set_text("Best: {}".format(self._best))

    # ---------- 触摸输入 ----------

    def _get_touch_pos(self):
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

        # 点击 -> 开始 / 继续 / 重启
        if self._state == "WAITING":
            self._start_game()
            return
        if self._state == "WON":
            # 继续玩
            self._state = "PLAYING"
            self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
            self._overlay.set_text("")
            return
        if self._state == "GAME_OVER":
            self._start_game()
            return

        # 滑动 -> 移动
        if self._state == "PLAYING" and self._touch_start:
            pos = self._get_touch_pos()
            if not pos:
                return
            dx = pos[0] - self._touch_start[0]
            dy = pos[1] - self._touch_start[1]
            if abs(dx) < 15 and abs(dy) < 15:
                return
            if abs(dx) > abs(dy):
                self._move(0 if dx < 0 else 1)
            else:
                self._move(2 if dy < 0 else 3)


