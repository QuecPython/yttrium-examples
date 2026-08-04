# Yttrium Demo — auto‑split from yttrium.py
import utime
import _thread
import lvgl as lv
from app_base import AppPage

class TetrisPage(AppPage):
    """俄罗斯方块 -- 10x20 网格，触摸滑动操控。"""

    CELL = 14
    COLS = 10
    ROWS = 20
    GAME_X = 2          # 游戏区 X 偏移（容器内）
    GAME_Y = 3          # 游戏区 Y 偏移（容器内）
    BASE_TICK = 500
    COL_EMPTY = 0x16213E

    # 7 种方块: (矩阵, 颜色)
    SHAPES = (
        ([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], 0x00BCD4),  # I 青
        ([[1,1],[1,1]],                              0xFFEB3B),  # O 黄
        ([[0,1,0],[1,1,1],[0,0,0]],                  0x9C27B0),  # T 紫
        ([[0,1,1],[1,1,0],[0,0,0]],                  0x4CAF50),  # S 绿
        ([[1,1,0],[0,1,1],[0,0,0]],                  0xFF5252),  # Z 红
        ([[1,0,0],[1,1,1],[0,0,0]],                  0xFF9800),  # L 橙
        ([[0,0,1],[1,1,1],[0,0,0]],                  0x2196F3),  # J 蓝
    )

    # 消行计分: 0行=0, 1行=100, 2行=300, 3行=500, 4行=800
    LINE_SCORES = (0, 100, 300, 500, 800)

    def _create_content(self):
        base_y = self.content_y

        # -- 游戏区容器（板子 + 右侧信息栏 整体水平居中于内容区宽度）--
        board_w = self.COLS * self.CELL + 4
        board_h = self.ROWS * self.CELL + 6
        info_w = 4 * self.CELL + 24
        left = (self._sw - (board_w + 12 + info_w)) // 2
        if left < 2:
            left = 2

        gc = lv.obj(self.screen)
        gc.remove_style_all()
        gc.set_size(board_w, board_h)
        gc.set_pos(left, base_y)
        gc.set_style_bg_color(lv.color_hex(0x0F3460), 0)
        gc.set_style_bg_opa(lv.OPA.COVER, 0)
        gc.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        gc.set_style_pad_all(0, 0)
        gc.clear_flag(lv.obj.FLAG.SCROLLABLE)
        gc.add_flag(lv.obj.FLAG.CLICKABLE)
        gc.add_event_cb(self._on_touch, lv.EVENT.ALL, None)
        self._refs.append(gc)
        self._gc = gc

        # -- 游戏区网格 10x20 --
        self._cells = []
        for r in range(self.ROWS):
            row = []
            for c in range(self.COLS):
                cell = lv.obj(gc)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(self.GAME_X + c * self.CELL,
                             self.GAME_Y + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                cell.clear_flag(lv.obj.FLAG.CLICKABLE)
                row.append(cell)
                self._refs.append(cell)
            self._cells.append(row)

        # -- 信息栏（右侧）--
        info_x = left + board_w + 12

        # "Next" 标签
        lbl_next = lv.label(self.screen)
        lbl_next.set_text("Next:")
        lbl_next.set_style_text_font(lv.font_montserrat_14, 0)
        lbl_next.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        lbl_next.set_pos(info_x, base_y + 4)
        self._refs.append(lbl_next)

        # 预览区 4x4 网格
        pv_ox = info_x + 8
        pv_oy = base_y + 22
        self._pv_cells = []
        for r in range(4):
            for c in range(4):
                cell = lv.obj(self.screen)
                cell.remove_style_all()
                cell.set_size(self.CELL, self.CELL)
                cell.set_pos(pv_ox + c * self.CELL, pv_oy + r * self.CELL)
                cell.set_style_bg_color(lv.color_hex(self.COL_EMPTY), 0)
                cell.set_style_bg_opa(lv.OPA.COVER, 0)
                cell.set_style_radius(1, 0)
                self._pv_cells.append(cell)
                self._refs.append(cell)

        # 分数 / 消行 / 等级（排在预览下方）
        info_y = pv_oy + 4 * self.CELL + 10
        self._score_lbl = lv.label(self.screen)
        self._score_lbl.set_text("Score: 0")
        self._score_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._score_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._score_lbl.set_pos(info_x, info_y)
        self._refs.append(self._score_lbl)

        self._lines_lbl = lv.label(self.screen)
        self._lines_lbl.set_text("Lines: 0")
        self._lines_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._lines_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._lines_lbl.set_pos(info_x, info_y + 20)
        self._refs.append(self._lines_lbl)

        self._level_lbl = lv.label(self.screen)
        self._level_lbl.set_text("Level: 1")
        self._level_lbl.set_style_text_font(lv.font_montserrat_14, 0)
        self._level_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self._level_lbl.set_pos(info_x, info_y + 40)
        self._refs.append(self._level_lbl)

        # -- 提示遮罩（铺满板子宽度，竖直居中）--
        pw, ph = board_w, 60
        panel = lv.obj(gc)
        panel.remove_style_all()
        panel.set_size(pw, ph)
        panel.set_pos((board_w - pw) // 2, (board_h - ph) // 2)
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

        # -- 游戏状态 --
        self._state = "WAITING"
        self._board = [[0] * self.COLS for _ in range(self.ROWS)]
        self._piece = None
        self._next_idx = 0
        self._bag = []
        self._score = 0
        self._lines = 0
        self._level = 1
        self._running = False
        self._touch_start = None
        # tick 用 lv.timer 驱动（回调在 task_handler/主线程里执行），不再开子线程碰 LVGL
        self._tick_timer = lv.timer_create(self._on_tick, self.BASE_TICK, None)

    # ---------- 方块逻辑 ----------

    def _rot_matrix(self, mat):
        """顺时针旋转矩阵。"""
        rows = len(mat)
        cols = len(mat[0])
        return [[mat[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]

    def _get_shape(self, idx, rot):
        """获取第 idx 种方块旋转 rot 次后的矩阵和颜色。"""
        mat, color = self.SHAPES[idx]
        for _ in range(rot % 4):
            mat = self._rot_matrix(mat)
        return mat, color

    def _bag_next(self):
        """7-bag 随机发生器。"""
        import urandom
        if not self._bag:
            self._bag = list(range(7))
            # Fisher-Yates shuffle
            for i in range(6, 0, -1):
                j = urandom.getrandbits(8) % (i + 1)
                self._bag[i], self._bag[j] = self._bag[j], self._bag[i]
        return self._bag.pop()

    def _cell_coords(self, mat, px, py):
        """返回方块占用的 (col, row) 列表。"""
        coords = []
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    coords.append((px + c, py + r))
        return coords

    def _fits(self, mat, px, py):
        """检查方块在 (px, py) 是否合法。"""
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = px + c, py + r
                    if x < 0 or x >= self.COLS or y >= self.ROWS:
                        return False
                    if y >= 0 and self._board[y][x]:
                        return False
        return True

    # ---------- 游戏控制 ----------

    def _start_game(self):
        self._board = [[0] * self.COLS for _ in range(self.ROWS)]
        self._score = 0
        self._lines = 0
        self._level = 1
        self._bag = []
        self._render_board()

        self._next_idx = self._bag_next()
        self._spawn_piece()

        self._state = "PLAYING"
        self._panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._overlay.set_text("")
        self._update_info()

        self._running = True
        # tick 由 lv.timer 驱动（主线程），不再开子线程
        if self._tick_timer:
            self._tick_timer.set_period(self._tick_period())

    def _spawn_piece(self):
        idx = self._next_idx
        self._next_idx = self._bag_next()
        mat, color = self._get_shape(idx, 0)
        px = (self.COLS - len(mat[0])) // 2
        py = 0
        # 如果顶部放不下，游戏结束
        if not self._fits(mat, px, py):
            self._end_game()
            return
        self._piece = {'idx': idx, 'rot': 0, 'x': px, 'y': py}
        self._render_piece()
        self._render_preview()

    def _move(self, dx, dy):
        if not self._piece or self._state != "PLAYING":
            return False
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        if self._fits(mat, p['x'] + dx, p['y'] + dy):
            self._clear_piece()
            p['x'] += dx
            p['y'] += dy
            self._render_piece()
            return True
        return False

    def _rotate_piece(self):
        if not self._piece or self._state != "PLAYING":
            return
        p = self._piece
        new_rot = (p['rot'] + 1) % 4
        mat, _ = self._get_shape(p['idx'], new_rot)
        # 尝试原位、左移1、右移1、上移1（wall kick）
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]:
            if self._fits(mat, p['x'] + dx, p['y'] + dy):
                self._clear_piece()
                p['rot'] = new_rot
                p['x'] += dx
                p['y'] += dy
                self._render_piece()
                return

    def _hard_drop(self):
        if not self._piece:
            return
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        dy = 0
        while self._fits(mat, p['x'], p['y'] + dy + 1):
            dy += 1
        self._clear_piece()
        p['y'] += dy
        self._render_piece()
        self._score += dy * 2  # 硬降加分
        self._lock()

    def _lock(self):
        """锁定当前方块到 board，检查消行。"""
        p = self._piece
        mat, color = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    bx, by = p['x'] + c, p['y'] + r
                    if 0 <= by < self.ROWS and 0 <= bx < self.COLS:
                        self._board[by][bx] = color

        self._piece = None
        cleared = self._clear_lines()
        if cleared:
            self._lines += cleared
            self._score += self.LINE_SCORES[min(cleared, 4)] * self._level
            self._level = self._lines // 10 + 1
            self._update_info()
            self._render_board()

        self._spawn_piece()

    def _clear_lines(self):
        """消除满行，返回消除行数。"""
        full = [r for r in range(self.ROWS)
                if all(self._board[r][c] for c in range(self.COLS))]
        if not full:
            return 0
        for r in sorted(full):
            del self._board[r]
            self._board.insert(0, [0] * self.COLS)
        return len(full)

    # ---------- 渲染 ----------

    def _render_board(self):
        for r in range(self.ROWS):
            for c in range(self.COLS):
                col = self._board[r][c] or self.COL_EMPTY
                self._cells[r][c].set_style_bg_color(lv.color_hex(col), 0)

    def _render_piece(self):
        if not self._piece:
            return
        p = self._piece
        mat, color = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = p['x'] + c, p['y'] + r
                    if 0 <= y < self.ROWS and 0 <= x < self.COLS:
                        self._cells[y][x].set_style_bg_color(
                            lv.color_hex(color), 0)

    def _clear_piece(self):
        if not self._piece:
            return
        p = self._piece
        mat, _ = self._get_shape(p['idx'], p['rot'])
        for r in range(len(mat)):
            for c in range(len(mat[0])):
                if mat[r][c]:
                    x, y = p['x'] + c, p['y'] + r
                    if 0 <= y < self.ROWS and 0 <= x < self.COLS:
                        col = self._board[y][x] or self.COL_EMPTY
                        self._cells[y][x].set_style_bg_color(
                            lv.color_hex(col), 0)

    def _render_preview(self):
        mat, color = self._get_shape(self._next_idx, 0)
        # 居中预览
        ox = (4 - len(mat[0])) // 2
        oy = (4 - len(mat)) // 2
        for r in range(4):
            for c in range(4):
                idx = r * 4 + c
                mr, mc = r - oy, c - ox
                if 0 <= mr < len(mat) and 0 <= mc < len(mat[0]) and mat[mr][mc]:
                    self._pv_cells[idx].set_style_bg_color(
                        lv.color_hex(color), 0)
                else:
                    self._pv_cells[idx].set_style_bg_color(
                        lv.color_hex(self.COL_EMPTY), 0)

    def _update_info(self):
        self._score_lbl.set_text("Score: {}".format(self._score))
        self._lines_lbl.set_text("Lines: {}".format(self._lines))
        self._level_lbl.set_text("Level: {}".format(self._level))

    # ---------- 游戏循环 ----------

    def _tick_period(self):
        return max(100, self.BASE_TICK - (self._level - 1) * 50)

    def _on_tick(self, timer):
        """lv.timer 回调（跑在主线程 task_handler 里）：每次下一格，碰底锁定；顺手按等级刷新周期。"""
        try:
            if self._state == "PLAYING" and self._piece:
                if not self._move(0, 1):
                    self._lock()
            timer.set_period(self._tick_period())
        except Exception as e:
            print("[TETRIS] tick error:", e)

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

        if code == lv.EVENT.RELEASED:
            if self._state in ("WAITING", "GAME_OVER"):
                self._start_game()
                return

            if self._state == "PLAYING" and self._touch_start:
                pos = self._get_touch_pos()
                if not pos:
                    return
                dx = pos[0] - self._touch_start[0]
                dy = pos[1] - self._touch_start[1]
                if abs(dx) < 10 and abs(dy) < 10:
                    self._rotate_piece()  # 点击 -> 旋转
                    return
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self._move(1, 0)
                    else:
                        self._move(-1, 0)
                else:
                    if dy > 20:
                        self._hard_drop()  # 长下滑 -> 硬降
                    else:
                        self._move(0, 1)
            return

        if code == lv.EVENT.PRESSING and self._state == "PLAYING":
            # 长按下 -> 软降加速
            pos = self._get_touch_pos()
            if pos and self._touch_start:
                dy = pos[1] - self._touch_start[1]
                if dy > 30:
                    self._move(0, 1)

    # ---------- 退出清理 ----------

    def _on_back(self, e=None):
        print("[TETRIS] cleaning up...")
        self._running = False
        self._state = "GAME_OVER"
        utime.sleep_ms(self.BASE_TICK + 20)
        super()._on_back(e)


