import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

# 1. Функция для поиска ВСЕХ решений задачи о восьми ферзях
def solve_all(board, row, solutions):
    if row == 8:
        # Сохраняем копию найденного решения
        solutions.append(board.copy())
        return
    for col in range(8):
        if is_safe(board, row, col):
            board[row] = col
            solve_all(board, row + 1, solutions)

def is_safe(board, row, col):
    for prev_row in range(row):
        prev_col = board[prev_row]
        if prev_col == col or abs(prev_col - col) == abs(prev_row - row):
            return False
    return True

# 2. Класс для визуализации с кнопками навигации
class EightQueensVisualizer:
    def __init__(self, solutions):
        self.solutions = solutions
        self.current_idx = 0
        self.total = len(solutions)
        
        # Создаем фигуру с большими размерами
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        plt.subplots_adjust(bottom=0.12)  # Оставляем место для кнопок
        
        # Устанавливаем заголовок окна
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
        
        # Создаем кнопки
        ax_prev = plt.axes([0.25, 0.05, 0.12, 0.05])
        ax_next = plt.axes([0.55, 0.05, 0.12, 0.05])
        ax_first = plt.axes([0.1, 0.05, 0.12, 0.05])
        ax_last = plt.axes([0.7, 0.05, 0.12, 0.05])
        
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперед >')
        self.btn_first = Button(ax_first, '← Первое')
        self.btn_last = Button(ax_last, 'Последнее →')
        
        # Привязываем обработчики
        self.btn_prev.on_clicked(self.prev_solution)
        self.btn_next.on_clicked(self.next_solution)
        self.btn_first.on_clicked(self.first_solution)
        self.btn_last.on_clicked(self.last_solution)
        
        # Рисуем первое решение
        self.update_display()
        
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
        
        # Добавляем ферзей
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
        
        # Настройка отображения - без заголовка на доске
        self.ax.set_xlim(-1.5, 9.0)
        self.ax.set_ylim(8.5, -1.5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title("")  # Убираем заголовок с доски
        
        # Перерисовываем
        self.fig.canvas.draw_idle()
    
    def update_display(self):
        """Обновляет отображение текущего решения"""
        board = self.solutions[self.current_idx]
        self.draw_board(board)
        # Обновляем заголовок окна с номером решения
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
    
    def prev_solution(self, event):
        """Предыдущее решение"""
        if self.current_idx > 0:
            self.current_idx -= 1
            self.update_display()
    
    def next_solution(self, event):
        """Следующее решение"""
        if self.current_idx < self.total - 1:
            self.current_idx += 1
            self.update_display()
    
    def first_solution(self, event):
        """Первое решение"""
        if self.current_idx != 0:
            self.current_idx = 0
            self.update_display()
    
    def last_solution(self, event):
        """Последнее решение"""
        if self.current_idx != self.total - 1:
            self.current_idx = self.total - 1
            self.update_display()

# 3. Альтернативная версия с буквой Q (если символ ♕ не отображается)
class EightQueensVisualizerSimple:
    def __init__(self, solutions):
        self.solutions = solutions
        self.current_idx = 0
        self.total = len(solutions)
        
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.subplots_adjust(bottom=0.12)
        
        # Устанавливаем заголовок окна
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
        
        ax_prev = plt.axes([0.25, 0.05, 0.12, 0.05])
        ax_next = plt.axes([0.55, 0.05, 0.12, 0.05])
        ax_first = plt.axes([0.1, 0.05, 0.12, 0.05])
        ax_last = plt.axes([0.7, 0.05, 0.12, 0.05])
        
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперед >')
        self.btn_first = Button(ax_first, '← Первое')
        self.btn_last = Button(ax_last, 'Последнее →')
        
        self.btn_prev.on_clicked(self.prev_solution)
        self.btn_next.on_clicked(self.next_solution)
        self.btn_first.on_clicked(self.first_solution)
        self.btn_last.on_clicked(self.last_solution)
        
        self.update_display()
        
    def draw_board(self, board):
        self.ax.clear()
        
        board_matrix = np.zeros((8, 8))
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    board_matrix[r, c] = 1
                else:
                    board_matrix[r, c] = 0
        
        cmap = plt.matplotlib.colors.ListedColormap(['#8B4513', '#F0D9B5'])
        self.ax.imshow(board_matrix, cmap=cmap, extent=[-0.5, 7.5, 7.5, -0.5])
        
        for r in range(8):
            c = board[r]
            circle = plt.Circle((c, r), 0.35, color='red', zorder=3, 
                               edgecolor='darkred', linewidth=2)
            self.ax.add_patch(circle)
            self.ax.text(c, r, 'Q', ha='center', va='center', 
                        fontsize=22, color='white', fontweight='bold', zorder=4)
        
        # Рисуем бордер
        border = plt.Rectangle((-0.5, -0.5), 8, 8, fill=False, 
                              edgecolor='black', linewidth=4)
        self.ax.add_patch(border)
        
        # Подписи колонок и строк
        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, col in enumerate(columns):
            self.ax.text(i, -1, col, ha='center', va='top', fontsize=14, fontweight='bold')
            self.ax.text(i, 8.0, col, ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        for i in range(1, 9):
            self.ax.text(-0.75, i-1, str(i), ha='right', va='center', fontsize=14, fontweight='bold')
            self.ax.text(7.76, i-1, str(i), ha='left', va='center', fontsize=14, fontweight='bold')
        
        self.ax.set_xlim(-1.5, 9.0)
        self.ax.set_ylim(8.5, -1.5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title("")  # Убираем заголовок с доски
        
        self.fig.canvas.draw_idle()
    
    def update_display(self):
        board = self.solutions[self.current_idx]
        self.draw_board(board)
        # Обновляем заголовок окна
        self.fig.canvas.manager.set_window_title(f"Задача о восьми ферзях - Решение {self.current_idx + 1} из {self.total}")
    
    def prev_solution(self, event):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.update_display()
    
    def next_solution(self, event):
        if self.current_idx < self.total - 1:
            self.current_idx += 1
            self.update_display()
    
    def first_solution(self, event):
        if self.current_idx != 0:
            self.current_idx = 0
            self.update_display()
    
    def last_solution(self, event):
        if self.current_idx != self.total - 1:
            self.current_idx = self.total - 1
            self.update_display()

# 4. Запуск программы
if __name__ == "__main__":
    print("Поиск всех решений задачи о восьми ферзях...")
    solutions = []
    solve_all([0] * 8, 0, solutions)
    
    print(f"Найдено {len(solutions)} уникальных решений!")
    print("Открывается окно с визуализацией. Используйте кнопки для навигации.")
    
    # Выберите один из вариантов:
    # Вариант 1: С символом ♕
    viz = EightQueensVisualizer(solutions)
    
    # Вариант 2: С буквой Q (раскомментируйте если символ ♕ не отображается)
    # viz = EightQueensVisualizerSimple(solutions)
    
    plt.show()