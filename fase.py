import random
from config import DURACAO_FASE, TOTAL_FASES, TEMPO_TRANSICAO_BOSS


class GerenciadorFases:
    ESTADO_FASE = 'fase'
    ESTADO_LIMPANDO = 'limpando'
    ESTADO_TRANSICAO_BOSS = 'transicao_boss'
    ESTADO_BOSS = 'boss'
    ESTADO_RECOMPENSA = 'recompensa'
    ESTADO_VITORIA = 'vitoria'

    def __init__(self):
        self.fase_atual = 1
        self.tempo_restante = DURACAO_FASE
        self.estado = self.ESTADO_FASE
        self.tempo_transicao = 0.0
        self.fase_concluida = 0

    def atualizar(self, dt, tela_limpa=False):
        if self.estado == self.ESTADO_FASE:
            self.tempo_restante -= dt
            if self.tempo_restante <= 0:
                self.tempo_restante = 0
                self.estado = self.ESTADO_LIMPANDO
        elif self.estado == self.ESTADO_LIMPANDO:
            if tela_limpa:
                self.estado = self.ESTADO_TRANSICAO_BOSS
                self.tempo_transicao = TEMPO_TRANSICAO_BOSS
        elif self.estado == self.ESTADO_TRANSICAO_BOSS:
            self.tempo_transicao -= dt
            if self.tempo_transicao <= 0:
                self.tempo_transicao = 0
                self.estado = self.ESTADO_BOSS

    def reiniciar(self):
        self.fase_atual = 1
        self.tempo_restante = DURACAO_FASE
        self.estado = self.ESTADO_FASE
        self.tempo_transicao = 0.0
        self.fase_concluida = 0

    def carregar_fase(self, fase):
        self.fase_atual = max(1, min(TOTAL_FASES, int(fase)))
        self.tempo_restante = DURACAO_FASE
        self.estado = self.ESTADO_FASE
        self.tempo_transicao = 0.0
        self.fase_concluida = 0

    def iniciar_recompensa(self):
        self.fase_concluida = self.fase_atual
        self.estado = self.ESTADO_RECOMPENSA
        self.tempo_transicao = 0.0

    def avancar_apos_recompensa(self):
        if self.fase_atual >= TOTAL_FASES:
            self.estado = self.ESTADO_VITORIA
            return False
        self.fase_atual += 1
        self.tempo_restante = DURACAO_FASE
        self.estado = self.ESTADO_FASE
        self.tempo_transicao = 0.0
        return True

    def pode_spawnar_normais(self):
        return self.estado == self.ESTADO_FASE
    def mostrar_timer(self):
        return self.estado == self.ESTADO_FASE
    def em_transicao_boss(self):
        return self.estado == self.ESTADO_TRANSICAO_BOSS
    def em_boss(self):
        return self.estado == self.ESTADO_BOSS
    def em_recompensa(self):
        return self.estado == self.ESTADO_RECOMPENSA
    def em_vitoria(self):
        return self.estado == self.ESTADO_VITORIA
    def limpando_tela(self):
        return self.estado == self.ESTADO_LIMPANDO

    def nome_chefe(self):
        nomes = {
            1: 'FALCAO DA TEMPESTADE',
            2: 'LESMA COLOSSAL',
            3: 'JAVALI DE FERRO',
            4: 'GUARDIAO VIOLETA',
            5: 'IMPERADOR CARMESIM',
        }
        return nomes.get(self.fase_atual, 'CHEFE')

    def intervalo_obstaculo(self):
        fator = max(0.72, 1.0 - (self.fase_atual - 1) * 0.07)
        return random.uniform(1.5, 3.0) * fator

    def intervalo_inimigo(self):
        fator = max(0.72, 1.0 - (self.fase_atual - 1) * 0.07)
        return random.uniform(4.0, 7.0) * fator
