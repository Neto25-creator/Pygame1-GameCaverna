import pygame
import sys
import math
import random
import json # Para o arquivo de texto de pontuações
import os   # Para verificar a existência do arquivo
from datetime import datetime
pygame.init()

#exigencia = importar uma função de outro arquivo: 
from recursos.ola import dizer_ola 
dizer_ola()

# Definições de Tela e Variáveis Globais
WIDTH, HEIGHT = 1000, 700
PLAYER_SPEED = 8
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plataforma Vertical")
# Carregamento de Imagens 
try:
    background_image_game = pygame.image.load("recursos/mainImages/caverna.png").convert() # Renomeado para clareza
    background_image_game = pygame.transform.scale(background_image_game, (WIDTH, HEIGHT))
    
    menu_background_img = pygame.image.load('recursos/mainImages/menu.png').convert()
    menu_background_img = pygame.transform.scale(menu_background_img, (WIDTH, HEIGHT))

    game_over_bg_img = pygame.image.load("recursos/mainImages/gameover.png").convert()
    game_over_bg_img = pygame.transform.scale(game_over_bg_img, (WIDTH, HEIGHT))

    # Carregando a imagem de fundo das instruções aqui para evitar recarregar
    instructions_background_img = pygame.image.load('recursos/mainImages/instrucoes.png').convert()
    instructions_background_img = pygame.transform.scale(instructions_background_img, (WIDTH, HEIGHT))
    
    recordes_imagem = pygame.image.load("recursos/mainImages/recordes.png").convert()
    recordes_imagem = pygame.transform.scale(recordes_imagem, (WIDTH, HEIGHT))
    
except pygame.error as e:
    print(f"Erro crucial ao carregar imagem de fundo: {e}.")
    print("Verifique se a pasta 'mainImages' e as imagens essenciais existem.")
    pygame.quit()
    sys.exit()


CLOCK = pygame.time.Clock()
FPS = 60
GRAVITY_PLAYER = 1.0 # Gravidade específica do jogador, diferente do GRAVITY global original

max_horizontal_gap = 150
max_vertical_gap = 120

pygame.mixer.init()
try:
    coin_sound = pygame.mixer.Sound("recursos/mainSounds/coin.mp3")
    coin_sound.set_volume(0.3)
    gameover_sound = pygame.mixer.Sound("recursos/mainSounds/gameover.mp3")
    jump_sound = pygame.mixer.Sound("recursos/mainSounds/jump.mp3")
    jump_sound.set_volume(0.3)
except pygame.error as e:
    print(f"Aviso: Erro ao carregar som: {e}. O jogo continuará sem alguns sons.")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
INPUT_BOX_COLOR = (50, 50, 80)
INPUT_TEXT_COLOR = (230, 230, 230)
SCORE_TEXT_COLOR = (220, 220, 200)

# Fontes
FONT_SMALL = pygame.font.SysFont("Arial", 24)
FONT_MEDIUM = pygame.font.SysFont("Arial", 36)
FONT_LARGE = pygame.font.SysFont("Arial", 60)

# --- Armazenamento de Pontuação (Arquivo JSON) ---
SCORES_FILE = "game_scores.json"

def load_score_data():
    if not os.path.exists(SCORES_FILE):
        return {"high_score": None, "recent_scores": []}
    try:
        with open(SCORES_FILE, 'r') as f:
            data = json.load(f)
            if "high_score" not in data: data["high_score"] = None
            if "recent_scores" not in data: data["recent_scores"] = []
            return data
    except (json.JSONDecodeError, IOError):
        print(f"Aviso: Arquivo de pontuação '{SCORES_FILE}' não encontrado ou corrompido. Um novo será criado.")
        return {"high_score": None, "recent_scores": []}

def save_score_data(data_to_save):
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except IOError:
        print(f"Erro: Não foi possível salvar os dados de pontuação em '{SCORES_FILE}'.")

from datetime import datetime

def update_and_save_game_score(player_name_str, score_value, coins_value):
    data = load_score_data()

    agora = datetime.now()
    data_str = agora.strftime('%d/%m/%Y')
    hora_str = agora.strftime('%H:%M:%S')

    current_game_entry = {
        "name": player_name_str,
        "score": score_value,
        "coins": coins_value,
        "data": data_str,
        "hora": hora_str
    }

    if data["high_score"] is None or score_value > data["high_score"]["score"] or \
       (score_value == data["high_score"]["score"] and coins_value > data["high_score"]["coins"]):
        data["high_score"] = current_game_entry

    data["recent_scores"].insert(0, current_game_entry)
    data["recent_scores"] = data["recent_scores"][:5]
    save_score_data(data)
