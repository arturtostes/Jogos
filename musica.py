import os
import pygame
from config import VOLUME_MUSICA


class GerenciadorMusica:
    """Controla as quatro trilhas de CHICKEN: THE GAME sem interromper o jogo se o audio falhar."""

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        pasta = os.path.join(base, 'soundtracks')
        self.trilhas = {
            'menu': os.path.join(pasta, 'menu.wav'),
            'fase': os.path.join(pasta, 'fase.wav'),
            'miniboss': os.path.join(pasta, 'miniboss.wav'),
            'boss_final': os.path.join(pasta, 'boss_final.wav'),
        }
        self.atual = None
        self.mudo = False
        self.disponivel = True

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.set_volume(VOLUME_MUSICA)
        except pygame.error:
            self.disponivel = False

    def tocar(self, nome):
        if not self.disponivel or nome == self.atual:
            return
        caminho = self.trilhas.get(nome)
        if not caminho or not os.path.isfile(caminho):
            return
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.0 if self.mudo else VOLUME_MUSICA)
            pygame.mixer.music.play(-1, fade_ms=500)
            self.atual = nome
        except pygame.error:
            self.disponivel = False

    def alternar_mudo(self):
        self.mudo = not self.mudo
        if self.disponivel:
            try:
                pygame.mixer.music.set_volume(0.0 if self.mudo else VOLUME_MUSICA)
            except pygame.error:
                self.disponivel = False
        return self.mudo
