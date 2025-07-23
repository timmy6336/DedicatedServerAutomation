from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
import requests
from static.games_list import GAMES_LIST
from game import Game

class GameListPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Game List')
        layout = QVBoxLayout()
        label = QLabel('Games:')
        layout.addWidget(label)
        # Create Game objects for each entry
        self.games = [Game(name) for name in GAMES_LIST]
        for game in self.games:
            game_layout = QVBoxLayout()
            game_label = QLabel(str(game))
            game_layout.addWidget(game_label)
            if game.image_url:
                try:
                    response = requests.get(game.image_url)
                    response.raise_for_status()
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    game_layout.addWidget(image_label)
                except Exception as e:
                    error_label = QLabel(f"Image load error: {e}")
                    game_layout.addWidget(error_label)
            layout.addLayout(game_layout)
        self.setLayout(layout)
