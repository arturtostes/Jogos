import math

from PPlay.sprite import Sprite
from config import LARGURA, ALTURA


class TiroBoss:
    def __init__(
        self, assets, x, y, vel_x, vel_y, forte=False,
        ondular=False, amplitude_onda=0.0, frequencia_onda=0.0, fase_onda=0.0
    ):
        chave = 'tiro_boss_forte' if forte else 'tiro_boss'
        self.sprite = Sprite(assets[chave])
        self.sprite.set_position(
            x - self.sprite.width / 2,
            y - self.sprite.height / 2,
        )
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.forte = forte

        # O modo ondulado mantém uma trajetória-base reta e aplica uma
        # oscilação perpendicular a ela. Assim o projétil continua indo
        # na direção em que foi disparado, mas desenha uma pequena onda.
        self.ondular = ondular
        self.amplitude_onda = amplitude_onda
        self.frequencia_onda = frequencia_onda
        self.fase_onda = fase_onda
        self.tempo_onda = 0.0
        self.base_x = self.sprite.x
        self.base_y = self.sprite.y

        modulo = max(1.0, math.hypot(vel_x, vel_y))
        self.perp_x = -vel_y / modulo
        self.perp_y = vel_x / modulo

    def atualizar(self, dt):
        if not self.ondular:
            self.sprite.x += self.vel_x * dt
            self.sprite.y += self.vel_y * dt
            return

        self.tempo_onda += dt
        self.base_x += self.vel_x * dt
        self.base_y += self.vel_y * dt

        deslocamento = math.sin(
            self.tempo_onda * self.frequencia_onda + self.fase_onda
        ) * self.amplitude_onda

        self.sprite.x = self.base_x + self.perp_x * deslocamento
        self.sprite.y = self.base_y + self.perp_y * deslocamento

    def saiu_da_tela(self):
        margem = 80
        return (
            self.sprite.x + self.sprite.width < -margem
            or self.sprite.x > LARGURA + margem
            or self.sprite.y + self.sprite.height < -margem
            or self.sprite.y > ALTURA + margem
        )

    def colidiu_com(self, outro_sprite):
        return self.sprite.collided(outro_sprite)

    def desenhar(self):
        self.sprite.draw()
