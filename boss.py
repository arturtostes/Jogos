import math
import pygame
from PPlay.sprite import Sprite
from PPlay.window import Window

from config import LARGURA, ALTURA, CHAO
from tiro_boss import TiroBoss


class Boss:
    VIDAS = {
        1: 15,
        2: 32,  # lesma: mais tank porque fica muito exposta aos tiros
        3: 38,  # porco: mais tank porque atravessa a arena e recebe muitos tiros
        4: 40,
        5: 120,
    }

    def __init__(self, assets, fase):
        self.assets = assets
        self.fase = fase
        nomes = {
            1: 'FALCAO DA TEMPESTADE',
            2: 'LESMA COLOSSAL',
            3: 'JAVALI DE FERRO',
            4: 'GUARDIAO VIOLETA',
            5: 'IMPERADOR CARMESIM',
        }
        self.nome = nomes.get(fase, 'CHEFE')

        self.sprite = Sprite(assets[f'boss_{fase}'], 4)
        self.sprite.set_sequence_time(0, 4, 520 if fase < 5 else 400, True)

        self.x_base = LARGURA - (285 if fase < 5 else 310)

        # Lesma e porco lutam mais perto do chao; os demais chefes ficam aereos.
        if fase in (2, 3):
            self.y_base = CHAO - self.sprite.height + 18
        else:
            self.y_base = 120 if fase < 5 else 95

        self.sprite.set_position(LARGURA + 30, self.y_base)

        self.vida_maxima = self.VIDAS[fase]
        self.vida = self.vida_maxima
        self.morto = False

        self.entrando = True
        self.tempo = 0.0
        self.tempo_hit = 0.0

        self.direcao_y = 1
        self.cooldown_tiro = 1.0
        self.cooldown_especial = 4.0
        self.cooldown_invocar = 6.0

        self.rajada_restante = 0
        self.tempo_rajada = 0.0
        self.intervalo_rajada = 0.2

        self.estado_dash = 0
        self.x_retorno = self.x_base
        self.tempo_espera_dash = 0.0

        self.estado_mergulho = 0
        self.y_retorno = self.y_base

        self.protegido = False
        self.tempo_protecao = 0.0
        self.aviso_protecao = False

    def centro(self):
        return (
            self.sprite.x + self.sprite.width / 2,
            self.sprite.y + self.sprite.height / 2,
        )

    def vida_percentual(self):
        if self.vida_maxima <= 0:
            return 0
        return max(0.0, self.vida / self.vida_maxima)

    def fase_final_atual(self):
        if self.fase != 5:
            return 0
        pct = self.vida_percentual()
        if pct > 0.70:
            return 1
        if pct > 0.35:
            return 2
        return 3

    def receber_tiro(self, dano=1):
        if self.morto or self.protegido or self.entrando:
            return False

        self.vida -= dano
        self.tempo_hit = 0.18
        self.sprite.x += 7

        if self.vida <= 0:
            self.vida = 0
            self.morto = True

        return True

    def _mover_vertical(self, dt, velocidade, y_min=65, y_max=400):
        self.sprite.y += self.direcao_y * velocidade * dt

        if self.sprite.y <= y_min:
            self.sprite.y = y_min
            self.direcao_y = 1
        elif self.sprite.y + self.sprite.height >= y_max + self.sprite.height:
            self.sprite.y = y_max
            self.direcao_y = -1

    def _tiro_direcionado(self, player, velocidade=390, forte=False):
        bx, by = self.centro()
        alvo = player.sprite_atual()
        px = alvo.x + alvo.width / 2
        py = alvo.y + alvo.height / 2

        dx = px - bx
        dy = py - by
        dist = max(1.0, math.hypot(dx, dy))

        return TiroBoss(
            self.assets,
            bx,
            by,
            dx / dist * velocidade,
            dy / dist * velocidade,
            forte,
        )

    def _tiro_direcionado_ondulado(
        self, player, velocidade=320, fase_onda=0.0, amplitude=20
    ):
        bx, by = self.centro()
        alvo = player.sprite_atual()
        px = alvo.x + alvo.width / 2
        py = alvo.y + alvo.height / 2

        dx = px - bx
        dy = py - by
        dist = max(1.0, math.hypot(dx, dy))

        return TiroBoss(
            self.assets,
            bx,
            by,
            dx / dist * velocidade,
            dy / dist * velocidade,
            False,
            ondular=True,
            amplitude_onda=amplitude,
            frequencia_onda=6.0,
            fase_onda=fase_onda,
        )

    def _tiro_angulo(self, angulo, velocidade=380, forte=False):
        bx, by = self.centro()
        return TiroBoss(
            self.assets,
            bx,
            by,
            math.cos(angulo) * velocidade,
            math.sin(angulo) * velocidade,
            forte,
        )

    def _angulo_para_player(self, player):
        bx, by = self.centro()
        alvo = player.sprite_atual()
        px = alvo.x + alvo.width / 2
        py = alvo.y + alvo.height / 2
        return math.atan2(py - by, px - bx)

    def _atualizar_rajada(self, dt, player, tiros, velocidade=420, forte=False):
        if self.rajada_restante <= 0:
            return

        self.tempo_rajada -= dt
        if self.tempo_rajada <= 0:
            tiros.append(self._tiro_direcionado(player, velocidade, forte))
            self.rajada_restante -= 1
            self.tempo_rajada = self.intervalo_rajada

    def _iniciar_rajada(self, quantidade, intervalo):
        if self.rajada_restante > 0:
            return
        self.rajada_restante = quantidade
        self.intervalo_rajada = intervalo
        self.tempo_rajada = 0

    def _atualizar_fase1(self, dt, player, tiros):
        self._mover_vertical(dt, 125, 80, 370)

        self.cooldown_tiro -= dt
        if self.cooldown_tiro <= 0:
            tiros.append(self._tiro_direcionado(player, 390))
            self.cooldown_tiro = 1.55

        self.cooldown_especial -= dt
        if self.estado_dash == 0 and self.cooldown_especial <= 0:
            self.estado_dash = 1
            self.x_retorno = self.x_base
            self.cooldown_especial = 5.4

        if self.estado_dash == 1:
            self.sprite.x -= 440 * dt
            if self.sprite.x <= LARGURA - 520:
                self.estado_dash = 2
        elif self.estado_dash == 2:
            self.sprite.x += 360 * dt
            if self.sprite.x >= self.x_retorno:
                self.sprite.x = self.x_retorno
                self.estado_dash = 0

    def _atualizar_fase2(self, dt, player, tiros):
        # Lesma gigante: fica no chao, desliza devagar e dispara uma rajada
        # simples. De tempos em tempos avanca um pouco e volta.
        self.sprite.y = self.y_base + math.sin(self.tempo * 1.8) * 5

        if self.estado_dash == 0:
            self.sprite.x = self.x_base + math.sin(self.tempo * 0.75) * 35

        self.cooldown_tiro -= dt

        # Rajada da lesma: 3 tiros em sequencia. Cada tiro mira a posicao
        # atual do player no momento em que sai e segue uma trajetoria reta
        # com uma ondulacao leve ao redor dela. Isso deixa o ataque legivel
        # e esquivavel sem perder a personalidade da lesma.
        if self.cooldown_tiro <= 0 and self.rajada_restante <= 0:
            self.rajada_restante = 3
            self.tempo_rajada = 0.0
            self.intervalo_rajada = 0.24
            self.cooldown_tiro = 3.55

        if self.rajada_restante > 0:
            self.tempo_rajada -= dt
            if self.tempo_rajada <= 0:
                indice = 3 - self.rajada_restante
                fases_onda = (0.0, 2.1, 4.2)
                tiros.append(
                    self._tiro_direcionado_ondulado(
                        player,
                        velocidade=315,
                        fase_onda=fases_onda[indice],
                        amplitude=18,
                    )
                )
                self.rajada_restante -= 1
                self.tempo_rajada = self.intervalo_rajada

        self.cooldown_especial -= dt
        if self.estado_dash == 0 and self.cooldown_especial <= 0:
            self.estado_dash = 1
            self.x_retorno = self.x_base
            self.cooldown_especial = 6.0

        if self.estado_dash == 1:
            self.sprite.x -= 230 * dt
            if self.sprite.x <= LARGURA - 470:
                self.estado_dash = 2
        elif self.estado_dash == 2:
            self.sprite.x += 200 * dt
            if self.sprite.x >= self.x_retorno:
                self.sprite.x = self.x_retorno
                self.estado_dash = 0

    def _atualizar_fase3(self, dt, player, tiros):
        # Porco gigante: menos tiros e uma investida que atravessa a arena inteira.
        # Ele vai ate o lado esquerdo, obrigando o jogador a pular, espera cerca
        # de 3 segundos e depois retorna para a posicao inicial no lado direito.
        self.sprite.y = self.y_base

        self.cooldown_tiro -= dt
        if self.cooldown_tiro <= 0:
            # O porco agora mira diretamente na posicao do jogador no instante
            # do disparo. Antes eram dois tiros diagonais desviados do alvo,
            # entao quase nunca ameaçavam o player de verdade.
            tiros.append(self._tiro_direcionado(player, 340))
            self.cooldown_tiro = 3.15

        self.cooldown_especial -= dt
        if self.estado_dash == 0 and self.cooldown_especial <= 0:
            self.estado_dash = 1
            self.x_retorno = self.x_base
            self.tempo_espera_dash = 0.0

        # 1 = investindo para a esquerda
        if self.estado_dash == 1:
            self.sprite.x -= 560 * dt
            limite_esquerdo = 18
            if self.sprite.x <= limite_esquerdo:
                self.sprite.x = limite_esquerdo
                self.estado_dash = 2
                self.tempo_espera_dash = 3.0

        # 2 = parado no lado esquerdo por aproximadamente 3 segundos
        elif self.estado_dash == 2:
            self.tempo_espera_dash -= dt
            if self.tempo_espera_dash <= 0:
                self.estado_dash = 3

        # 3 = retornando para o lado direito
        elif self.estado_dash == 3:
            self.sprite.x += 420 * dt
            if self.sprite.x >= self.x_retorno:
                self.sprite.x = self.x_retorno
                self.estado_dash = 0
                self.cooldown_especial = 5.6

        # A invocacao de inimigos foi movida para a fase 4.
        return False

    def _atualizar_fase4(self, dt, player, tiros):
        # Continua sendo uma luta mais intensa, mas com janelas claras para
        # esquiva. Os inimigos extras permanecem como a principal pressao.
        self._mover_vertical(dt, 140, 70, 355)

        if self.protegido:
            self.tempo_protecao -= dt
            if self.tempo_protecao <= 0:
                self.protegido = False
                ang = self._angulo_para_player(player)
                for desvio in (-0.30, 0, 0.30):
                    tiros.append(self._tiro_angulo(ang + desvio, 390, True))
                self.cooldown_especial = 5.5
        else:
            self.cooldown_especial -= dt
            if self.cooldown_especial <= 0:
                self.protegido = True
                self.tempo_protecao = 1.35

        self.cooldown_tiro -= dt
        if self.cooldown_tiro <= 0 and not self.protegido:
            self._iniciar_rajada(4, 0.20)
            self.cooldown_tiro = 3.35
        self._atualizar_rajada(dt, player, tiros, 390)

        self.cooldown_invocar -= dt
        invocar = False
        if self.cooldown_invocar <= 0:
            invocar = True
            self.cooldown_invocar = 7.2

        return invocar

    def _atualizar_final(self, dt, player, tiros):
        etapa = self.fase_final_atual()

        if etapa == 1:
            self._mover_vertical(dt, 150, 55, 360)
            self.cooldown_tiro -= dt
            if self.cooldown_tiro <= 0:
                tiros.append(self._tiro_direcionado(player, 430))
                self.cooldown_tiro = 1.25

        elif etapa == 2:
            self._mover_vertical(dt, 190, 50, 375)

            self.cooldown_tiro -= dt
            if self.cooldown_tiro <= 0:
                self._iniciar_rajada(3, 0.16)
                self.cooldown_tiro = 1.95
            self._atualizar_rajada(dt, player, tiros, 480)

            self.cooldown_especial -= dt
            if self.estado_dash == 0 and self.cooldown_especial <= 0:
                self.estado_dash = 1
                self.x_retorno = self.x_base
                self.cooldown_especial = 4.8

            if self.estado_dash == 1:
                self.sprite.x -= 520 * dt
                if self.sprite.x <= LARGURA - 560:
                    self.estado_dash = 2
            elif self.estado_dash == 2:
                self.sprite.x += 430 * dt
                if self.sprite.x >= self.x_retorno:
                    self.sprite.x = self.x_retorno
                    self.estado_dash = 0

        else:
            self.sprite.x = self.x_base + math.sin(self.tempo * 1.5) * 90
            self.sprite.y = 165 + math.sin(self.tempo * 2.15) * 135

            self.cooldown_tiro -= dt
            if self.cooldown_tiro <= 0:
                ang = self._angulo_para_player(player)
                for desvio in (-0.28, 0, 0.28):
                    tiros.append(self._tiro_angulo(ang + desvio, 500, desvio == 0))
                self.cooldown_tiro = 1.35

            self.cooldown_invocar -= dt
            invocar = False
            if self.cooldown_invocar <= 0:
                invocar = True
                self.cooldown_invocar = 5.0

            self.cooldown_especial -= dt
            if not self.protegido and self.cooldown_especial <= 0:
                self.protegido = True
                self.tempo_protecao = 0.8

            if self.protegido:
                self.tempo_protecao -= dt
                if self.tempo_protecao <= 0:
                    self.protegido = False
                    ang = self._angulo_para_player(player)
                    for desvio in (-0.5, -0.25, 0, 0.25, 0.5):
                        tiros.append(self._tiro_angulo(ang + desvio, 520, True))
                    self.cooldown_especial = 4.2

            return invocar

        return False

    def atualizar(self, dt, player):
        tiros = []
        invocar = False

        if self.morto:
            return tiros, invocar

        self.tempo += dt
        self.sprite.update()

        if self.tempo_hit > 0:
            self.tempo_hit -= dt
            if self.tempo_hit < 0:
                self.tempo_hit = 0

        if self.entrando:
            self.sprite.x -= 270 * dt
            if self.sprite.x <= self.x_base:
                self.sprite.x = self.x_base
                self.entrando = False
                self.cooldown_tiro = 0.8
                self.cooldown_especial = 3.6
            return tiros, invocar

        if self.fase == 1:
            self._atualizar_fase1(dt, player, tiros)
        elif self.fase == 2:
            self._atualizar_fase2(dt, player, tiros)
        elif self.fase == 3:
            invocar = self._atualizar_fase3(dt, player, tiros)
        elif self.fase == 4:
            invocar = self._atualizar_fase4(dt, player, tiros)
        else:
            invocar = self._atualizar_final(dt, player, tiros)

        return tiros, invocar

    def colidiu_com(self, outro_sprite):
        if self.morto:
            return False
        return outro_sprite.collided(self.sprite)

    def desenhar(self):
        if self.morto:
            return

        mostrar = True
        if self.tempo_hit > 0 and not self.protegido:
            mostrar = int(self.tempo_hit / 0.035) % 2 == 1

        if mostrar:
            self.sprite.draw()

        if self.protegido:
            tela = Window.get_screen()
            cx = int(self.sprite.x + self.sprite.width / 2)
            cy = int(self.sprite.y + self.sprite.height / 2)
            raio = int(max(self.sprite.width, self.sprite.height) * 0.57)
            camada = pygame.Surface((raio * 2 + 8, raio * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                camada,
                (100, 205, 255, 48),
                (raio + 4, raio + 4),
                raio,
            )
            pygame.draw.circle(
                camada,
                (180, 235, 255, 200),
                (raio + 4, raio + 4),
                raio,
                4,
            )
            tela.blit(camada, (cx - raio - 4, cy - raio - 4))
