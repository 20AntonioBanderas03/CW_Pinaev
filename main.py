import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from itertools import combinations


def is_safe_position(queens, obstacles, n):
    """Проверяет, что ферзи не бьют друг друга и не стоят на препятствиях"""
    for i, (r1, c1) in enumerate(queens):
        if (r1, c1) in obstacles:
            return False
        for j, (r2, c2) in enumerate(queens):
            if i != j:
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    return False
    return True


def get_attacked_cells(queens, obstacles, n):
    """Возвращает множество клеток, атакуемых ферзями (включая их позиции)"""
    attacked = set()
    for r, c in queens:
        attacked.add((r, c))
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < n and 0 <= nc < n:
                if (nr, nc) in obstacles:
                    break
                attacked.add((nr, nc))
                nr += dr
                nc += dc
    return attacked


def find_min_dominating_queens(n, obstacles):
    """Находит минимальное количество ферзей, покрывающих всю доску"""
    all_cells = {(r, c) for r in range(n) for c in range(n) if (r, c) not in obstacles}
    
    if not all_cells:
        return [], 0
    
    for k in range(1, n * n + 1):
        available_positions = [(r, c) for r in range(n) for c in range(n) 
                               if (r, c) not in obstacles]
        
        solutions_for_k = []
        for positions in combinations(available_positions, k):
            if not is_safe_position(positions, obstacles, n):
                continue
            
            attacked = get_attacked_cells(positions, obstacles, n)
            if all_cells.issubset(attacked):
                solutions_for_k.append([[r, c] for r, c in positions])
        
        if solutions_for_k:
            return solutions_for_k, k
    
    return [], -1


