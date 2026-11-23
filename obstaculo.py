import random
import pygame
from PPlay.sprite import Sprite
from config import LARGURA, CHAO, ALT_OBSTACULO, VEL_MUNDO


class Obstaculo:
    def __init__(self, assets):
        self.hitboxes = assets['hitboxes_obstaculos']
        self.sprite = Sprite(assets['obstaculos'], 8)
        self.frame = random.randint(0, 7)
        self.sprite.set_curr_frame(self.frame)

        # Pedra e troncos ficam alguns pixels acima para nao serem
        # escondidos demais pela grama de primeiro plano.
        offsets_altura = {
            2: -8,  # pedra
            3: -8,  # toco
            6: -8,  # tronco deitado
            7: -8,  # pedra grande
        }
        offset_y = offsets_altura.get(self.frame, 0)
        self.sprite.set_position(LARGURA, CHAO - ALT_OBSTACULO + offset_y)

    def atualizar(self, dt):
        self.sprite.x -= VEL_MUNDO * dt

    def saiu_da_tela(self):
        return self.sprite.x + self.sprite.width < 0

    def colidiu_com_player(self, player_sprite):
        rect_frame = self.hitboxes[self.frame]

        hitbox_obstaculo = pygame.Rect(
            int(self.sprite.x + rect_frame.x),
            int(self.sprite.y + rect_frame.y),
            rect_frame.width,
            rect_frame.height,
        )

        margem_x = 18
        margem_cima = 12
        margem_baixo = 8

        hitbox_player = pygame.Rect(
            int(player_sprite.x + margem_x),
            int(player_sprite.y + margem_cima),
            int(player_sprite.width - margem_x * 2),
            int(player_sprite.height - margem_cima - margem_baixo),
        )

        return hitbox_player.colliderect(hitbox_obstaculo)

    def desenhar(self):
        self.sprite.draw()
