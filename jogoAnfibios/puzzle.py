# puzzle.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle
from kivy.core.image import Image as CoreImage
from kivy.uix.behaviors import DragBehavior

import random
from PIL import Image as PILImage
import os

class PuzzlePiece(DragBehavior, Image):
    def __init__(self, original_pos, **kwargs):
        super().__init__(**kwargs)
        self.original_pos = original_pos
        self.current_pos = original_pos
        self.drag_timeout = 10000000
        self.drag_distance = 0
        self.allow_stretch = True
        self.keep_ratio = False

class PuzzleArea(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pieces = []
        self.cols = 3
        self.rows = 3
        self.image_path = None

    def load_image(self, image_path):
        self.clear_widgets()
        self.pieces.clear()
        self.image_path = image_path

        img = PILImage.open(image_path)
        width, height = img.size

        piece_width = width // self.cols
        piece_height = height // self.rows

        # Criar imagens separadas para cada pedaço
        for row in range(self.rows):
            for col in range(self.cols):
                left = col * piece_width
                top = row * piece_height
                box = (left, top, left + piece_width, top + piece_height)
                piece_img = img.crop(box)

                piece_filename = f"piece_{row}_{col}.png"
                piece_path = os.path.join("temp", piece_filename)
                os.makedirs("temp", exist_ok=True)
                piece_img.save(piece_path)

                piece = PuzzlePiece(original_pos=(col, row), source=piece_path,
                                    size_hint=(None, None),
                                    size=(self.width // self.cols, self.height // self.rows))
                self.add_widget(piece)
                self.pieces.append(piece)

        self.bind(size=self.update_piece_positions)
        self.update_piece_positions()

    def update_piece_positions(self, *args):
        piece_width = self.width / self.cols
        piece_height = self.height / self.rows
        for piece in self.pieces:
            col, row = piece.current_pos
            piece.size = (piece_width, piece_height)
            piece.pos = (col * piece_width, row * piece_height)

    def shuffle(self):
        positions = [(col, row) for row in range(self.rows) for col in range(self.cols)]
        random.shuffle(positions)
        for piece, new_pos in zip(self.pieces, positions):
            piece.current_pos = new_pos
        self.update_piece_positions()

    def solve(self):
        for piece in self.pieces:
            piece.current_pos = piece.original_pos
        self.update_piece_positions()
