import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

# 1. Функция для поиска ВСЕХ решений задачи о восьми ферзях с учетом препятствий
def solve_all_with_obstacles(board, row, solutions, obstacles):
    if row == 8:
        # Сохраняем копию найденного решения
        solutions.append(board.copy())
        return
    for col in range(8):
        # Проверяем, не является ли клетка препятствием
        if (row, col) in obstacles:
            continue
        if is_safe_with_obstacles(board, row, col, obstacles):
            board[row] = col
            solve_all_with_obstacles(board, row + 1, solutions, obstacles)

def is_safe_with_obstacles(board, row, col, obstacles):
    for prev_row in range(row):
        prev_col = board[prev_row]
        if prev_col == col or abs(prev_col - col) == abs(prev_row - row):
            return False
    return True

# 2. Класс для визуализации с возможностью добавления препятствий
class EightQueensVisualizerWithObstacles:
    def __init__(self, solutions):
        self.all_solutions = solutions
        self.current_idx = 0
        self.total = len(solutions)
        self.obstacles = set()  # Множество препятствий (row, col)
        
        # Создаем фигуру с большими размерами
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        plt.subplots_adjust(bottom=0.18)  # Увеличиваем отступ снизу
        
        # Устанавливаем заголовок окна
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
        
        # Создаем кнопки навигации (повыше - y=0.12)
        button_width = 0.12
        button_height = 0.05
        spacing = 0.02
        center_x = 0.5
        nav_y = 0.12  # Кнопки навигации выше
        
        # 4 кнопки навигации: первое, назад, вперед, последнее
        first_x = center_x - 2 * button_width - 1.5 * spacing
        prev_x = center_x - button_width - 0.5 * spacing
        next_x = center_x + 0.5 * spacing
        last_x = center_x + button_width + 1.5 * spacing
        
        ax_first = plt.axes([first_x, nav_y, button_width, button_height])
        ax_prev = plt.axes([prev_x, nav_y, button_width, button_height])
        ax_next = plt.axes([next_x, nav_y, button_width, button_height])
        ax_last = plt.axes([last_x, nav_y, button_width, button_height])
        
        # Кнопка очистки препятствий (ниже, по центру)
        clear_y = 0.05  # Ниже кнопок навигации
        ax_clear = plt.axes([center_x - 0.1, clear_y, 0.2, 0.04])
        
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперед >')
        self.btn_first = Button(ax_first, 'Первое')
        self.btn_last = Button(ax_last, 'Последнее')
        self.btn_clear = Button(ax_clear, 'Очистить препятствия')
        
        # Привязываем обработчики
        self.btn_prev.on_clicked(self.prev_solution)
        self.btn_next.on_clicked(self.next_solution)
        self.btn_first.on_clicked(self.first_solution)
        self.btn_last.on_clicked(self.last_solution)
        self.btn_clear.on_clicked(self.clear_obstacles)
        
        # Привязываем обработчик кликов по доске (автоматический пересчет)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Рисуем доску
        self.update_display()
        
    def on_click(self, event):
        # Проверяем, что клик был по доске (не по кнопкам)
        if event.inaxes == self.ax:
            # Получаем координаты клетки
            col = int(round(event.xdata))
            row = int(round(event.ydata))
            
            # Проверяем, что координаты в пределах доски
            if 0 <= row <= 7 and 0 <= col <= 7:
                # Добавляем или удаляем препятствие
                if (row, col) in self.obstacles:
                    self.obstacles.remove((row, col))
                else:
                    self.obstacles.add((row, col))
                
                # Автоматически пересчитываем решения
                self.recalculate_solutions()
    
    def recalculate_solutions(self):
        """Пересчитывает все решения с учетом текущих препятствий"""
        print("Пересчет решений с учетом препятствий...")
        new_solutions = []
        solve_all_with_obstacles([0] * 8, 0, new_solutions, self.obstacles)
        
        if new_solutions:
            self.all_solutions = new_solutions
            self.total = len(new_solutions)
            self.current_idx = 0
            print(f"Найдено {self.total} решений с учетом препятствий!")
            self.update_display()
        else:
            print("Нет решений с текущими препятствиями!")
            self.all_solutions = []
            self.total = 0
            self.show_no_solutions_message()
    
    def show_no_solutions_message(self):
        """Показывает сообщение об отсутствии решений"""
        self.ax.clear()
        
        # Создаем шахматную доску
        board_matrix = np.zeros((8, 8))
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    board_matrix[r, c] = 1
                else:
                    board_matrix[r, c] = 0
        
        cmap = plt.matplotlib.colors.ListedColormap(['#8B4513', '#F0D9B5'])
        self.ax.imshow(board_matrix, cmap=cmap, extent=[-0.5, 7.5, 7.5, -0.5])
        
        # Рисуем препятствия
        for (row, col) in self.obstacles:
            rect = plt.Rectangle((col-0.5, row-0.5), 1, 1, color='gray', alpha=0.7, zorder=2)
            self.ax.add_patch(rect)
            self.ax.text(col, row, '╳', ha='center', va='center', 
                        fontsize=30, color='black', fontweight='bold', zorder=3)
        
        # Рисуем бордер
        border = plt.Rectangle((-0.5, -0.5), 8, 8, fill=False, 
                              edgecolor='black', linewidth=4)
        self.ax.add_patch(border)
        
        # Подписи
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, col in enumerate(columns):
            self.ax.text(i, -1, col, ha='center', va='top', fontsize=14, fontweight='bold')
            self.ax.text(i, 8.0, col, ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        for i in range(1, 9):
            self.ax.text(-0.75, i-1, str(i), ha='right', va='center', fontsize=14, fontweight='bold')
            self.ax.text(7.76, i-1, str(i), ha='left', va='center', fontsize=14, fontweight='bold')
        
        # Сообщение об отсутствии решений
        self.ax.text(4, 4, 'НЕТ РЕШЕНИЙ!\nУберите некоторые препятствия', 
                    ha='center', va='center', fontsize=20, fontweight='bold',
                    color='red', 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red', linewidth=3))
        
        # Информация о препятствиях
        info_text = f"Препятствий: {len(self.obstacles)}"
        self.ax.text(4, -1.4, info_text, ha='center', va='top', 
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        self.ax.text(4, 8.8, 'Клик по клетке - добавить/убрать препятствие', 
                    ha='center', va='bottom', fontsize=11, style='italic',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        self.ax.set_xlim(-1.5, 9.0)
        self.ax.set_ylim(8.8, -1.6)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title("")
        
        # Обновляем заголовок окна
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - НЕТ РЕШЕНИЙ")
        self.fig.canvas.draw_idle()
    
    def draw_board(self, board):
        # Очищаем ось
        self.ax.clear()
        
        # Создаем шахматную доску (8x8)
        board_matrix = np.zeros((8, 8))
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    board_matrix[r, c] = 1  # Светлые клетки
                else:
                    board_matrix[r, c] = 0  # Темные клетки
        
        # Рисуем доску
        cmap = plt.matplotlib.colors.ListedColormap(['#8B4513', '#F0D9B5'])
        self.ax.imshow(board_matrix, cmap=cmap, extent=[-0.5, 7.5, 7.5, -0.5])
        
        # Рисуем препятствия (серые клетки с крестиками)
        for (row, col) in self.obstacles:
            rect = plt.Rectangle((col-0.5, row-0.5), 1, 1, color='gray', alpha=0.7, zorder=2)
            self.ax.add_patch(rect)
            self.ax.text(col, row, '╳', ha='center', va='center', 
                        fontsize=30, color='black', fontweight='bold', zorder=3)
        
        # Добавляем ферзей
        if board and len(board) == 8:
            for r in range(8):
                c = board[r]
                # Красный кружок
                circle = plt.Circle((c, r), 0.35, color='red', zorder=3, alpha=0.9)
                self.ax.add_patch(circle)
                # Символ ферзя
                self.ax.text(c, r, '♕', ha='center', va='center', 
                            fontsize=28, color='darkred', fontweight='bold', zorder=4)

        # Рисуем бордер (рамку) вокруг доски
        border = plt.Rectangle((-0.5, -0.5), 8, 8, fill=False, 
                              edgecolor='black', linewidth=4)
        self.ax.add_patch(border)
        
        # Добавляем подписи колонок (a, b, c, d, e, f, g, h)
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, col in enumerate(columns):
            self.ax.text(i, -1, col, ha='center', va='top', fontsize=14, fontweight='bold')
            self.ax.text(i, 8.0, col, ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        # Добавляем подписи строк (1, 2, 3, 4, 5, 6, 7, 8)
        for i in range(1, 9):
            self.ax.text(-0.75, i-1, str(i), ha='right', va='center', fontsize=14, fontweight='bold')
            self.ax.text(7.76, i-1, str(i), ha='left', va='center', fontsize=14, fontweight='bold')
        
        # Добавляем информацию о количестве препятствий
        if self.obstacles:
            info_text = f"Препятствий: {len(self.obstacles)} | Решение {self.current_idx + 1} из {self.total}"
        else:
            info_text = f"Нет препятствий | Решение {self.current_idx + 1} из {self.total}"
        
        self.ax.text(4, -2.4, info_text, ha='center', va='top', 
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # Инструкция
        self.ax.text(4, 8.5, 'Клик по клетке - добавить/убрать препятствие', 
                    ha='center', va='bottom', fontsize=11, style='italic',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # Настройка отображения
        self.ax.set_xlim(-1.5, 9.0)
        self.ax.set_ylim(8.8, -1.6)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title("")
        
        # Перерисовываем
        self.fig.canvas.draw_idle()
    
    def update_display(self):
        """Обновляет отображение текущего решения"""
        if self.all_solutions and self.current_idx < len(self.all_solutions):
            board = self.all_solutions[self.current_idx]
            self.draw_board(board)
            # Обновляем заголовок окна с номером решения
            self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
    
    def clear_obstacles(self, event):
        """Очищает все препятствия"""
        self.obstacles.clear()
        self.recalculate_solutions()
    
    def prev_solution(self, event):
        """Предыдущее решение"""
        if self.all_solutions and self.current_idx > 0:
            self.current_idx -= 1
            self.update_display()
    
    def next_solution(self, event):
        """Следующее решение"""
        if self.all_solutions and self.current_idx < self.total - 1:
            self.current_idx += 1
            self.update_display()
    
    def first_solution(self, event):
        """Первое решение"""
        if self.all_solutions and self.current_idx != 0:
            self.current_idx = 0
            self.update_display()
    
    def last_solution(self, event):
        """Последнее решение"""
        if self.all_solutions and self.current_idx != self.total - 1:
            self.current_idx = self.total - 1
            self.update_display()

# 4. Запуск программы
if __name__ == "__main__":
    print("Поиск всех решений задачи о восьми ферзях...")
    print("(без препятствий)")
    
    # Сначала находим все решения без препятствий
    initial_solutions = []
    solve_all_with_obstacles([0] * 8, 0, initial_solutions, set())
    
    print(f"Найдено {len(initial_solutions)} уникальных решений!")
    print("\nИнструкция:")
    print("- Кликайте по клеткам, чтобы добавлять/убирать препятствия")
    print("- Программа автоматически пересчитает решения")
    print("- Используйте кнопки навигации для просмотра решений\n")
    
    # Запускаем визуализацию
    viz = EightQueensVisualizerWithObstacles(initial_solutions)
    plt.show()