import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.animation import Animation
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
import random
import os
from glob import glob
import math
import kivy
from kivy.app import App
from kivy.uix.widget import Widget  # Adicione esta linha
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.animation import Animation
# Configuração da janela
Window.size = (1000, 700)
Window.clearcolor = (0.2, 0.4, 0.5, 1)

kivy.require('2.0.0')

class CelebrationWidget(Widget):
    active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(CelebrationWidget, self).__init__(**kwargs)
        self.particles = []
        self.bind(active=self.start_celebration)
    
    def start_celebration(self, instance, value):
        if value:
            self.create_particles()
            Clock.schedule_interval(self.update_particles, 1/60.)
        else:
            Clock.unschedule(self.update_particles)
            self.particles = []
            self.canvas.clear()
    
    def create_particles(self):
        colors = [
            (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
            (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1)
        ]
        for _ in range(100):
            particle = {
                'pos': [random.randint(0, int(self.width)), random.randint(0, int(self.height))],
                'size': random.randint(5, 15),
                'color': random.choice(colors),
                'speed': random.uniform(1, 3),
                'angle': random.uniform(0, 2 * math.pi),
                'life': random.uniform(1, 3)
            }
            self.particles.append(particle)
    
    def update_particles(self, dt):
        self.canvas.clear()
        with self.canvas:
            for particle in self.particles[:]:
                particle['pos'][0] += math.cos(particle['angle']) * particle['speed']
                particle['pos'][1] += math.sin(particle['angle']) * particle['speed'] - 0.5
                particle['life'] -= dt
                
                if particle['life'] <= 0:
                    self.particles.remove(particle)
                else:
                    Color(*particle['color'])
                    Ellipse(pos=particle['pos'], size=(particle['size'], particle['size']))

class DraggablePuzzlePiece(Image):
    piece_id = NumericProperty(0)
    correct_pos = ListProperty([0, 0])
    is_correct = False
    snap_threshold = 50

    def __init__(self, **kwargs):
        super(DraggablePuzzlePiece, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.allow_stretch = True
        self.keep_ratio = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.is_correct:
            touch.grab(self)
            parent = self.parent
            if parent:
                parent.remove_widget(self)
                parent.add_widget(self)
            return True
        return super(DraggablePuzzlePiece, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and not self.is_correct:
            self.center = touch.pos
            return True
        return super(DraggablePuzzlePiece, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and not self.is_correct:
            touch.ungrab(self)
            if self.check_snap():
                self.center = self.correct_pos
                self.is_correct = True
                # Animação quando a peça encaixa
                anim = Animation(size=(self.width*1.1, self.height*1.1), duration=0.1) + \
                       Animation(size=(self.width, self.height), duration=0.1)
                anim.start(self)
            return True
        return super(DraggablePuzzlePiece, self).on_touch_up(touch)

    def check_snap(self):
        return (abs(self.center_x - self.correct_pos[0]) < self.snap_threshold and
                abs(self.center_y - self.correct_pos[1]) < self.snap_threshold)

class PuzzleGame(FloatLayout):
    def __init__(self, app, **kwargs):
        super(PuzzleGame, self).__init__(**kwargs)
        self.app = app
        self.pieces = []
        self.celebration = CelebrationWidget()
        self.add_widget(self.celebration)
        self.celebration.size = self.size
        Clock.schedule_once(self.setup_puzzle, 0.1)

    def setup_puzzle(self, dt):
        self.clear_widgets()
        self.add_widget(self.celebration)
        self.pieces = []
        
        cols, rows = 3, 2
        img = self.app.original_image
        img_width, img_height = img.size
        
        img_ratio = img_width / img_height
        available_height = self.height * 0.6
        available_width = self.width * 0.8
        
        if available_width / available_height > img_ratio:
            puzzle_height = available_height
            puzzle_width = puzzle_height * img_ratio
        else:
            puzzle_width = available_width
            puzzle_height = puzzle_width / img_ratio
        
        puzzle_x = (self.width - puzzle_width) / 2
        puzzle_y = self.height * 0.3
        
        with self.canvas:
            Color(0.1, 0.1, 0.1, 0.3)
            Rectangle(pos=(puzzle_x, puzzle_y), size=(puzzle_width, puzzle_height))
            
            Color(1, 1, 1, 0.7)
            cell_width = puzzle_width / cols
            cell_height = puzzle_height / rows
            
            for i in range(cols + 1):
                Line(points=[puzzle_x + i * cell_width, puzzle_y, 
                           puzzle_x + i * cell_width, puzzle_y + puzzle_height], width=1.5)
            
            for i in range(rows + 1):
                Line(points=[puzzle_x, puzzle_y + i * cell_height,
                           puzzle_x + puzzle_width, puzzle_y + i * cell_height], width=1.5)
        
        piece_width = cell_width * 0.95
        piece_height = cell_height * 0.95
        
        img_piece_width = img_width // cols
        img_piece_height = img_height // rows
        
        for row in range(rows):
            for col in range(cols):
                left = col * img_piece_width
                upper = row * img_piece_height
                right = left + img_piece_width
                lower = upper + img_piece_height
                piece_img = img.crop((left, upper, right, lower))
                
                piece_img = piece_img.transpose(PILImage.FLIP_TOP_BOTTOM)
                texture = self.pil_to_kivy_texture(piece_img)
                
                piece = DraggablePuzzlePiece(
                    texture=texture,
                    size=(piece_width, piece_height),
                    piece_id=row * cols + col
                )
                
                piece.correct_pos = (
                    puzzle_x + (col + 0.5) * cell_width,
                    puzzle_y + (rows - row - 0.5) * cell_height
                )
                
                min_x = 50
                max_x = max(min_x, int(self.width - piece.width - 50))
                min_y = 50
                max_y = max(min_y, int(puzzle_y - piece.height - 20))
                
                piece.pos = (
                    random.randint(min_x, max_x),
                    random.randint(min_y, max_y)
                )
                
                self.add_widget(piece)
                self.pieces.append(piece)
        
        btn_check = Button(
            text="Verificar",
            size_hint=(0.3, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        btn_check.bind(on_press=self.check_puzzle)
        self.add_widget(btn_check)

    def pil_to_kivy_texture(self, pil_img):
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        texture = Texture.create(size=pil_img.size, colorfmt='rgba')
        texture.blit_buffer(pil_img.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        return texture

    def check_puzzle(self, instance):
        correct_pieces = sum(1 for piece in self.pieces if piece.is_correct)
        total_pieces = len(self.pieces)
        
        # Calcula pontuação da montagem (0-5 pontos)
        assembly_score = int(5 * (correct_pieces / total_pieces))
        self.app.assembly_score = assembly_score
        
        if correct_pieces == total_pieces:
            self.celebration.active = True
            Clock.schedule_once(lambda dt: setattr(self.celebration, 'active', False), 2)
            self.app.show_question()
        else:
            feedback = f"Você encaixou {correct_pieces} de {total_pieces} peças.\nTente encaixar todas para ganhar mais pontos!"
            self.app.show_message(feedback, None)

class BioMemoryApp(App):
    def __init__(self, **kwargs):
        super(BioMemoryApp, self).__init__(**kwargs)
        self.title = "BioMemory"
        self.original_image = None
        self.score = 0
        self.assembly_score = 0
        self.current_amphibian_group = ""
        self.images_played = 0
        self.layout = BoxLayout(orientation='vertical')
        self.timer_event = None
        self.all_images = []

    def build(self):
        try:
            self.load_amphibian_images()
            self.show_welcome_screen()
        except Exception as e:
            self.show_error(f"Erro inicial: {str(e)}")
        return self.layout

    def load_amphibian_images(self):
        try:
            if not os.path.exists("amphibians"):
                os.makedirs("amphibians")
                self.create_sample_images()
            
            groups = ["anura", "urodela", "apoda"]
            self.all_images = []
            
            for group in groups:
                images = glob(os.path.join("amphibians", f"{group}_*.jpg")) + \
                         glob(os.path.join("amphibians", f"{group}_*.png"))
                self.all_images.extend(images[:2])
            
            if len(self.all_images) < 3:
                raise Exception("Adicione imagens para cada grupo (anura, urodela, apoda)")
                
        except Exception as e:
            self.show_error(str(e))
            raise

    def create_sample_images(self):
        groups = ["anura", "urodela", "apoda"]
        colors = {
            "anura": (220, 80, 80),
            "urodela": (80, 220, 80),
            "apoda": (80, 80, 220)
        }
        
        for group in groups:
            for i in range(1, 3):
                img = PILImage.new('RGB', (600, 400), colors[group])
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    font = ImageFont.load_default()
                
                draw = ImageDraw.Draw(img)
                text = f"{group.capitalize()} {i}"
                w, h = draw.textsize(text, font=font)
                draw.text(((600-w)/2, (400-h)/2), text, font=font, fill=(255, 255, 255))
                img.save(os.path.join("amphibians", f"{group}_{i}.jpg"))

    def show_error(self, message):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        content.add_widget(Label(text=message, font_size=20, color=(1,1,1,1)))
        btn = Button(text="OK", size_hint=(1, 0.3))
        popup = Popup(title="Erro", content=content, size_hint=(0.8, 0.5))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def show_welcome_screen(self):
        self.layout.clear_widgets()
        
        welcome = Label(
            text="[b]Bem-vindo ao BioMemory![/b]\n\n"
                 "Você terá 3 segundos para memorizar cada anfíbio\n"
                 "e depois montar o quebra-cabeça.\n"
                 "Acerte o grupo para ganhar pontos extras!\n\n"
                 "Pontuação máxima por rodada: 10 pontos",
            font_size=24,
            halign='center',
            size_hint=(1, 0.6),
            color=(1, 1, 1, 1),
            markup=True
        )
        
        btn_start = Button(
            text="COMEÇAR JOGO",
            size_hint=(0.7, 0.15),
            pos_hint={'center_x': 0.5},
            font_size=20,
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        btn_start.bind(on_press=self.start_game)
        
        self.layout.add_widget(welcome)
        self.layout.add_widget(btn_start)

    def start_game(self, instance):
        if not hasattr(self, 'all_images') or len(self.all_images) < 3:
            self.show_error("Adicione imagens na pasta 'amphibians'")
            return
            
        self.score = 0
        self.images_played = 0
        self.select_random_image()

    def select_random_image(self):
        if not self.all_images or self.images_played >= 3:
            self.show_final_screen()
            return
            
        image_path = random.choice(self.all_images)
        self.all_images.remove(image_path)
        
        filename = os.path.basename(image_path).lower()
        if "anura" in filename:
            self.current_amphibian_group = "Anura"
        elif "urodela" in filename:
            self.current_amphibian_group = "Urodela"
        else:
            self.current_amphibian_group = "Apoda"
        
        self.original_image = PILImage.open(image_path)
        self.show_image_for_memorization()

    def show_image_for_memorization(self):
        self.layout.clear_widgets()
        self.countdown = 3
        self.timer_label = Label(
            text=f"Memorize: {self.countdown}s",
            font_size=26,
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.timer_label)
        
        img_texture = self.pil_to_kivy_texture(self.original_image)
        img_widget = Image(
            texture=img_texture,
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5},
            keep_ratio=True,
            allow_stretch=True
        )
        self.layout.add_widget(img_widget)
        
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.countdown -= 1
        self.timer_label.text = f"Memorize: {self.countdown}s"
        
        if self.countdown <= 0:
            if self.timer_event:
                self.timer_event.cancel()
            self.create_puzzle()

    def create_puzzle(self):
        self.layout.clear_widgets()
        self.assembly_score = 0  # Reset da pontuação de montagem
        self.layout.add_widget(PuzzleGame(self))

    def show_question(self):
        self.layout.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        
        img_texture = self.pil_to_kivy_texture(self.original_image)
        img_widget = Image(
            texture=img_texture,
            size_hint=(0.8, 0.5),
            pos_hint={'center_x': 0.5},
            keep_ratio=True,
            allow_stretch=True
        )
        main_layout.add_widget(img_widget)
        
        lbl_question = Label(
            text="Qual grupo este anfíbio pertence?",
            font_size=26,
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(lbl_question)
        
        options = ["Anura", "Urodela", "Apoda"]
        random.shuffle(options)
        
        for option in options:
            btn = Button(
                text=option,
                size_hint=(0.7, 0.12),
                pos_hint={'center_x': 0.5},
                font_size=20,
                background_color=(0.4, 0.6, 0.9, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, opt=option: self.check_answer(opt))
            main_layout.add_widget(btn)
        
        self.layout.add_widget(main_layout)

    def check_answer(self, selected_option):
        # Pontuação da resposta (0-5 pontos)
        answer_score = 5 if selected_option == self.current_amphibian_group else 0
        
        # Pontuação total da rodada (montagem + resposta)
        round_score = self.assembly_score + answer_score
        self.score += round_score
        
        feedback = ""
        if selected_option == self.current_amphibian_group:
            feedback += f"Correto! +5 pontos (Identificação)\n"
        else:
            feedback += f"Errado! Era {self.current_amphibian_group}\n"
        
        feedback += f"+{self.assembly_score} pontos (Montagem)\n"
        feedback += f"Total desta rodada: {round_score}/10 pontos\n"
        feedback += f"Pontuação acumulada: {self.score}/{3*10} pontos\n\n"
        
        # Mensagem motivacional baseada na pontuação
        if round_score >= 9:
            feedback += "Excelente! Você dominou este anfíbio!"
        elif round_score >= 7:
            feedback += "Muito bom! Quase perfeito!"
        elif round_score >= 5:
            feedback += "Bom trabalho! Continue praticando!"
        elif round_score >= 3:
            feedback += "Foi bem, mas precisa estudar mais!"
        else:
            feedback += "Não desanime! Revise os grupos e tente novamente!"
        
        self.images_played += 1
        
        if self.images_played < 3:
            self.show_message(feedback, self.select_random_image)
        else:
            self.show_final_screen()

    def show_message(self, message, callback):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        content.add_widget(Label(text=message, font_size=18, color=(1,1,1,1)))
        
        btn = Button(
            text="CONTINUAR" if callback else "ENTENDI",
            size_hint=(1, 0.3),
            font_size=20,
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title="Resultado",
            content=content,
            size_hint=(0.8, 0.6))
        
        def dismiss_popup(instance):
            popup.dismiss()
            if callback:
                callback()
        
        btn.bind(on_press=dismiss_popup)
        content.add_widget(btn)
        popup.open()

    def show_final_screen(self):
        self.layout.clear_widgets()
        
        # Calcula porcentagem de acerto
        total_possible = 3 * 10  # 3 rodadas, 10 pontos cada
        percentage = (self.score / total_possible) * 100
        
        # Mensagem final baseada no desempenho
        if percentage >= 90:
            message = "PERFEITO! Você é um expert em anfíbios!"
            color = (0, 1, 0, 1)  # Verde
        elif percentage >= 70:
            message = "ÓTIMO TRABALHO! Você conhece bem os anfíbios!"
            color = (0.2, 0.8, 0.2, 1)  # Verde claro
        elif percentage >= 50:
            message = "BOM RESULTADO! Com mais prática você melhora!"
            color = (1, 1, 0, 1)  # Amarelo
        else:
            message = "CONTINUE ESTUDANDO! Revise os grupos e tente novamente!"
            color = (1, 0.5, 0, 1)  # Laranja
        
        main_layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        lbl_title = Label(
            text="Fim do Jogo!",
            font_size=36,
            color=(1, 1, 1, 1),
            bold=True
        )
        
        lbl_score = Label(
            text=f"Pontuação Final: {self.score}/30\n"
                 f"({percentage:.0f}% de acertos)",
            font_size=28,
            color=color
        )
        
        lbl_message = Label(
            text=message,
            font_size=24,
            color=color
        )
        
        btn_restart = Button(
            text="JOGAR NOVAMENTE",
            size_hint=(0.7, 0.15),
            pos_hint={'center_x': 0.5},
            font_size=20,
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_quit = Button(
            text="SAIR",
            size_hint=(0.7, 0.15),
            pos_hint={'center_x': 0.5},
            font_size=20,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_restart.bind(on_press=lambda x: self.restart_game())
        btn_quit.bind(on_press=lambda x: App.get_running_app().stop())
        
        main_layout.add_widget(lbl_title)
        main_layout.add_widget(lbl_score)
        main_layout.add_widget(lbl_message)
        main_layout.add_widget(btn_restart)
        main_layout.add_widget(btn_quit)
        
        self.layout.add_widget(main_layout)
        
        # Efeitos de celebração para bons resultados
        if percentage >= 70:
            celebration = CelebrationWidget(size=self.layout.size)
            self.layout.add_widget(celebration)
            celebration.active = True
            Clock.schedule_once(lambda dt: setattr(celebration, 'active', False), 3)

    def restart_game(self):
        self.load_amphibian_images()
        self.show_welcome_screen()

    def pil_to_kivy_texture(self, pil_image):
        """Converte PIL Image para Kivy Texture corretamente"""
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        pil_image = pil_image.transpose(PILImage.FLIP_TOP_BOTTOM)
        texture = Texture.create(size=pil_image.size, colorfmt='rgba')
        texture.blit_buffer(pil_image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        return texture

if __name__ == '__main__':
    BioMemoryApp().run()