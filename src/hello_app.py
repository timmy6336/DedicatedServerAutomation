import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from PyQt5.QtWidgets import QStackedWidget
from game_list_page import GameListPage

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyQt5 Hello World')
        self.stacked_widget = QStackedWidget()
        self.main_page = QWidget()
        main_layout = QVBoxLayout()
        self.show_games_btn = QPushButton('Show Game List')
        self.show_games_btn.clicked.connect(self.show_game_list)
        main_layout.addWidget(self.show_games_btn)
        self.main_page.setLayout(main_layout)
        self.game_list_page = GameListPage()
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.game_list_page)
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def show_game_list(self):
        self.stacked_widget.setCurrentWidget(self.game_list_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
