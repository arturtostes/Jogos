import math
import random
import pygame
from PPlay.sprite import Sprite
from PPlay.window import Window

from config import LARGURA, ALTURA, VEL_CORACAO_ESPECIAL


class CoracaoEspecial:
    """Alvo raro de cura: atravessa a tela e precisa receber 3 tiros."""

    def __init__(self, assets):
        self.sprite = Sprite(assets['coracao'])
        self.vida_maxima = 3
        self.vida = self.vida_maxima
        self.destruido = False
        self.tempo = 0.0
        self.y_base = random.randint(405, 425)
        self.sprite.set_position(LARGURA + 30, self.y_base)
        self.velocidade = VEL_CORACAO_ESPECIAL
        self.tempo_hit = 0.0

    def atualizar(self, dt):
        self.tempo += dt
        self.sprite.x -= self.velocidade * dt
        self.sprite.y = self.y_base + math.sin(self.tempo * 4.0) * 8

        if self.tempo_hit > 0:
            self.tempo_hit = max(0.0, self.tempo_hit - dt)

    def receber_tiro(self):
        if self.destruido:
            return False

        self.vida -= 1
        self.tempo_hit = 0.16
        if self.vida <= 0:
            self.vida = 0
            self.destruido = True
            return True
        return False

    def saiu_da_tela(self):
        return self.sprite.x + self.sprite.width < 0

    def desenhar(self):
        tela = Window.get_screen()

        # Halo discreto para deixar claro que este coracao e um alvo especial.
        centro = (
            int(self.sprite.x + self.sprite.width / 2),
            int(self.sprite.y + self.sprite.height / 2),
        )
        raio = int(max(self.sprite.width, self.sprite.height) * 0.72)
        halo = pygame.Surface((raio * 2 + 8, raio * 2 + 8), pygame.SRCALPHA)
        alpha = 70 if self.tempo_hit <= 0 else 150
        pygame.draw.circle(
            halo,
            (255, 225, 235, alpha),
            (halo.get_width() // 2, halo.get_height() // 2),
            raio,
            3,
        )
        tela.blit(
            halo,
            (centro[0] - halo.get_width() // 2, centro[1] - halo.get_height() // 2),
        )

        if not (self.tempo_hit > 0 and int(self.tempo_hit / 0.04) % 2 == 0):
            self.sprite.draw()

        # 3 marcadores de vida embaixo do alvo.
        inicio_x = int(self.sprite.x + self.sprite.width / 2 - 18)
        y = int(self.sprite.y + self.sprite.height + 5)
        for i in range(self.vida_maxima):
            cor = (255, 240, 245) if i < self.vida else (90, 75, 80)
            pygame.draw.circle(tela, cor, (inicio_x + i * 18, y), 5)