class KQueensVisualizer:
    def __init__(self, n, k=None):
        self.n = n
        self.k = k
        self.active_obstacles = set()  # активные препятствия (после поиска)
        self.temp_obstacles = set()    # временные препятствия для ДОБАВЛЕНИЯ (светло-серые)
        self.delete_obstacles = set()  # препятствия для УДАЛЕНИЯ (с красным крестиком)
        self.selected_queen = None
        self.current_idx = 0
        self.check_mode = False
        self.highlighted_queens = set()
        self.solutions = []
        self.total = 0
        self.min_queens = 0
        self.has_changes = False

        # Создаем окно и оси
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        plt.subplots_adjust(bottom=0.18)
        
        # Создаем кнопки
        self.create_buttons()
        
        # Подключаем обработчик кликов
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.find_solution(None)

    def update_window_title(self):
        if self.total > 0:
            title = f"Минимальное покрытие доски {self.n}x{self.n} - {self.min_queens} ферзей - Решение {self.current_idx + 1} из {self.total}"
            if self.check_mode:
                title += f" [Режим проверки: подсвечено {len(self.highlighted_queens)} ферзей]"
            if self.has_changes:
                title += " [Есть изменения! Нажмите 'Найти решение']"
            self.fig.canvas.manager.set_window_title(title)
        else:
            title = f"Покрытие доски {self.n}x{self.n} - НЕТ РЕШЕНИЙ"
            if self.has_changes:
                title += " [Есть изменения! Нажмите 'Найти решение']"
            self.fig.canvas.manager.set_window_title(title)

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
        ax_clear = plt.axes([center_x - 0.28, 0.05, 0.14, 0.04])
        ax_find = plt.axes([center_x - 0.12, 0.05, 0.14, 0.04])
        ax_check = plt.axes([center_x + 0.04, 0.05, 0.14, 0.04])

        self.btn_first = Button(ax_first, '← Первое')
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперёд >')
        self.btn_last = Button(ax_last, 'Последнее →')
        self.btn_clear = Button(ax_clear, 'Очистить всё')
        self.btn_find = Button(ax_find, '⟳ Найти решение')
        self.btn_check = Button(ax_check, 'Проверить ходы')

        self.btn_first.on_clicked(self.first_solution)
        self.btn_prev.on_clicked(self.prev_solution)
        self.btn_next.on_clicked(self.next_solution)
        self.btn_last.on_clicked(self.last_solution)
        self.btn_clear.on_clicked(self.clear_all)
        self.btn_find.on_clicked(self.find_solution)
        self.btn_check.on_clicked(self.toggle_check_mode)

    def toggle_check_mode(self, event):
        """Включение/выключение режима проверки ходов"""
        self.check_mode = not self.check_mode
        if not self.check_mode:
            self.highlighted_queens.clear()
        self.selected_queen = None
        self.update_display()

    def get_moves_for_queen(self, row, col, use_temp_obstacles=False):
        moves = set()
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        # Выбираем, какие препятствия использовать
        obstacles = self.temp_obstacles if use_temp_obstacles else self.active_obstacles

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < self.n and 0 <= c < self.n:
                if (r, c) in obstacles:
                    break
                moves.add((r, c))
                r += dr
                c += dc

        return moves

    def get_color_for_queen(self, index):
        """Возвращает цвет для ферзя по его индексу"""
        colors = [
            '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
            '#9B59B6', '#1ABC9C', '#E67E22', '#1F618D',
            '#C0392B', '#27AE60', '#D35400', '#8E44AD'
        ]
        return colors[index % len(colors)]

    def draw_obstacle(self, row, col, is_temp=False, is_delete=False):
        """Рисует препятствие с крестиком"""
        if is_delete:
            # Препятствие на удаление - красный крестик поверх активного фона
            color = 'gray'
            alpha = 0.7
            cross_color = 'red'
            line_width = 3
            # Не рисуем пунктирную рамку для удаления
            rect = plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                 color=color, alpha=alpha, zorder=3)
            self.ax.add_patch(rect)
            
            # Большой красный крестик
            self.ax.plot([col - 0.4, col + 0.4], [row - 0.4, row + 0.4],
                        color=cross_color, linewidth=line_width, zorder=5)
            self.ax.plot([col + 0.4, col - 0.4], [row - 0.4, row + 0.4],
                        color=cross_color, linewidth=line_width, zorder=5)
        elif is_temp:
            # Новое препятствие для добавления - светло-серое с серым крестиком
            color = 'lightgray'
            alpha = 0.5
            rect = plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                 color=color, alpha=alpha, zorder=3)
            self.ax.add_patch(rect)
            
            # Серый крестик
            self.ax.plot([col - 0.35, col + 0.35], [row - 0.35, row + 0.35],
                        color='gray', linewidth=2, zorder=4)
            self.ax.plot([col + 0.35, col - 0.35], [row - 0.35, row + 0.35],
                        color='gray', linewidth=2, zorder=4)
            
            # Пунктирная рамка
            self.ax.plot([col - 0.45, col + 0.45], [row - 0.45, row - 0.45],
                        'gray', linewidth=1, linestyle='--', zorder=3)
            self.ax.plot([col + 0.45, col - 0.45], [row - 0.45, row - 0.45],
                        'gray', linewidth=1, linestyle='--', zorder=3)
            self.ax.plot([col - 0.45, col + 0.45], [row + 0.45, row + 0.45],
                        'gray', linewidth=1, linestyle='--', zorder=3)
            self.ax.plot([col + 0.45, col - 0.45], [row + 0.45, row + 0.45],
                        'gray', linewidth=1, linestyle='--', zorder=3)
        else:
            # Активное препятствие - серое с белым крестиком
            color = 'gray'
            alpha = 0.7
            rect = plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                 color=color, alpha=alpha, zorder=3)
            self.ax.add_patch(rect)
            
            # Белый крестик
            self.ax.plot([col - 0.35, col + 0.35], [row - 0.35, row + 0.35],
                        color='white', linewidth=2, zorder=4)
            self.ax.plot([col + 0.35, col - 0.35], [row - 0.35, row + 0.35],
                        color='white', linewidth=2, zorder=4)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        col = int(round(event.xdata))
        row = int(round(event.ydata))

        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        # В режиме проверки ходов
        if self.check_mode and self.solutions and not self.has_changes:
            # Проверяем, есть ли ферзь в этой клетке
            for idx, (r, c) in enumerate(self.solutions[self.current_idx]):
                if r == row and c == col:
                    queen_pos = (row, col)
                    if queen_pos in self.highlighted_queens:
                        self.highlighted_queens.discard(queen_pos)
                    else:
                        self.highlighted_queens.add(queen_pos)
                    self.update_display()
                    return
            return

        # Обычный режим: ПКМ - выделение ферзя
        if event.button == 3 and self.solutions and not self.has_changes:
            for idx, (r, c) in enumerate(self.solutions[self.current_idx]):
                if r == row and c == col:
                    if self.selected_queen == (row, col):
                        self.selected_queen = None
                    else:
                        self.selected_queen = (row, col)
                    self.update_display()
                    return

        # Обычный режим: ЛКМ - добавление/удаление препятствий
        if event.button == 1 and not self.check_mode:
            self.selected_queen = None
            self.check_mode = False
            
            # Проверяем, кликнули ли на активное препятствие (помечаем на удаление)
            if (row, col) in self.active_obstacles:
                if (row, col) not in self.delete_obstacles:
                    self.delete_obstacles.add((row, col))
                    self.has_changes = True
                else:
                    # Если уже помечено на удаление, снимаем пометку
                    self.delete_obstacles.discard((row, col))
                    self.has_changes = True
                self.update_display()
                return
            
            # Проверяем, кликнули ли на препятствие, помеченное на удаление
            elif (row, col) in self.delete_obstacles:
                self.delete_obstacles.discard((row, col))
                self.has_changes = True
                self.update_display()
                return
            
            # Проверяем, кликнули ли на временное препятствие (для добавления)
            elif (row, col) in self.temp_obstacles:
                self.temp_obstacles.remove((row, col))
                self.has_changes = True
            else:
                # Добавляем новое препятствие для добавления
                self.temp_obstacles.add((row, col))
                self.has_changes = True
            
            self.update_display()

    def find_solution(self, event):
        """Найти решение с текущими препятствиями"""
        print("Ищем минимальное покрытие доски ферзями...")
        
        # Применяем изменения
        new_active = self.active_obstacles.copy()
        
        # Добавляем новые препятствия
        for obs in self.temp_obstacles:
            new_active.add(obs)
        
        # Удаляем помеченные препятствия
        for obs in self.delete_obstacles:
            new_active.discard(obs)
        
        self.active_obstacles = new_active
        self.temp_obstacles.clear()
        self.delete_obstacles.clear()
        
        self.solutions, self.min_queens = find_min_dominating_queens(self.n, self.active_obstacles)
        self.total = len(self.solutions)
        self.current_idx = 0
        self.check_mode = False
        self.highlighted_queens.clear()
        self.selected_queen = None
        self.has_changes = False
        
        if self.total > 0:
            print(f"Найдено {self.total} решений с {self.min_queens} ферзями")
        else:
            print("Решений не найдено")
        
        self.update_display()

    def clear_all(self, event):
        """Очистить все препятствия и найти решение для пустой доски"""
        self.temp_obstacles.clear()
        self.delete_obstacles.clear()
        self.active_obstacles.clear()
        self.has_changes = True
        self.selected_queen = None
        self.check_mode = False
        self.highlighted_queens.clear()
        
        # Пересчитываем для пустой доски
        self.find_solution(event)

    def draw_board(self, board):
        self.ax.clear()
        n = self.n

        # Рисуем шахматную доску
        board_matrix = np.zeros((n, n))
        for r in range(n):
            for c in range(n):
                board_matrix[r, c] = (r + c) % 2

        cmap = plt.matplotlib.colors.ListedColormap(['#8B4513', '#F0D9B5'])
        self.ax.imshow(board_matrix, cmap=cmap,
                       extent=[-0.5, n - 0.5, n - 0.5, -0.5])

        # Преобразуем board в список координат ферзей
        queens_coords = board if board else []

        # Рисуем зоны атаки всех ферзей (полупрозрачная зеленая заливка)
        if queens_coords and not self.has_changes:
            all_attacked = set()
            for r, c in queens_coords:
                all_attacked.update(self.get_moves_for_queen(r, c, use_temp_obstacles=False))
                all_attacked.add((r, c))
            
            for (r, c) in all_attacked:
                if (r, c) not in queens_coords:
                    rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                         color='lightgreen', alpha=0.2, zorder=1)
                    self.ax.add_patch(rect)

        # Рисуем ходы выделенного ферзя в обычном режиме (ПКМ)
        if self.selected_queen and not self.check_mode and not self.has_changes:
            moves = self.get_moves_for_queen(*self.selected_queen, use_temp_obstacles=False)
            for (r, c) in moves:
                rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                     color='orange', alpha=0.3, zorder=2)
                self.ax.add_patch(rect)
                
                dot = plt.Circle((c, r), 0.12,
                                 color='blue', alpha=0.8, zorder=4)
                self.ax.add_patch(dot)

        # Рисуем ходы подсвеченных ферзей в режиме проверки
        if self.check_mode and self.highlighted_queens and not self.has_changes:
            for highlighted in self.highlighted_queens:
                moves = self.get_moves_for_queen(*highlighted, use_temp_obstacles=False)
                queen_idx = None
                for idx, (r, c) in enumerate(queens_coords):
                    if (r, c) == highlighted:
                        queen_idx = idx
                        break
                
                if queen_idx is not None:
                    queen_color = self.get_color_for_queen(queen_idx)
                    for (r, c) in moves:
                        rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                             color=queen_color, alpha=0.25, zorder=2)
                        self.ax.add_patch(rect)
                        
                        dot = plt.Circle((c, r), 0.12,
                                         color=queen_color, alpha=0.8, zorder=4)
                        self.ax.add_patch(dot)

        # Рисуем активные препятствия (кроме помеченных на удаление)
        for (row, col) in self.active_obstacles:
            if (row, col) not in self.delete_obstacles:
                self.draw_obstacle(row, col, is_temp=False, is_delete=False)
        
        # Рисуем препятствия, помеченные на удаление (красный крестик)
        for (row, col) in self.delete_obstacles:
            self.draw_obstacle(row, col, is_temp=False, is_delete=True)
        
        # Рисуем новые препятствия для добавления (светло-серые)
        for (row, col) in self.temp_obstacles:
            if (row, col) not in self.active_obstacles:
                self.draw_obstacle(row, col, is_temp=True, is_delete=False)

        # Рисуем ферзей
        if queens_coords and not self.has_changes:
            for idx, (r, c) in enumerate(queens_coords):
                if self.selected_queen == (r, c) and not self.check_mode:
                    color = 'blue'
                elif self.check_mode and (r, c) in self.highlighted_queens:
                    color = self.get_color_for_queen(idx)
                elif self.check_mode:
                    color = 'black'
                else:
                    color = 'red'

                if self.check_mode and (r, c) in self.highlighted_queens:
                    self.ax.text(
                        c, r, '♕',
                        ha='center',
                        va='center',
                        fontsize=max(10, 300 // n),
                        color=color,
                        fontweight='bold',
                        zorder=5,
                        bbox=dict(boxstyle='circle', facecolor='white', 
                                 edgecolor=color, linewidth=2, alpha=0.8)
                    )
                else:
                    self.ax.text(
                        c, r, '♕',
                        ha='center',
                        va='center',
                        fontsize=max(10, 300 // n),
                        color=color,
                        fontweight='bold',
                        zorder=5
                    )

        # Текстовая информация
        if self.total > 0 and not self.has_changes:
            # Проверяем, все ли клетки покрыты
            all_cells = {(r, c) for r in range(n) for c in range(n) 
                        if (r, c) not in self.active_obstacles}
            attacked = set()
            for r, c in queens_coords:
                attacked.update(self.get_moves_for_queen(r, c, use_temp_obstacles=False))
                attacked.add((r, c))
            uncovered = all_cells - attacked
            
            if self.check_mode:
                if self.highlighted_queens:
                    text = f"Режим проверки - подсвечено {len(self.highlighted_queens)} ферзей (кликни для добавления/удаления)"
                else:
                    text = f"Режим проверки - кликни на ферзя, чтобы показать его ходы"
            else:
                text = f"Решение {self.current_idx + 1} из {self.total} | Ферзей: {self.min_queens}"
                if uncovered:
                    text += f" | НЕПОКРЫТО: {len(uncovered)} клеток!"
                else:
                    text += " | ✓ ВСЕ КЛЕТКИ ПОКРЫТЫ"
        elif self.has_changes:
            text = "Есть изменения! Нажмите 'Найти решение' для поиска минимального покрытия"
        else:
            text = "НЕТ РЕШЕНИЙ"

        self.ax.text(n / 2, -1.8, text,
                     ha='center', va='top',
                     fontsize=11,
                     fontweight='bold',
                     bbox=dict(boxstyle='round',
                               facecolor='lightyellow',
                               alpha=0.9))

        # Рамка доски
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
        if self.solutions and not self.has_changes:
            board = self.solutions[self.current_idx]
        else:
            board = None
        self.draw_board(board)

    def prev_solution(self, event):
        if self.solutions and not self.has_changes and self.current_idx > 0:
            self.current_idx -= 1
            self.selected_queen = None
            self.highlighted_queens.clear()
            self.update_display()

    def next_solution(self, event):
        if self.solutions and not self.has_changes and self.current_idx < self.total - 1:
            self.current_idx += 1
            self.selected_queen = None
            self.highlighted_queens.clear()
            self.update_display()

    def first_solution(self, event):
        if self.solutions and not self.has_changes:
            self.current_idx = 0
            self.selected_queen = None
            self.highlighted_queens.clear()
            self.update_display()

    def last_solution(self, event):
        if self.solutions and not self.has_changes:
            self.current_idx = self.total - 1
            self.selected_queen = None
            self.highlighted_queens.clear()
            self.update_display()


if __name__ == "__main__":
    print("Задача о минимальном покрытии доски ферзями")
    print("Ферзи не должны бить друг друга, но должны атаковать все клетки доски")
    print()
    
    try:
        n = int(input("Введите размер доски N: "))
    except:
        n = 5
    
    viz = KQueensVisualizer(n)
    plt.show()