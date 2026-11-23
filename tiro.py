import math
from PPlay.sprite import Sprite
from config import LARG_PLAYER, ALT_PLAYER, LARGURA, ALTURA


class Tiro:
    def __init__(self, assets, player, velocidade=750, dano=1, angulo=0.0,
                 penetracao=1, id_arma='normal'):
        chave = f'tiro_{id_arma}'
        caminho = assets.get(chave, assets.get('tiro_normal', assets['tiro']))
        self.sprite = Sprite(caminho)
        self.sprite.set_position(
            player.x + LARG_PLAYER - 5,
            player.y + ALT_PLAYER / 2 - self.sprite.height / 2,
        )
        self.vel_x = math.cos(angulo) * velocidade
        self.vel_y = math.sin(angulo) * velocidade
        self.dano = dano
        self.acertos_restantes = max(1, int(penetracao))
        self.alvos_acertados = set()

    def atualizar(self, dt):
        self.sprite.x += self.vel_x * dt
        self.sprite.y += self.vel_y * dt

    def pode_acertar(self, alvo):
        return id(alvo) not in self.alvos_acertados

    def registrar_acerto(self, alvo):
        self.alvos_acertados.add(id(alvo))
        self.acertos_restantes -= 1

    def esgotou_penetracao(self):
        return self.acertos_restantes <= 0

    def saiu_da_tela(self):
        return (self.sprite.x > LARGURA or self.sprite.y + self.sprite.height < 0 or self.sprite.y > ALTURA)

    def desenhar(self):
        self.sprite.draw()
