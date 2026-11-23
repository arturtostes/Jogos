import pygame
import sys
from pygame.locals import *

"""
===============================================================================
POWER PPLAY 2.0 - Framework de Alta Performance para Desenvolvimento de Jogos
===============================================================================
Versao local ajustada para CHICKEN: THE GAME:
- resolucao virtual preservada em tela cheia;
- conversao correta do mouse para coordenadas virtuais;
- F11 alterna tela cheia;
- draw_text compativel com size/color/font_name e tamanho/cor/fonte;
- limite de FPS para estabilidade.
===============================================================================
"""


class Window:
    _instance = None
    screen = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Window, cls).__new__(cls)
        return cls._instance

    def __init__(self, largura_virtual=800, altura_virtual=600, titulo='Power PPlay 2.0',
                 resizavel=True, pixel_art=True, fps_maximo=120):
        if hasattr(self, '_already_init'):
            return

        if not pygame.get_init():
            pygame.init()

        self.largura = largura_virtual
        self.altura = altura_virtual
        self.titulo = titulo
        self.pixel_art = pixel_art
        self.resizavel = resizavel
        self.fps_maximo = fps_maximo
        self.fullscreen = False
        self._tamanho_janela = (self.largura, self.altura)

        self._clock = pygame.time.Clock()
        self._delta_time = 0.0
        self.eventos = []
        self.cor_fundo = (0, 0, 0)

        self.real_screen = self._criar_tela_janela(self._tamanho_janela)
        self.screen = pygame.Surface((self.largura, self.altura)).convert_alpha()
        Window.screen = self.screen
        pygame.display.set_caption(self.titulo)

        from .keyboard import Keyboard
        from .mouse import Mouse
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self._already_init = True

    def _flags_janela(self):
        flags = pygame.DOUBLEBUF
        if self.resizavel:
            flags |= pygame.RESIZABLE
        return flags

    def _criar_tela_janela(self, tamanho):
        return pygame.display.set_mode(tamanho, self._flags_janela())

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            Window()
        return cls._instance

    @classmethod
    def get_screen(cls):
        return cls.get_instance().screen

    def set_title(self, title):
        self.titulo = str(title)
        pygame.display.set_caption(self.titulo)

    def set_fullscreen(self, ativo=True):
        ativo = bool(ativo)
        if ativo == self.fullscreen:
            return

        try:
            if ativo:
                if not self.fullscreen:
                    tamanho_atual = self.real_screen.get_size()
                    if tamanho_atual[0] > 0 and tamanho_atual[1] > 0:
                        self._tamanho_janela = tamanho_atual
                self.real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
                self.fullscreen = True
            else:
                self.real_screen = self._criar_tela_janela(self._tamanho_janela)
                self.fullscreen = False
            pygame.display.set_caption(self.titulo)
        except pygame.error:
            # Se o driver nao aceitar fullscreen, o jogo segue em janela.
            self.fullscreen = False
            self.real_screen = self._criar_tela_janela(self._tamanho_janela)

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)

    def screen_to_virtual_coords(self, px, py):
        lw, lh = self.real_screen.get_size()
        if lw < 1 or lh < 1:
            return float(px), float(py)

        ratio = min(lw / self.largura, lh / self.altura)
        if ratio <= 0:
            return float(px), float(py)
        nova_w = self.largura * ratio
        nova_h = self.altura * ratio
        pos_x = (lw - nova_w) / 2.0
        pos_y = (lh - nova_h) / 2.0
        return int((px - pos_x) / ratio), int((py - pos_y) / ratio)

    def get_mouse_position(self):
        return self.screen_to_virtual_coords(*pygame.mouse.get_pos())

    def update(self):
        largura_real, altura_real = self.real_screen.get_size()

        if largura_real < 1 or altura_real < 1:
            pygame.display.flip()
            self.eventos = pygame.event.get()
            self._delta_time = self._clock.tick(self.fps_maximo) / 1000.0
            return

        ratio = min(largura_real / self.largura, altura_real / self.altura)
        nova_w = max(1, int(self.largura * ratio))
        nova_h = max(1, int(self.altura * ratio))
        pos_x = (largura_real - nova_w) // 2
        pos_y = (altura_real - nova_h) // 2

        self.real_screen.fill((0, 0, 0))
        try:
            if self.pixel_art:
                scaled = pygame.transform.scale(self.screen, (nova_w, nova_h))
            else:
                scaled = pygame.transform.smoothscale(self.screen, (nova_w, nova_h))
            self.real_screen.blit(scaled, (pos_x, pos_y))
        except pygame.error:
            self.real_screen.blit(self.screen, (0, 0))

        pygame.display.flip()
        self.screen.fill(self.cor_fundo)

        self.eventos = pygame.event.get()
        for ev in self.eventos:
            if ev.type == QUIT:
                self.close()
            elif ev.type == KEYDOWN and ev.key == K_F11:
                self.toggle_fullscreen()

        self._delta_time = self._clock.tick(self.fps_maximo) / 1000.0

    def delta_time(self):
        return self._delta_time

    def get_fps(self):
        return self._clock.get_fps()

    def set_background_color(self, cor):
        if isinstance(cor, str):
            try:
                self.cor_fundo = pygame.Color(cor)
            except ValueError:
                self.cor_fundo = (0, 0, 0)
        else:
            self.cor_fundo = cor

    def draw_text(self, texto, x, y, tamanho=20, cor=(255, 255, 255), fonte='Arial', **kwargs):
        # Compatibilidade com as duas APIs usadas em diferentes versoes do PPlay.
        tamanho = kwargs.pop('size', tamanho)
        cor = kwargs.pop('color', cor)
        fonte = kwargs.pop('font_name', fonte)
        try:
            f = pygame.font.SysFont(fonte, int(tamanho))
            img = f.render(str(texto), True, cor)
            self.screen.blit(img, (x, y))
        except Exception:
            pass

    def close(self):
        pygame.quit()
        sys.exit()
