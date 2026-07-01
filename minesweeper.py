import sys
from typing import Final

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QLabel, QComboBox, QVBoxLayout, QGridLayout, QScrollArea, QMessageBox
)

EASY: Final[str] = '8 8 10'
NORMAL: Final[str] = '16 16 40'
HARD: Final[str] = '30 16 99'
ADMIN: Final[str] = ('gAAAAABo0SlSROmflEkNs98BH3ArIAXa9DNNfrO0IRbmAPjE'
                     'cz21H2-GTkP5KpU5EpZOgrSH8ck98tQp_UJljBD34F7nwpj0DdRPctHhQqLiy18qbuBmJD8=')


class Minesweeper:
    class Mine:
        def __init__(self) -> None:
            self.is_mine: bool = True

        def __repr__(self) -> str:
            return 'M'

        def __str__(self) -> str:
            return 'M'

        def __format__(self, format_spec: format) -> str:
            return f'{'M':{format_spec}}'

    class Flag:
        def __init__(self) -> None:
            self.is_flagged: bool = True

        def __repr__(self) -> str:
            return 'F'

        def __str__(self) -> str:
            return 'F'

        def __format__(self, format_spec: format) -> str:
            return f'{'F':{format_spec}}'

    class Doubt:
        def __init__(self) -> None:
            self.is_doubt: bool = True

        def __repr__(self) -> str:
            return '?'

        def __str__(self) -> str:
            return '?'

        def __format__(self, format_spec: format) -> str:
            return f'{'?':{format_spec}}'

    class ConsoleGame:
        def __init__(self, mode: EASY or NORMAL or HARD = NORMAL) -> None:
            self.rows, self.cols, self.mines = map(int, mode.split())
            self.board = [[0] * self.cols for _ in range(self.rows)]
            self.visible = [[False] * self.cols for _ in range(self.rows)]
            self.marks = [[None] * self.cols for _ in range(self.rows)]
            self.mines_placed = False
            self.game_over = False
            self.victory = False

        def _place_mines(self, safe_r: int, safe_c: int) -> None:
            from random import randint

            placed = 0
            forbidden = {(safe_r + dr, safe_c + dc) for dr in range(-1, 2) for dc in range(-1, 2)
                         if 0 <= safe_r + dr < self.rows and 0 <= safe_c + dc < self.cols}

            while placed < self.mines:
                r: int = randint(0, self.rows - 1)
                c: int = randint(0, self.cols - 1)

                if (r, c) in forbidden:
                    continue

                if not isinstance(self.board[r][c], Minesweeper.Mine):
                    self.board[r][c] = Minesweeper.Mine()
                    placed += 1

            self._calculate_numbers()
            self.mines_placed = True

        def _calculate_numbers(self) -> None:
            from itertools import product

            for r, c in product(range(self.rows), range(self.cols)):
                if isinstance(self.board[r][c], Minesweeper.Mine):
                    continue

                mines_count = 0
                for dr, dc in product(range(-1, 2), repeat=2):
                    if dr == dc == 0:
                        continue

                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if isinstance(self.board[nr][nc], Minesweeper.Mine):
                            mines_count += 1

                self.board[r][c] = mines_count

        def flags_count(self) -> int:
            return sum(isinstance(self.marks[r][c], Minesweeper.Flag)
                       for r in range(self.rows) for c in range(self.cols))

        def print_board(self, reveal: bool = False) -> None:
            print(f"Флагов осталось: {self.mines - self.flags_count()}")
            print("\t" + "\t".join(f"{i:2}" for i in range(1, self.cols + 1)))
            for r in range(1, self.rows + 1):
                row_str = f"{r:2}\t"
                for c in range(self.cols):
                    if reveal:
                        cell = self.board[r - 1][c]

                    else:
                        if isinstance(self.marks[r - 1][c], Minesweeper.Flag):
                            cell = Minesweeper.Flag()

                        elif isinstance(self.marks[r - 1][c], Minesweeper.Doubt):
                            cell = Minesweeper.Doubt()

                        elif not self.visible[r - 1][c]:
                            cell = '#'

                        else:
                            cell = self.board[r - 1][c]
                    row_str += f"{cell:>2}\t"
                print(row_str)

        def open_cell(self, r: int, c: int) -> None:
            if not (1 <= r <= self.rows and 1 <= c <= self.cols):
                print("Неверные координаты")
                return

            r -= 1
            c -= 1

            if self.marks[r][c] is not None or self.visible[r][c]:
                return

            if not self.mines_placed:
                self._place_mines(r, c)

            self.visible[r][c] = True
            if isinstance(self.board[r][c], Minesweeper.Mine):
                self.game_over = True
                print("Вы подорвались на мине!")
                return

            if self.board[r][c] == 0:
                from itertools import product

                for dr, dc in product(range(-1, 2), repeat=2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.visible[nr][nc]:
                            self.open_cell(nr + 1, nc + 1)

        def toggle_flag(self, r: int, c: int) -> None:
            if not (1 <= r <= self.rows and 1 <= c <= self.cols):
                print("Неверные координаты")
                return

            r -= 1
            c -= 1

            if self.visible[r][c]:
                return

            self.marks[r][c] = Minesweeper.Flag() if not isinstance(self.marks[r][c], Minesweeper.Flag) else None

        def toggle_question(self, r: int, c: int) -> None:
            if not (1 <= r <= self.rows and 1 <= c <= self.cols):
                print("Неверные координаты")
                return

            r -= 1
            c -= 1

            if self.visible[r][c]:
                return

            self.marks[r][c] = Minesweeper.Doubt() if not isinstance(self.marks[r][c], Minesweeper.Doubt) else None

        def check_victory(self) -> bool:
            from itertools import product

            for r, c in product(range(self.rows), range(self.cols)):
                if not isinstance(self.board[r][c], Minesweeper.Mine) and not self.visible[r][c]:
                    return False

            self.victory = True
            return True

        def run(self) -> None:
            while not self.game_over and not self.victory:
                self.print_board()
                cmd = input("Введите команду (<open / flag / doubt> <row> <col>): ").split()

                if not cmd:
                    continue

                if cmd[0] == 'open' and len(cmd) == 3:
                    r, c = int(cmd[1]), int(cmd[2])
                    self.open_cell(r, c)

                elif cmd[0] == 'flag' and len(cmd) == 3:
                    r, c = int(cmd[1]), int(cmd[2])
                    self.toggle_flag(r, c)

                elif cmd[0] == 'doubt' and len(cmd) == 3:
                    r, c = int(cmd[1]), int(cmd[2])
                    self.toggle_question(r, c)

                else:
                    print("Неверная команда")

                if self.check_victory():
                    print("Поздравляем, вы победили!")

            self.print_board(reveal=True)

    class _Game(QMainWindow):
        class MSG(QMessageBox):
            def __init__(self, parent: QMainWindow) -> None:
                super().__init__(parent)
                self._parent = parent
                self.setStyleSheet("background-color: white; font-weight: bold;")

            def victory(self) -> None:
                self.information(self._parent, 'Victory', 'Победа! Все спасены :)')

            def game_over(self) -> None:
                self.information(self._parent, 'Game Over', 'Проигрыш. Подрыв на мине ;(')

        class Cell(QPushButton):
            def __init__(self, row: int, col: int, parent_game: 'Minesweeper._Game') -> None:
                super().__init__('')
                self.setStyleSheet("""
                QPushButton {
                    background-color: #6a0d6a;
                    color: white;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    border: 1px solid #330033;
                    min-width: 30px;
                    min-height: 30px;
                }

                QPushButton:hover {
                    background-color: #8b008b;
                }

                QPushButton:pressed {
                    background-color: #4b004b;
                }
                """)
                self.setFixedSize(QSize(36, 36))

                self.row = row
                self.col = col
                self.parent_game = parent_game
                self.is_open = False
                self.is_flagged = False
                self.is_doubt = False

            def mousePressEvent(self, e: QMouseEvent) -> None:
                if self.is_open:
                    return

                game_logic: Minesweeper.ConsoleGame = self.parent_game.logic

                if e.button() == Qt.MouseButton.LeftButton:
                    if self.is_flagged:
                        return

                    self.open_cell(game_logic)

                elif e.button() == Qt.MouseButton.MiddleButton:
                    if self.is_doubt:
                        self.setText('')
                        self.is_doubt = False

                    else:
                        self.setText('?')
                        self.is_doubt = True

                    game_logic.toggle_question(self.row + 1, self.col + 1)
                    if self.parent_game.is_admin:
                        game_logic.print_board()

                elif e.button() == Qt.MouseButton.RightButton:
                    if self.is_flagged:
                        self.setText('')
                        self.is_flagged = False

                    elif self.parent_game.logic.flags_count() == self.parent_game.logic.mines:
                        return

                    else:
                        self.setText('🚩')
                        self.is_flagged = True

                    game_logic.toggle_flag(self.row + 1, self.col + 1)
                    self.parent_game.update_flags_count()

                    if self.parent_game.is_admin:
                        game_logic.print_board()

                if (e.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton) and game_logic.check_victory()
                        and self.parent_game.logic.flags_count() == self.parent_game.logic.mines):
                    msg_box = Minesweeper._Game.MSG(self.parent_game)
                    msg_box.victory()
                    self.parent_game.main_menu()
                    return

            def open_cell(self, game_logic: 'Minesweeper.ConsoleGame', gameover=False) -> None:
                if self.is_open or self.is_flagged:
                    return

                self.is_open = True
                game_logic.open_cell(self.row + 1, self.col + 1)
                value = game_logic.board[self.row][self.col]
                game_logic.print_board()

                if isinstance(value, Minesweeper.Mine):
                    if gameover:
                        self.setStyleSheet(f"background-color: red")
                        self.setText('💣')
                        return

                    if self.parent_game.is_admin:
                        game_logic.print_board(reveal=True)

                    from itertools import product

                    layout = self.parentWidget().layout()
                    for r, c in product(range(game_logic.rows), range(game_logic.cols)):
                        neighbor = layout.itemAtPosition(r, c).widget()
                        if neighbor and not neighbor.is_open:
                            neighbor.open_cell(game_logic, gameover=True)

                    self.setStyleSheet(f"background-color: red")
                    self.setText('💣')

                    Minesweeper._Game.MSG(self.parent_game).game_over()
                    self.parent_game.main_menu()
                    return

                number_colors = ["#0000FF", "#008200", "#FF0000", "#000084", "#840000", "#008284", "#840084", "#000000"]
                self.setStyleSheet(f"background-color: #aaaaaa; color: {number_colors[value - 1]}; font-weight: bold;")

                if value > 0:
                    self.setText(str(value))

                else:
                    layout = self.parentWidget().layout()

                    from itertools import product

                    for dx, dy in product(range(-1, 2), repeat=2):
                        nx, ny = self.row + dx, self.col + dy
                        if 0 <= nx < game_logic.rows and 0 <= ny < game_logic.cols:
                            neighbor = layout.itemAtPosition(nx, ny).widget()
                            if neighbor and not neighbor.is_open:
                                neighbor.open_cell(game_logic)

        def __init__(self, mode: None or ADMIN = None) -> None:
            super().__init__()
            self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e0033, stop:1 #4b004b
                );
            }

            QLabel#titleLabel {
                color: #ff99ff;
                font-family: 'Lucida Console', sans-serif;
                font-size: 32pt;
                font-weight: bold;
                text-shadow: 1px 1px 2px #000000;
            }

            QPushButton#btn {
                font-family: 'Lucida Console', sans-serif;
                font-size: 16pt;
                padding: 14px 24px;
                background-color: #8b008b;
                color: white;
                border-radius: 12px;
                border: 2px solid transparent;
                min-width: 200px;
                transition: all 0.2s;
            }

            QPushButton#btn:hover {
                background-color: #b300b3;
                border: 2px solid #ff66ff;
                color: black;
            }

            QPushButton#btn:pressed {
                background-color: #660066;
            }

            QComboBox {
                font-family: 'Lucida Console', sans-serif;
                font-size: 14pt;
                padding: 8px 16px;
                background-color: #8b008b;
                color: white;
                border-radius: 10px;
                border: 2px solid #330033;
                min-width: 180px;
            }

            QComboBox:hover {
                background-color: #b300b3;
                border: 2px solid #ff66ff;
                color: black;
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QScrollArea {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c003e, stop:1 #19002d
                );
                border: none;
            }

            QWidget#gameWrapper {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 12px;
                padding: 8px;
            }

            QVBoxLayout()#wrapperLayout {
                color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c003e, stop:1 #19002d
                );
            }
            """)

            if mode == ADMIN:
                self.is_admin = True
            else:
                self.is_admin = False

            self.setWindowTitle("Minesweeper")
            self.flags_label = None

            self.mode = NORMAL
            self.logic = None

            self.main_menu()

        def main_menu(self) -> None:
            self.setFixedSize(QSize(500, 500))

            central_widget = QWidget()

            label = QLabel('The Minesweeper')
            label.setObjectName("titleLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            start_btn = QPushButton('Start')
            start_btn.setFixedHeight(60)
            start_btn.clicked.connect(self.start_game)
            start_btn.setObjectName("btn")

            settings_btn = QPushButton('Settings')
            settings_btn.setFixedHeight(60)
            settings_btn.clicked.connect(self.settings)
            settings_btn.setObjectName("btn")

            exit_btn = QPushButton('Exit')
            exit_btn.setFixedHeight(60)
            exit_btn.clicked.connect(lambda _: QApplication.quit())
            exit_btn.setObjectName("btn")

            menu_layout = QVBoxLayout()
            menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            menu_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            menu_layout.addSpacing(20)
            menu_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            menu_layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            menu_layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

            central_widget.setLayout(menu_layout)
            self.setCentralWidget(central_widget)

        def start_game(self) -> None:
            self.logic = Minesweeper.ConsoleGame(self.mode)
            rows, cols = self.logic.rows, self.logic.cols

            if self.is_admin:
                self.logic.print_board(reveal=True)

            central_widget = QWidget()

            game_layout = QGridLayout()
            game_layout.setSpacing(6)
            game_layout.setContentsMargins(10, 10, 10, 10)

            self.flags_label = QLabel(f"🚩 Осталось: {self.logic.mines - self.logic.flags_count()}")
            self.flags_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.flags_label.setStyleSheet("""
                    QLabel {
                        color: #ffccff;
                        font-family: 'Lucida Console', sans-serif;
                        font-size: 14pt;
                        font-weight: bold;
                    }
                """)

            from itertools import product

            for row, col in product(range(rows), range(cols)):
                cell = Minesweeper._Game.Cell(row, col, self)
                game_layout.addWidget(cell, row, col)
                game_layout.setSpacing(4)

            central_widget.setLayout(game_layout)

            max_width, max_height = 800, 800
            width = cols * 36 + 50
            height = rows * 36 + 50

            if width <= max_width and height <= max_height:
                wrapper = QWidget()
                wrapper.setObjectName('gameWrapper')

                wrapper_layout = QVBoxLayout()
                wrapper_layout.setObjectName('wrapperLayout')
                wrapper_layout.addWidget(self.flags_label, alignment=Qt.AlignmentFlag.AlignCenter)
                wrapper_layout.addWidget(central_widget)
                wrapper_layout.setContentsMargins(10, 10, 10, 10)

                wrapper.setLayout(wrapper_layout)

                self.setCentralWidget(wrapper)
                self.setFixedSize(QSize(width, height))

            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(central_widget)

                wrapper = QWidget()
                wrapper.setObjectName('gameWrapper')

                wrapper_layout = QVBoxLayout()
                wrapper_layout.setObjectName('wrapperLayout')
                wrapper_layout.addWidget(self.flags_label, alignment=Qt.AlignmentFlag.AlignCenter)
                wrapper_layout.addWidget(scroll)
                wrapper_layout.setContentsMargins(10, 10, 10, 10)

                wrapper.setLayout(wrapper_layout)

                self.setCentralWidget(wrapper)
                self.setFixedSize(QSize(min(cols * 36, 800), min(rows * 36 + 100, 700)))

        def update_flags_count(self):
            remaining = self.logic.mines - self.logic.flags_count()
            self.flags_label.setText(f"🚩 Осталось: {remaining}")

        def settings(self) -> None:
            self.setFixedSize(QSize(500, 500))

            central_widget = QWidget()

            label = QLabel('Settings')
            label.setObjectName("titleLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            mode_option = QComboBox()
            mode_option.addItems(['Easy', 'Normal', 'Hard'])
            mode_option.setCurrentIndex(1)
            mode_option.activated.connect(lambda _: self.change_mode(mode_option))

            back_btn = QPushButton('Back')
            back_btn.setFixedHeight(60)
            back_btn.clicked.connect(self.main_menu)
            back_btn.setObjectName("btn")

            settings_layout = QVBoxLayout()
            settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            settings_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            settings_layout.addSpacing(20)
            settings_layout.addWidget(mode_option, alignment=Qt.AlignmentFlag.AlignCenter)
            settings_layout.addSpacing(20)
            settings_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

            central_widget.setLayout(settings_layout)
            self.setCentralWidget(central_widget)

        def change_mode(self, obj: QComboBox) -> None:
            mode = obj.currentText()

            if self.is_admin:
                print(f'Selected {mode} game mode.')

            if mode == 'Easy':
                self.mode = EASY

            elif mode == 'Hard':
                self.mode = HARD

            else:
                self.mode = NORMAL

    class Game:
        @staticmethod
        def run(mode: ADMIN or None = None) -> None:
            _app = QApplication(sys.argv)
            try:
                _game = Minesweeper._Game(mode=mode)
                _game.show()
            except KeyboardInterrupt:
                pass
            finally:
                sys.exit(_app.exec())


if __name__ == '__main__':
    # console_game = Minesweeper.ConsoleGame()
    game = Minesweeper.Game()
    # console_game.run()
    game.run(mode=ADMIN)