# --- Fim do Armazenamento de Pontuação ---

# --- Definições de Classes Originais ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.frames = [
                pygame.transform.scale(
                    pygame.image.load(f"recursos/frames/CoinFrame/frame_{i}.png").convert_alpha(), (24, 24)
                )
                for i in range(8)
            ]
        except pygame.error as e:
            print(f"Aviso: Erro ao carregar frames da moeda: {e}.")
            self.frames = [pygame.Surface((24,24), pygame.SRCALPHA)]; self.frames[0].fill(YELLOW) # Placeholder
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        try:
            self.frames_right = [
                pygame.transform.scale(pygame.image.load(f"recursos/frames/SelfFrames/direita/frame_{i}_di.png").convert_alpha(), (50, 60))
                for i in range(4)
            ]
            self.frames_left = [
                pygame.transform.scale(pygame.image.load(f"recursos/frames/SelfFrames/esquerda/frame_{i}_es.png").convert_alpha(), (50, 60))
                for i in range(4)
            ]
        except pygame.error as e:
            print(f"Aviso: Erro ao carregar frames do jogador: {e}.")
            self.frames_right = [pygame.Surface((50,60), pygame.SRCALPHA) for _ in range(4)] # Placeholders
            self.frames_left = [pygame.Surface((50,60), pygame.SRCALPHA) for _ in range(4)]
            for frame in self.frames_right + self.frames_left: frame.fill(RED)

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.image = self.frames_right[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.alive = True
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        self.visited_platforms = set()
        self.last_direction = "right"
        self.started_jumping = False # Variável original
        self.can_score = False       # Variável original
        self.jump_force = -12.5
        self.gravity = GRAVITY_PLAYER # Usando a gravidade específica do jogador
        self.max_fall_speed = 10.0
        self.jump_timer = 0
        self.jump_timer_max = 10

    def update(self, platforms): # lógica original
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.last_direction = "left"
            moved = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.last_direction = "right"
            moved = True
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        if keys[pygame.K_w]:
            if self.on_ground:
                self.vel_y = self.jump_force
                self.on_ground = False
                self.jump_timer = self.jump_timer_max
                if 'jump_sound' in globals(): jump_sound.play()
            elif self.jump_timer > 0:
                self.vel_y = self.jump_force
                self.jump_timer -= 1
        else:
            self.jump_timer = 0
        if moved:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % 4
        else:
            self.current_frame = 0 
        if self.last_direction == "right":
            self.image = self.frames_right[self.current_frame]
        else:
            self.image = self.frames_left[self.current_frame]
        self.vel_y += self.gravity
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        old_bottom = self.rect.bottom
        self.rect.y += self.vel_y
        landed = False
        for p in platforms:
            if self.vel_y > 0 and self.rect.colliderect(p.rect) and old_bottom <= p.rect.top + 1: # Verifica se está caindo
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True
                landed = True
                if id(p) not in self.visited_platforms and p.rect.top < HEIGHT - 50:
                    self.visited_platforms.add(id(p))
                    self.score += 1
                break
        if not landed:
            self.on_ground = False
        if self.rect.top > HEIGHT:
            self.alive = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, largura=None, altura=None, image_file="recursos/mainImages/plataformas1.png"):
        super().__init__()
        try:
            imagem_original = pygame.image.load(image_file).convert_alpha()
        except pygame.error as e:
            print(f"Aviso: Erro ao carregar imagem da plataforma '{image_file}': {e}.")
            imagem_original = pygame.Surface((largura if largura else 100, altura if altura else 20), pygame.SRCALPHA)
            imagem_original.fill((150,150,150)) 
        
        if largura is None or altura is None:
            self.image = imagem_original
        else:
            orig_width, orig_height = imagem_original.get_size()
            if orig_width > 0:
                scale_x = largura / orig_width
                nova_altura = int(orig_height * scale_x)
                self.image = pygame.transform.scale(imagem_original, (largura, nova_altura))
            else: 
                self.image = pygame.transform.scale(imagem_original, (largura, altura if altura else 20))
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_min=0.5, speed_max=2.0):
        super().__init__()
        try:
            self.frames = [
                pygame.transform.scale(pygame.image.load(f"recursos/frames/EnemyFrames/frame_{i}.png").convert_alpha(), (37, 37))
                for i in range(15)
            ]
        except pygame.error as e:
            print(f"Aviso: Erro ao carregar frames do inimigo: {e}.")
            self.frames = [pygame.Surface((37,37), pygame.SRCALPHA)]; self.frames[0].fill(BLACK) # Placeholder

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1 # velocidade original
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dir_x = random.choice([-1, 1])
        self.dir_y = random.choice([-1, 1])
        self.speed_x = random.uniform(speed_min, speed_max)
        self.speed_y = random.uniform(speed_min, speed_max)
   
    def update(self): 
        self.rect.x += self.dir_x * self.speed_x
        self.rect.y += self.dir_y * self.speed_y
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dir_x *= -1
        if self.rect.top <= 0: # condição original
            self.dir_y *= -1
        if self.rect.top > HEIGHT: 
            pass 
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
    
    
# --- Classe para Diamantes Decorativos ---  Exigencia de objeto randomico que nao interage com o personagem
class DecorativeDiamond(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_min=0.5, speed_max=2.0):
        super().__init__()
        try:
            self.image = pygame.transform.scale(pygame.image.load("recursos/mainImages/diamante.png").convert_alpha(), (30, 30))
        except pygame.error as e:
            print(f"Aviso: Erro ao carregar imagem do diamante: {e}.")
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            self.image.fill((0, 255, 255)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dir_x = random.choice([-1, 1])
        self.dir_y = random.choice([-1, 1])
        self.speed_x = random.uniform(speed_min, speed_max)
        self.speed_y = random.uniform(speed_min, speed_max)

    def update(self):
        self.rect.x += self.dir_x * self.speed_x
        self.rect.y += self.dir_y * self.speed_y

        # Inverte a direção se atingir as bordas da tela
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dir_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dir_y *= -1

# ---  Funções Originais de UI (draw_text, button) ---

def draw_text(text, font, color, x, y, center=False): 
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    SCREEN.blit(surface, rect)

def button(text, x, y, width, height): 
    mouse_pos = pygame.mouse.get_pos()
    # A variável 'click' aqui pega o estado contínuo do botão pressionado.
    
    click = pygame.mouse.get_pressed()[0] 
    rect = pygame.Rect(x, y, width, height)
    base_color = (30, 30, 60)
    hover_color = (70, 70, 120)
    click_color = (150, 150, 200)
    action = False # Variável para retornar se o botão foi "ativado"

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(SCREEN, hover_color, rect, border_radius=12)
        if click: # Se o mouse está sobre E pressionado
            pygame.draw.rect(SCREEN, click_color, rect, border_radius=12)
            
            action = True # O botão foi "clicado" de acordo com a lógica original
    else:
        pygame.draw.rect(SCREEN, base_color, rect, border_radius=12)
    
    
    draw_text(text, FONT_MEDIUM, WHITE, x + width / 2, y + height / 2, center=True)
    
    if action:
        pass

    return action


# --- Novas Telas e Funções Auxiliares para Menus ---
def ui_button_enhanced(text, x, y, width, height, font_to_use=FONT_MEDIUM, base_color=(30,30,60), hover_color=(70,70,120)):
    """Função de botão aprimorada para menus, apenas desenha e indica hover."""
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    is_hovered = rect.collidepoint(mouse_pos)
    
    current_color = hover_color if is_hovered else base_color
    pygame.draw.rect(SCREEN, current_color, rect, border_radius=12)
    draw_text(text, font_to_use, WHITE, rect.centerx, rect.centery, center=True) # Usa a draw_text original
    return is_hovered

def get_player_name_screen():
    player_name_str = ""
    input_field_rect = pygame.Rect(WIDTH / 2 - 200, HEIGHT / 2 - 25, 400, 50)
    error_message_str = ""
    max_name_len = 15

    btn_confirm_rect = pygame.Rect(WIDTH / 2 - 100 - 10, input_field_rect.bottom + 40, 200, 55) # X, Y, W, H
    btn_back_rect = pygame.Rect(WIDTH / 2 + 10, input_field_rect.bottom + 40, 200, 55) # X ajustado se necessário
   
    total_width_btns = 200 + 20 + 200 # Largura do botão de confirmação + espaçamento + largura do botão de voltar
    start_x_btns = WIDTH/2 - total_width_btns/2
    btn_confirm_rect = pygame.Rect(start_x_btns, input_field_rect.bottom + 40, 200, 55)
    btn_back_rect = pygame.Rect(start_x_btns + 200 + 20, input_field_rect.bottom + 40, 200, 55)


    screen_active = True
    while screen_active:
        SCREEN.blit(instructions_background_img, (0, 0)) 
        draw_text("Digite seu nome:", FONT_MEDIUM, WHITE, WIDTH / 2, HEIGHT / 2 - 80, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(player_name_str.strip()) > 0: return player_name_str.strip()
                    else: error_message_str = "Nome deve ter pelo menos 1 caractere!"
                elif event.key == pygame.K_BACKSPACE:
                    player_name_str = player_name_str[:-1]; error_message_str = ""
                elif event.key == pygame.K_ESCAPE: return None
                else:
                    if len(player_name_str) < max_name_len: player_name_str += event.unicode; error_message_str = ""
                    else: error_message_str = f"Máximo de {max_name_len} caracteres."
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_confirm_rect.collidepoint(event.pos):
                    if len(player_name_str.strip()) > 0: pygame.time.delay(100); return player_name_str.strip()
                    else: error_message_str = "Nome deve ter pelo menos 1 caractere!"
                elif btn_back_rect.collidepoint(event.pos):
                    pygame.time.delay(100); return None
        
        pygame.draw.rect(SCREEN, INPUT_BOX_COLOR, input_field_rect, border_radius=10)
        name_surf = FONT_MEDIUM.render(player_name_str, True, INPUT_TEXT_COLOR)
        SCREEN.blit(name_surf, (input_field_rect.x + 10, input_field_rect.y + (input_field_rect.height - name_surf.get_height()) / 2))
        pygame.draw.rect(SCREEN, WHITE, input_field_rect, 2, border_radius=10)

        if error_message_str:
            draw_text(error_message_str, FONT_SMALL, RED, WIDTH / 2, input_field_rect.bottom + 15, center=True)

        ui_button_enhanced("Confirmar", btn_confirm_rect.x, btn_confirm_rect.y, btn_confirm_rect.width, btn_confirm_rect.height)
        ui_button_enhanced("Voltar", btn_back_rect.x, btn_back_rect.y, btn_back_rect.width, btn_back_rect.height)
        
        pygame.display.flip()
        CLOCK.tick(FPS)

def high_scores_screen():
    scores = load_score_data()
    btn_back_details = {"rect": pygame.Rect(WIDTH / 2 - 100, HEIGHT - 100, 200, 55), "text": "Voltar"}
    
    screen_active = True
    while screen_active:
        SCREEN.blit(recordes_imagem, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back_details["rect"].collidepoint(event.pos): pygame.time.delay(100); return
        
        draw_text("Recordes", FONT_LARGE, WHITE, WIDTH / 2, HEIGHT / 7, center=True)

        # --- Melhor Pontuação ---
        hs_title_y, hs_entry_y = HEIGHT / 4.5, HEIGHT / 4.5 + 45
        draw_text("Melhor Pontuação:", FONT_MEDIUM, YELLOW, WIDTH / 2, hs_title_y, center=True)

        if scores["high_score"]:
            hs = scores["high_score"]
            texto = f"{hs['name']}: {hs['score']} Pts, {hs['coins']} Moedas"
            if 'data' in hs and 'hora' in hs:
                texto += f" | {hs['data']} {hs['hora']}"
            draw_text(texto, FONT_SMALL, SCORE_TEXT_COLOR, WIDTH / 2, hs_entry_y, center=True)
        else:
            draw_text("Nenhum recorde ainda!", FONT_SMALL, SCORE_TEXT_COLOR, WIDTH / 2, hs_entry_y, center=True)

        # --- Últimas 5 Partidas ---
        recent_title_y, recent_start_y = hs_entry_y + 70, hs_entry_y + 70 + 50
        draw_text("Últimas 5 Partidas:", FONT_MEDIUM, YELLOW, WIDTH / 2, recent_title_y, center=True)

        if not scores["recent_scores"]:
            draw_text("Nenhuma partida recente.", FONT_SMALL, SCORE_TEXT_COLOR, WIDTH / 2, recent_start_y, center=True)
        else:
            for i, entry in enumerate(scores["recent_scores"]):
                texto = f"{i+1}. {entry['name']}: {entry['score']} Pts, {entry['coins']} Moedas"
                if 'data' in entry and 'hora' in entry:
                    texto += f" | {entry['data']} {entry['hora']}"
                draw_text(texto, FONT_SMALL, SCORE_TEXT_COLOR, WIDTH / 2, recent_start_y + i * 35, center=True)

        # --- Botão Voltar ---
        ui_button_enhanced(btn_back_details["text"], btn_back_details["rect"].x, btn_back_details["rect"].y, btn_back_details["rect"].width, btn_back_details["rect"].height)

        pygame.display.flip()
        CLOCK.tick(FPS)

# --- Funções de Jogo e Menus 
def main_menu(): 
    btn_w, btn_h, spacing = 200, 50, 10 # dimensões
    start_y_btns = HEIGHT / 1.6 # Posição Y inicial dos botões
    btn_x_pos = WIDTH / 2 - btn_w / 2 # Centralizando os botões horizontalmente
  
    # Definindo as geometrias dos botões uma vez
    buttons_layout = [
        {"text": "Iniciar", "rect": pygame.Rect(btn_x_pos, start_y_btns, btn_w, btn_h), "action": "start_game"},
        {"text": "Instruções", "rect": pygame.Rect(btn_x_pos, start_y_btns + (btn_h + spacing), btn_w, btn_h), "action": "instructions"},
        {"text": "Recordes", "rect": pygame.Rect(btn_x_pos, start_y_btns + 2 * (btn_h + spacing), btn_w, btn_h), "action": "high_scores"},
        {"text": "Sair", "rect": pygame.Rect(btn_x_pos, start_y_btns + 3 * (btn_h + spacing), btn_w, btn_h), "action": "quit"}
    ]

    while True:
        SCREEN.blit(menu_background_img, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn_info in buttons_layout:
                    if btn_info["rect"].collidepoint(event.pos):
                        pygame.time.delay(100) # Pequeno delay visual no clique
                        if btn_info["action"] == "start_game": return "start_game"
                        elif btn_info["action"] == "instructions": instructions_menu(); break 
                        elif btn_info["action"] == "high_scores": high_scores_screen(); break 
                        elif btn_info["action"] == "quit": pygame.quit(); sys.exit()
        
        for btn_info in buttons_layout: # Desenha os botões usando função original `button`
                                        # mas sem checar o retorno dela aqui, pois o clique é tratado acima.
            button(btn_info["text"], btn_info["rect"].x, btn_info["rect"].y, btn_info["rect"].width, btn_info["rect"].height)
        
        pygame.display.flip()
        CLOCK.tick(FPS)

def instructions_menu(): 
    btn_w, btn_h = 200, 50
    btn_back_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT - 130, btn_w, btn_h)
    
    while True:
        SCREEN.blit(instructions_background_img, (0, 0))
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_back_rect.collidepoint(e.pos): pygame.time.delay(100); return
        
        lines = ["→ Use as teclas A e D para se mover para os lados", "→ Use a tecla W para pular",
                 "→ Evite os morcegos que voam pelo caminho", "→ Suba o mais alto que conseguir para ganhar pontos", "→ Clique ESC para pausar o jogo", "→ Segure W para pular alto, aperte rapidamente para pular pouco", "→ Boa sorte!"]
        y_start_txt, line_spacing_txt = HEIGHT // 3, 35
        for i, line in enumerate(lines):
            draw_text(line, FONT_SMALL, (0,0,0), WIDTH // 2 + 2, y_start_txt + i * line_spacing_txt + 2, center=True) # Sombra
            draw_text(line, FONT_SMALL, YELLOW, WIDTH // 2, y_start_txt + i * line_spacing_txt, center=True)
        
        button("Voltar", btn_back_rect.x, btn_back_rect.y, btn_back_rect.width, btn_back_rect.height) # Seu botão
        pygame.display.flip()
        CLOCK.tick(FPS)
        
    #selecionar dificuldade 
def select_difficulty(): 
    difficulties_cfg = {
        "Fácil": {"enemy_speed_min": 0.5, "enemy_speed_max": 1.0, "name": "Fácil"},
        "Médio": {"enemy_speed_min": 1.0, "enemy_speed_max": 2.0, "name": "Médio"},
        "Difícil": {"enemy_speed_min": 1.5, "enemy_speed_max": 3.0, "name": "Difícil"},
    }
    order = ["Fácil", "Médio", "Difícil"]
    btn_w, btn_h, spacing = 200, 50, 20
    start_y_sel = HEIGHT / 2 - (len(order) * btn_h + (len(order)-1) * spacing) / 2
    
    buttons_geom = []
    current_y = start_y_sel
    for level_name in order:
        buttons_geom.append({"text": level_name, "rect": pygame.Rect(WIDTH / 2 - btn_w / 2, current_y, btn_w, btn_h), "config": difficulties_cfg[level_name]})
        current_y += btn_h + spacing

    while True:
        SCREEN.fill(BLACK)
        draw_text("Selecione a Dificuldade", FONT_LARGE, WHITE, WIDTH / 2, HEIGHT / 4, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn_info in buttons_geom:
                    if btn_info["rect"].collidepoint(event.pos):
                        pygame.time.delay(100) 
                        return btn_info["config"]
        
        for btn_info in buttons_geom: 
            button(btn_info["text"], btn_info["rect"].x, btn_info["rect"].y, btn_info["rect"].width, btn_info["rect"].height)
        
        pygame.display.flip()
        CLOCK.tick(FPS)

def pause_menu(): 
    options, selected_idx = ["Continuar", "Sair"], 0
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,128))
    
    opt_rects = []
    for i in range(len(options)):
         opt_rects.append(pygame.Rect(WIDTH // 2 - 125, HEIGHT // 2 -30 + i * 80, 250, 60)) 

    while True:
        SCREEN.blit(overlay, (0,0)) # Desenha o overlay por cima do jogo pausado 
        draw_text("PAUSADO", FONT_LARGE, WHITE, WIDTH // 2, HEIGHT // 2 - 120, center=True)
        mouse_p = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "continue"
                if e.key == pygame.K_UP: selected_idx = (selected_idx - 1 + len(options)) % len(options)
                if e.key == pygame.K_DOWN: selected_idx = (selected_idx + 1) % len(options)
                if e.key == pygame.K_RETURN:
                    if selected_idx == 0: return "continue"
                    elif selected_idx == 1: return "exit_to_main_menu" # Alterado para sair para o menu
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(opt_rects):
                    if r.collidepoint(e.pos):
                        if i == 0: return "continue"
                        elif i == 1: return "exit_to_main_menu"
        
        for i, option_txt in enumerate(options):
            r = opt_rects[i]
            color = (200,200,0) if i == selected_idx or r.collidepoint(mouse_p) else (255,255,255)
            pygame.draw.rect(SCREEN, color, r, border_radius=10)
            draw_text(option_txt, FONT_SMALL, BLACK, r.centerx, r.centery, center=True) # Texto do botão
        
        pygame.display.flip()
        CLOCK.tick(FPS) # Manter FPS para menu responsivo

# --- SEU GAME LOOP  ---
def game_loop(player_speed, enemy_speed_min, enemy_speed_max):
    # Carrega o ícone da moeda e prepara para a animação de pulsar
    coin_icon_original = pygame.image.load("recursos/frames/CoinFrame/frame_0.png").convert_alpha()
    
    pulse_angle = 0
    pulse_speed = 0.05
    base_icon_size = 40
    pulse_amplitude = 4
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    moedas = 0

    initial_platform = Platform(0, HEIGHT - 40, WIDTH, 100, image_file="recursos/mainImages/chao.png")
    platforms.add(initial_platform)
    last_y = initial_platform.rect.top

    platform_count = 1

    while len(platforms) < 8:
        if platform_count == 1:
            new_y = last_y - random.randint(40, 60)
        else:
            new_y = last_y - random.randint(80, max_vertical_gap)

        largura = random.randint(80, 100)
        candidates = [p for p in platforms if p.rect.top > new_y]
        if candidates:
            closest_platform = min(candidates, key=lambda p: p.rect.top)
            base_center_x = closest_platform.rect.x + closest_platform.rect.width // 2
            x_min = base_center_x - max_horizontal_gap
            x_max = base_center_x + max_horizontal_gap
            x_min = max(largura // 2, x_min)
            x_max = min(WIDTH - largura // 2, x_max)
            new_center_x = random.randint(int(x_min), int(x_max))
            new_x = new_center_x - largura // 2
        else:
            new_x = random.randint(0, WIDTH - largura)

        new_platform = Platform(new_x, new_y, largura, 40)
        platforms.add(new_platform)
        platform_count += 1

        if platform_count % 5 == 0:
            coin_x = new_x + largura // 2
            coin_y = new_y - 15
            coins.add(Coin(coin_x, coin_y))
        last_y = new_y

    enemies = pygame.sprite.Group()
    decorative_diamonds = pygame.sprite.Group() # Adiciona o grupo para os diamantes decorativos
    for _ in range(4):
        ex = random.randint(0, WIDTH - 40)
        ey = random.randint(100, HEIGHT - 140)
        enemies.add(Enemy(ex, ey, enemy_speed_min, enemy_speed_max))

    # Adiciona diamantes decorativos
    for _ in range(5): # Adiciona 5 diamantes
        dx = random.randint(0, WIDTH - 30)
        dy = random.randint(100, HEIGHT - 100)
        decorative_diamonds.add(DecorativeDiamond(dx, dy))

    player = Player(WIDTH // 2, HEIGHT - 100, player_speed)
    for p in platforms: # Marca o chão inicial como visitado
        if p.rect.top >= HEIGHT - 50:
            player.visited_platforms.add(id(p))

    camera_y_original_var = 0 

    while True: # Loop interno do jogo
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    action_from_pause = pause_menu() # função de pause
                    if action_from_pause == "exit_to_main_menu": # Se pause_menu instruir sair
                        return player.score, moedas, True # True indica que saiu para o menu
                    # Se "continue", o jogo apenas continua daqui
        
        player.update(platforms)
        enemies.update()
        decorative_diamonds.update() # Atualiza os diamantes decorativos
        coins.update()

        collected_coins_list = pygame.sprite.spritecollide(player, coins, True)
        if collected_coins_list:
            if 'coin_sound' in globals(): coin_sound.play()
            moedas += len(collected_coins_list)

        if not player.alive:
            return player.score, moedas, False # False indica game over normal

        if pygame.sprite.spritecollideany(player, enemies):
            return player.score, moedas, False # False indica game over normal

        if player.rect.top < HEIGHT // 3:
            diff = HEIGHT // 3 - player.rect.top
            player.rect.top = HEIGHT // 3
            camera_y_original_var += diff 

            # Loop para mover plataformas e remover as que saem da tela
            for p_sprite in list(platforms): # Usar list() para permitir remoção durante iteração
                p_sprite.rect.y += diff
                if p_sprite.rect.top > HEIGHT:
                    platforms.remove(p_sprite)
                    if id(p_sprite) in player.visited_platforms: # Mantém a consistência
                        player.visited_platforms.remove(id(p_sprite))
            
            # Loop para mover inimigos e remover os que saem da tela
            for enemy_sprite in list(enemies):
                enemy_sprite.rect.y += diff
                if enemy_sprite.rect.top > HEIGHT: # Se o inimigo saiu da tela por baixo
                    enemies.remove(enemy_sprite)


            # Loop para mover moedas e remover as que saem da tela
            for coin_sprite in list(coins):
                coin_sprite.rect.y += diff
                if coin_sprite.rect.top > HEIGHT:
                    coins.remove(coin_sprite)

            # lógica de geração de novas plataformas
            highest_y_val = min(p.rect.top for p in platforms) if platforms else HEIGHT 
            while highest_y_val > 50:
                new_y_val = highest_y_val - random.randint(60, max_vertical_gap)
                largura_val = random.randint(80, 100)
                candidates_val = [p for p in platforms if p.rect.top > new_y_val] # Deve ser < new_y_val para plataformas acima
               
                if candidates_val: # pega plataformas *abaixo* da nova plataforma
                    closest_platform_val = min(candidates_val, key=lambda p: p.rect.top)
                    base_center_x_val = closest_platform_val.rect.x + closest_platform_val.rect.width // 2
                    x_min_val = base_center_x_val - max_horizontal_gap
                    x_max_val = base_center_x_val + max_horizontal_gap
                    x_min_val = max(largura_val // 2, x_min_val)
                    x_max_val = min(WIDTH - largura_val // 2, x_max_val)
                    new_center_x_val = random.randint(int(x_min_val), int(x_max_val))
                    new_x_val = new_center_x_val - largura_val // 2
                else:
                    new_x_val = random.randint(0, WIDTH - largura_val)

                new_platform_inst = Platform(new_x_val, new_y_val, largura_val, 40)
                platforms.add(new_platform_inst)
                platform_count += 1 # contagem

                if platform_count % 5 == 0: #  lógica de moedas
                    coin_x_val = new_x_val + largura_val // 2
                    coin_y_val = new_y_val - 15
                    coins.add(Coin(coin_x_val, coin_y_val))

                # lógica de geração de inimigos
                for _ in range(random.randint(1, 2)):
                    ex_val = new_x_val + random.randint(-100, 250) # X relativo à nova plataforma
                    ey_val = new_y_val - random.randint(250, 350) # Y acima da nova plataforma
                    ex_val = max(0, min(ex_val, WIDTH - 40)) # Garante dentro da tela
                    ey_val = max(0, ey_val) # Garante dentro da tela
                    enemies.add(Enemy(ex_val, ey_val, enemy_speed_min, enemy_speed_max))
                
                highest_y_val = new_y_val # Atualiza para a próxima iteração do while


        SCREEN.blit(background_image_game, (0, 0)) # Usar a imagem de fundo do jogo
        for p_item in platforms: SCREEN.blit(p_item.image, p_item.rect) # Desenhar individualmente
        enemies.draw(SCREEN)
        decorative_diamonds.draw(SCREEN) # Desenha os diamantes decorativos
        coins.draw(SCREEN)
        SCREEN.blit(player.image, player.rect)
    
    # Lógica para fazer o ícone pulsar e desenhá-lo na tela
        pulse_angle += pulse_speed
        scale_offset = math.sin(pulse_angle) * pulse_amplitude
        current_size = int(base_icon_size + scale_offset)

        # Redimensiona a imagem original
        pulsing_icon = pygame.transform.scale(coin_icon_original, (current_size, current_size))

        # Posiciona no canto superior direito com uma pequena margem
        icon_rect = pulsing_icon.get_rect(topright=(WIDTH - 15, 15))

        SCREEN.blit(pulsing_icon, icon_rect)


        draw_text(f"Pontos: {player.score}  - Press ESC to Pause Game.", FONT_SMALL, WHITE, 10, 10, center=False) 
        draw_text(f"Moedas: {moedas}", FONT_SMALL, YELLOW, 10, 40, center=False) 

        pygame.display.flip()
        CLOCK.tick(FPS)
    # Fim do loop while True do jogo
    return player.score, moedas, False # Retorno padrão se o loop terminar por outra razão improvável aqui


# --- GAME_OVER  ---

def game_over_screen_original(current_score, collected_coins, difficulty_settings, player_name_for_display):
    if 'gameover_sound' in globals(): gameover_sound.play() # Toca o som de game over

   
    def draw_text_shadow(text, font, color, x, y, center=True):
        shadow_color = (0, 0, 0)
        shadow_offset = 2
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
            shadow_rect = rect.copy()
            shadow_rect.center = (x + shadow_offset, y + shadow_offset)
        else:
            rect.topleft = (x, y)
            shadow_rect = rect.copy()
            shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)
        SCREEN.blit(font.render(text, True, shadow_color), shadow_rect)
        SCREEN.blit(surf, rect)
            
    btn_restart_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
    btn_exit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

    while True:
        SCREEN.blit(game_over_bg_img, (0, 0)) 

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True # Reiniciar
                if e.key == pygame.K_ESCAPE: return False 
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # A função button original tem seu próprio delay e update.
                # Para consistência com o clique único, verificamos a colisão aqui.
                if btn_restart_rect.collidepoint(e.pos):
                    # O button original faz o display.update(rect) e time.delay(100)
                    # Para evitar isso aqui e deixar o flip principal cuidar, não chamamos o button para checar o clique
                    pygame.time.delay(100) # Adicionando o delay aqui
                    return True 
                if btn_exit_rect.collidepoint(e.pos):
                    pygame.time.delay(100)
                    return False # Modificado para retornar False para ir ao menu, em vez de sys.exit()

        # Desenha os textos e botões
        draw_text_shadow(f"{player_name_for_display}, sua pontuação foi: {current_score}", FONT_SMALL, WHITE, WIDTH//2, HEIGHT//4 + 40)
        draw_text_shadow(f"Moedas coletadas: {collected_coins}", FONT_SMALL, YELLOW, WIDTH//2, HEIGHT//4 + 80)  
        
        draw_text_shadow("Pressione R para reiniciar", FONT_SMALL, WHITE, WIDTH//2, HEIGHT//4 + 130) # Y ajustado
        draw_text_shadow("Pressione ESC para voltar ao menu", FONT_SMALL, WHITE, WIDTH//2, HEIGHT//4 + 160) # Y ajustado

        
        button("Reiniciar", btn_restart_rect.x, btn_restart_rect.y, btn_restart_rect.width, btn_restart_rect.height)
        button("Menu", btn_exit_rect.x, btn_exit_rect.y, btn_exit_rect.width, btn_exit_rect.height) # Texto alterado

        pygame.display.flip()
        CLOCK.tick(FPS)

# --- Loop Principal do Jogo (main) ---
def main():
    current_player_name = "Jogador" # Nome padrão

    while True: # Loop da aplicação (volta para o menu principal)
        action_from_main_menu = main_menu() #  função main_menu

        if action_from_main_menu == "start_game":
            name_entered = get_player_name_screen()
            if name_entered is None: # Usuário clicou em "Voltar" na tela de nome
                continue # Volta para o main_menu
            current_player_name = name_entered
       

        difficulty_config = select_difficulty() # função select_difficulty
        if difficulty_config is None: # Usuário apertou ESC na seleção de dificuldade
            continue # Volta para o main_menu

        # Loop de Jogo (permite reiniciar o jogo na mesma dificuldade)
        play_again = True
        while play_again:
            # game_loop retorna: score, moedas, saiu_para_menu_pelo_pause (booleano)
            score, moedas, exited_from_pause = game_loop(
                PLAYER_SPEED, 
                difficulty_config["enemy_speed_min"], 
                difficulty_config["enemy_speed_max"]
            )

            if exited_from_pause: # Se saiu do jogo pelo menu de pausa
                play_again = False # Não vai para game_over, volta para o menu principal
                break # Sai do loop `while play_again`

            # Se o jogo terminou normalmente (não por pausa para sair)
            update_and_save_game_score(current_player_name, score, moedas)
            
            # Exibe a tela de game over
            should_restart = game_over_screen_original(score, moedas, difficulty_config, current_player_name)
            
            if not should_restart: # Se o jogador escolheu "Sair para Menu" ou pressionou ESC
                play_again = False # Interrompe o loop de "jogar novamente"
            # Se should_restart for True (pressionou R), o loop `while play_again` continua

if __name__ == "__main__":
    pygame.init() # Garante que está inicializado
    main()
