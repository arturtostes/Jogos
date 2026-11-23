from PPlay.sprite import Sprite
from config import (
    PLAYER_X, CHAO, ALT_PLAYER, OFFSET_PLAYER_CHAO,
    GRAVIDADE, FORCA_PULO, TEMPO_INVENCIVEL,
    LARGURA, LARG_PLAYER, VEL_PLAYER_BOSS, MARGEM_SALA_BOSS,
    VIDA_MAXIMA_PLAYER,
)


class Player:
    def __init__(self, assets):
        self.x = PLAYER_X
        self.y = CHAO - ALT_PLAYER + OFFSET_PLAYER_CHAO

        self.vel_y = 0
        self.vidas = 3
        self.tempo_invencivel = 0
        self.tempo_pisca = 0
        self.game_over = False
        self.mult_velocidade_boss = 1.0
        self.bonus_invencibilidade = 0.0
        self.vida_inicial = 3
        self.vida_maxima = VIDA_MAXIMA_PLAYER
        self.double_jump_ativo = False
        self.pulos_usados = 0
        self.caindo_morte = False
        self.vel_y_morte = 0.0

        self.andando = Sprite(assets['galinha_andando'], 6)
        self.andando.set_sequence_time(0, 6, 420, True)

        self.pulando = Sprite(assets['galinha_pulando'], 6)
        self.pulando.set_sequence_time(0, 6, 950, False)

        self.parado = Sprite(assets['galinha_parada'])

        self.morrendo = Sprite(assets['galinha_morre'], 4)
        self.morrendo.set_sequence_time(0, 4, 700, False)

        self.no_chao = True
        self.sincronizar_sprites()

    def sincronizar_sprites(self):
        self.andando.set_position(self.x, self.y)
        self.pulando.set_position(self.x, self.y)
        self.parado.set_position(self.x, self.y)
        self.morrendo.set_position(self.x, self.y)

    def atualizar_invencibilidade(self, dt):
        if self.tempo_invencivel > 0:
            self.tempo_invencivel -= dt
            self.tempo_pisca += dt
            if self.tempo_invencivel < 0:
                self.tempo_invencivel = 0

    def atualizar_fisica(self, dt):
        self.vel_y += GRAVIDADE * dt
        self.y += self.vel_y * dt
        self.no_chao = False

        # Nunca deixa o player sair pela parte de cima da tela, inclusive
        # quando o DOUBLE JUMP estiver ativo.
        if self.y < 0:
            self.y = 0
            if self.vel_y < 0:
                self.vel_y = 0

        if self.y + ALT_PLAYER >= CHAO + OFFSET_PLAYER_CHAO:
            self.y = CHAO - ALT_PLAYER + OFFSET_PLAYER_CHAO
            self.vel_y = 0
            self.no_chao = True
            self.pulos_usados = 0

        self.sincronizar_sprites()

    def atualizar_movimento_boss(self, dt, teclado):
        """Libera esquerda/direita somente durante a luta contra o boss."""
        direcao = 0

        if teclado.key_pressed('LEFT') or teclado.key_pressed('A'):
            direcao -= 1
        if teclado.key_pressed('RIGHT') or teclado.key_pressed('D'):
            direcao += 1

        self.x += direcao * VEL_PLAYER_BOSS * self.mult_velocidade_boss * dt

        limite_esquerdo = MARGEM_SALA_BOSS
        limite_direito = LARGURA - LARG_PLAYER - MARGEM_SALA_BOSS

        if self.x < limite_esquerdo:
            self.x = limite_esquerdo
        elif self.x > limite_direito:
            self.x = limite_direito

        self.sincronizar_sprites()


    def aplicar_upgrades(self, upgrades):
        try:
            nivel_vel = max(0, int(upgrades.get('velocidade_player', 0)))
        except (TypeError, ValueError):
            nivel_vel = 0
        try:
            nivel_inv = max(0, int(upgrades.get('invencibilidade', 0)))
        except (TypeError, ValueError):
            nivel_inv = 0

        try:
            nivel_vida = max(0, int(upgrades.get('vida_extra', 0)))
        except (TypeError, ValueError):
            nivel_vida = 0
        try:
            nivel_double = max(0, int(upgrades.get('double_jump', 0)))
        except (TypeError, ValueError):
            nivel_double = 0

        self.mult_velocidade_boss = 1.0 + 0.10 * nivel_vel
        self.bonus_invencibilidade = 0.5 * nivel_inv
        self.vida_inicial = 3 + min(1, nivel_vida)
        self.vida_maxima = VIDA_MAXIMA_PLAYER + min(1, nivel_vida)
        self.double_jump_ativo = nivel_double > 0
        if self.vidas > self.vida_maxima:
            self.vidas = self.vida_maxima

    def resetar_posicao_horizontal(self):
        self.x = PLAYER_X
        self.sincronizar_sprites()

    def restaurar_vidas_fase(self):
        self.vidas = self.vida_inicial
        self.tempo_invencivel = 0
        self.tempo_pisca = 0
        self.pulos_usados = 0

    def reiniciar(self):
        self.x = PLAYER_X
        self.y = CHAO - ALT_PLAYER + OFFSET_PLAYER_CHAO
        self.vel_y = 0
        self.no_chao = True
        self.vidas = 3
        self.tempo_invencivel = 0
        self.tempo_pisca = 0
        self.game_over = False
        self.pulos_usados = 0
        self.caindo_morte = False
        self.vel_y_morte = 0.0

        self.morrendo.stop()
        self.morrendo.set_curr_frame(0)
        self.pulando.stop()
        self.pulando.set_curr_frame(0)
        self.andando.play()
        self.sincronizar_sprites()

    def pode_pular(self):
        if self.no_chao:
            return True
        return self.double_jump_ativo and self.pulos_usados < 2

    def pular(self, forca=None):
        if not self.pode_pular():
            return False

        # No primeiro pulo saindo do chao, pulos_usados vale 0.
        # O DOUBLE JUMP libera exatamente mais um pulo no ar.
        self.pulos_usados += 1
        self.vel_y = FORCA_PULO if forca is None else forca
        self.pulando.stop()
        self.pulando.set_curr_frame(0)
        self.pulando.play()
        self.no_chao = False
        return True

    def curar(self, quantidade=1):
        if self.game_over:
            return False
        vidas_antes = self.vidas
        self.vidas = min(self.vida_maxima, self.vidas + max(0, int(quantidade)))
        return self.vidas > vidas_antes

    def tomar_dano(self):
        if self.tempo_invencivel > 0 or self.game_over:
            return False

        self.vidas -= 1
        self.tempo_invencivel = TEMPO_INVENCIVEL + self.bonus_invencibilidade
        self.tempo_pisca = 0

        if self.vidas <= 0:
            self.vidas = 0
            self.game_over = True
            self.morrendo.stop()
            self.morrendo.set_curr_frame(0)
            self.morrendo.play()
            self.caindo_morte = True
            self.vel_y_morte = max(0.0, self.vel_y)

        return True

    def atualizar_morte(self, dt):
        if not self.game_over:
            return

        if self.caindo_morte:
            self.vel_y_morte += GRAVIDADE * dt
            self.y += self.vel_y_morte * dt
            y_chao = CHAO - ALT_PLAYER + OFFSET_PLAYER_CHAO
            if self.y >= y_chao:
                self.y = y_chao
                self.vel_y_morte = 0
                self.caindo_morte = False

        self.morrendo.set_position(self.x, self.y)

    def sprite_atual(self):
        if self.no_chao:
            return self.andando
        return self.pulando

    def atualizar_animacao(self):
        if self.no_chao:
            self.andando.update()
        else:
            self.pulando.update()

    def desenhar(self):
        desenhar_player = True

        if self.tempo_invencivel > 0:
            if int(self.tempo_pisca / 0.12) % 2 == 1:
                desenhar_player = False

        if desenhar_player:
            self.sprite_atual().draw()

    def desenhar_parado(self):
        self.parado.draw()

    def desenhar_morte(self):
        self.morrendo.update()
        self.morrendo.draw()
