import random
from PPlay.sprite import Sprite
from config import LARGURA, CHAO, ALT_INIMIGO, OFFSET_CHAO_INIMIGO, VEL_MUNDO, GRAVIDADE


class Inimigo:
    def __init__(self, assets, fase=1):
        self.configs = {
            'lesma': {
                'andar': assets['lesma_andando'],
                'morrer': assets['lesma_morre'],
                'frames_andar': 4,
                'frames_morrer': 4,
                'voador': False,
                'tempo_animacao': 1200,
                'multiplicador_vel': 1.0,
            },
            'porco': {
                'andar': assets['porco_andando'],
                'morrer': assets['porco_morre'],
                'frames_andar': 4,
                'frames_morrer': 4,
                'voador': False,
                'tempo_animacao': 450,
                'multiplicador_vel': 1.0,
            },
            'passaro': {
                'andar': assets['passaro_voando'],
                'morrer': assets['passaro_morre'],
                'frames_andar': 4,
                'frames_morrer': 4,
                'voador': True,
                'tempo_animacao': 450,
                'multiplicador_vel': 1.3,
            },
            'carangueijo': {
                'andar': assets['carangueijo_andando'],
                'morrer': assets['carangueijo_morre'],
                'frames_andar': 4,
                'frames_morrer': 4,
                'voador': False,
                'tempo_animacao': 450,
                'multiplicador_vel': 1.0,
            },
        }

        self.tipo = random.choice(list(self.configs.keys()))
        self.config = self.configs[self.tipo]

        self.sprite = Sprite(self.config['andar'], self.config['frames_andar'])
        self.sprite.set_sequence_time(
            0,
            self.config['frames_andar'],
            self.config['tempo_animacao'],
            True,
        )

        y_chao_inimigo = CHAO - ALT_INIMIGO + OFFSET_CHAO_INIMIGO

        if self.config['voador']:
            y = random.randint(CHAO - 225, CHAO - 205)
        else:
            y = y_chao_inimigo + self.config.get('offset_y', 0)

        self.sprite.set_position(LARGURA, y)

        self.morto = False

        # Progressao de resistencia por fase. Os inimigos comuns ficam
        # gradualmente mais resistentes para acompanhar armas e upgrades.
        self.fase = max(1, min(5, int(fase)))
        vidas_por_fase = {1: 2, 2: 3, 3: 4, 4: 6, 5: 8}
        self.vida_maxima = vidas_por_fase[self.fase]
        self.vida = self.vida_maxima
        self.tempo_hit = 0
        self.caindo = False
        self.vel_y_morte = 0

    def atualizar(self, dt):
        self.sprite.x -= VEL_MUNDO * self.config['multiplicador_vel'] * dt
        self.sprite.update()

        if self.tempo_hit > 0:
            self.tempo_hit -= dt
            if self.tempo_hit < 0:
                self.tempo_hit = 0

        if self.morto and self.caindo:
            self.vel_y_morte += GRAVIDADE * dt
            self.sprite.y += self.vel_y_morte * dt

            y_chao_morte = (
                CHAO - self.sprite.height + OFFSET_CHAO_INIMIGO
                + self.config.get('offset_y', 0)
            )

            if self.sprite.y >= y_chao_morte:
                self.sprite.y = y_chao_morte
                self.vel_y_morte = 0
                self.caindo = False

    def receber_tiro(self, dano=1):
        if self.morto:
            return

        self.vida -= dano
        self.tempo_hit = 0.25
        self.sprite.x += 14

        if self.vida <= 0:
            self.matar()

    def matar(self):
        x = self.sprite.x
        y = self.sprite.y
        caminho_morte = self.config['morrer']

        if caminho_morte is not None:
            morte = Sprite(caminho_morte, self.config['frames_morrer'])
            morte.set_sequence_time(0, self.config['frames_morrer'], 600, False)
            morte.set_position(x, y)
            self.sprite = morte

        self.morto = True

        if self.tipo == 'passaro':
            self.caindo = True
            self.vel_y_morte = 0
        else:
            self.caindo = False
            self.vel_y_morte = 0

    def saiu_da_tela(self):
        return self.sprite.x + self.sprite.width < 0

    def colidiu_com(self, outro_sprite):
        return outro_sprite.collided(self.sprite)

    def desenhar(self):
        desenhar_inimigo = True

        if self.tempo_hit > 0 and not self.morto:
            if int(self.tempo_hit / 0.04) % 2 == 0:
                desenhar_inimigo = False

        if desenhar_inimigo:
            self.sprite.draw()
