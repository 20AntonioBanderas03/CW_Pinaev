import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button


def solve_k_queens(n, k, obstacles):
    solutions = []
    board = [-1] * k

    def is_safe(row, col):
        if (row, col) in obstacles:
            return False
        for prev_row in range(row):
            prev_col = board[prev_row]
            if prev_col == col:
                return False
            if abs(prev_col - col) == abs(prev_row - row):
                return False
        return True

    def backtrack(row):
        if row == k:
            solutions.append(board.copy())
            return
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1)

    backtrack(0)
    return solutions


class KQueensVisualizer:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.obstacles = set()
        self.selected_queen = None
        self.current_idx = 0

        print("Считаем решения...")
        self.solutions = solve_k_queens(n, k, set())
        self.total = len(self.solutions)

        print(f"Найдено {self.total} решений")

        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        plt.subplots_adjust(bottom=0.18)

        self.update_window_title()
        self.create_buttons()

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        self.update_display()

    def update_window_title(self):
        if self.total > 0:
            self.fig.canvas.manager.set_window_title(
                f"Задача о {self.k} ферзях - Решение {self.current_idx + 1} из {self.total}"
            )
        else:
            self.fig.canvas.manager.set_window_title(
                "Задача о {self.k} ферзях - НЕТ РЕШЕНИЙ"
            )

    def create_buttons(self):
        button_width = 0.12
        button_height = 0.05
        spacing = 0.02
        center_x = 0.5
        nav_y = 0.12

        first_x = center_x - 2 * button_width - 1.5 * spacing
        prev_x = center_x - button_width - 0.5 * spacing
        next_x = center_x + 0.5 * spacing
        last_x = center_x + button_width + 1.5 * spacing

        ax_first = plt.axes([first_x, nav_y, button_width, button_height])
        ax_prev = plt.axes([prev_x, nav_y, button_width, button_height])
        ax_next = plt.axes([next_x, nav_y, button_width, button_height])
        ax_last = plt.axes([last_x, nav_y, button_width, button_height])
        ax_clear = plt.axes([center_x - 0.1, 0.05, 0.2, 0.04])

        self.btn_first = Button(ax_first, '← Первое')
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперёд >')
        self.btn_last = Button(ax_last, 'Последнее →')
        self.btn_clear = Button(ax_clear, 'Очистить препятствия')

        self.btn_first.on_clicked(self.first_solution)
        self.btn_prev.on_clicked(self.prev_solution)
        self.btn_next.on_clicked(self.next_solution)
        self.btn_last.on_clicked(self.last_solution)
        self.btn_clear.on_clicked(self.clear_obstacles)

    def get_moves_for_queen(self, row, col):
        moves = set()
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < self.n and 0 <= c < self.n:
                if (r, c) in self.obstacles:
                    break
                moves.add((r, c))
                r += dr
                c += dc

        return moves

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        col = int(round(event.xdata))
        row = int(round(event.ydata))

        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        if event.button == 3 and self.solutions:
            board = self.solutions[self.current_idx]
            for r in range(len(board)):
                if board[r] == col and r == row:
                    if self.selected_queen == (r, col):
                        self.selected_queen = None
                    else:
                        self.selected_queen = (r, col)
                    self.update_display()
                    return

        if event.button == 1:
            self.selected_queen = None

            if (row, col) in self.obstacles:
                self.obstacles.remove((row, col))
            else:
                self.obstacles.add((row, col))

            self.recalculate()

    def recalculate(self):
        self.solutions = solve_k_queens(self.n, self.k, self.obstacles)
        self.total = len(self.solutions)
        self.current_idx = 0
        self.update_display()

    def clear_obstacles(self, event):
        self.obstacles.clear()
        self.selected_queen = None
        self.solutions = solve_k_queens(self.n, self.k, set())
        self.total = len(self.solutions)
        self.current_idx = 0
        self.update_display()

    def draw_board(self, board):
        self.ax.clear()
        n = self.n

        board_matrix = np.zeros((n, n))
        for r in range(n):
            for c in range(n):
                board_matrix[r, c] = (r + c) % 2

        cmap = plt.matplotlib.colors.ListedColormap(['#8B4513', '#F0D9B5'])
        self.ax.imshow(board_matrix, cmap=cmap,
                       extent=[-0.5, n - 0.5, n - 0.5, -0.5])

        if self.selected_queen:
            moves = self.get_moves_for_queen(*self.selected_queen)
            for (r, c) in moves:
                rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                     color='orange', alpha=0.3, zorder=1)
                self.ax.add_patch(rect)

                dot = plt.Circle((c, r), 0.12,
                                 color='blue', zorder=3)
                self.ax.add_patch(dot)

        for (row, col) in self.obstacles:
            rect = plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                 color='gray', alpha=0.7, zorder=2)
            self.ax.add_patch(rect)

        if board:
            for r in range(len(board)):
                c = board[r]
                color = 'blue' if self.selected_queen == (r, c) else 'red'

                self.ax.text(
                    c, r, '♕',
                    ha='center',
                    va='center',
                    fontsize=max(10, 300 // n),
                    color=color,
                    fontweight='bold',
                    zorder=5
                )

        if self.total > 0:
            text = f"Решение {self.current_idx + 1} из {self.total}"
        else:
            text = "НЕТ РЕШЕНИЙ"

        self.ax.text(n / 2, -1.8, text,
                     ha='center', va='top',
                     fontsize=14,
                     fontweight='bold',
                     bbox=dict(boxstyle='round',
                               facecolor='lightyellow',
                               alpha=0.9))

        border = plt.Rectangle((-0.5, -0.5), n, n,
                               fill=False, edgecolor='black', linewidth=3)
        self.ax.add_patch(border)

        self.ax.set_xlim(-1.5, n + 0.5)
        self.ax.set_ylim(n + 0.5, -2.2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.update_window_title()
        self.fig.canvas.draw_idle()

    def update_display(self):
        if self.solutions:
            board = self.solutions[self.current_idx]
        else:
            board = None
        self.draw_board(board)

    def prev_solution(self, event):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.selected_queen = None
            self.update_display()

    def next_solution(self, event):
        if self.current_idx < self.total - 1:
            self.current_idx += 1
            self.selected_queen = None
            self.update_display()

    def first_solution(self, event):
        self.current_idx = 0
        self.update_display()

    def last_solution(self, event):
        self.current_idx = self.total - 1
        self.update_display()


if __name__ == "__main__":
    print("Задача K-ферзей\n")

    try:
        n = int(input("Введите размер доски N: "))
        k = int(input("Введите количество ферзей K: "))
    except:
        n, k = 8, 8

    if k > n:
        k = n

    viz = KQueensVisualizer(n, k)
    plt.show()