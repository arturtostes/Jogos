import random
import pygame
from PPlay.window import Window

from config import (
    LARGURA, ALTURA, DISTANCIA_MIN_SPAWN, COOLDOWN_TIRO,
    FORCA_PULO_BOSS_DIFICIL, DURACAO_FASE, TELA_CHEIA_INICIAL,
)
from assets import preparar_assets
from player import Player
from tiro import Tiro
from obstaculo import Obstaculo
from inimigo import Inimigo
from boss import Boss
from cenario import Cenario
from interface import Interface
from fase import GerenciadorFases
from save import GerenciadorSave
from arma import obter_arma, todas_as_armas, armas_bloqueadas
from upgrade import BUFFS, gerar_buffs, opcao_buff
from coracao_especial import CoracaoEspecial
from musica import GerenciadorMusica


class Jogo:
    def __init__(self):
        self.janela = Window(LARGURA, ALTURA)
        self.janela.set_title('CHICKEN: THE GAME')
        try:
            icone = pygame.image.load('coracao.png').convert_alpha()
            pygame.display.set_icon(icone)
        except pygame.error:
            pass
        self.janela.set_fullscreen(TELA_CHEIA_INICIAL)
        self.teclado = self.janela.keyboard
        self.musica = GerenciadorMusica()

        self.assets = preparar_assets()

        self.cenario = Cenario(self.assets)
        self.interface = Interface(self.janela, self.assets)
        self.player = Player(self.assets)
        self.fases = GerenciadorFases()
        self.save = GerenciadorSave()
        self.dados_save = self.save.carregar()
        self.arma_atual = obter_arma(self.dados_save.get('arma_selecionada', 'normal'))
        self.selecao_arma_ativa = False
        self.arma_selecao_id = self.arma_atual.id
        self.opcoes_recompensa = []

        self.tiros = []
        self.tiros_boss = []
        self.obstaculos = []
        self.inimigos = []
        self.boss = None
        self.coracao_especial = None
        self.coracao_apareceu_na_fase = False
        self.momento_coracao = self.sortear_momento_coracao()

        self.menu_ativo = True
        self.jogo_iniciado = False
        self.mouse_pressionado_anterior = False
        self.espaco_pressionado_anterior = False

        self.tempo_tiro = COOLDOWN_TIRO

        self.tempo_obstaculo = 0
        self.proximo_obstaculo = self.fases.intervalo_obstaculo()

        self.tempo_inimigo = 0
        self.proximo_inimigo = self.fases.intervalo_inimigo()

        self.fase_monitorada = self.fases.fase_atual
        self.player.aplicar_upgrades(self.dados_save.get('upgrades', {}))
        self.player.restaurar_vidas_fase()

    def sortear_momento_coracao(self):
        # Um unico coracao especial por fase, surgindo em um momento
        # imprevisivel entre aproximadamente 15s e 42s.
        inicio = max(2.0, DURACAO_FASE * 0.25)
        fim = max(inicio + 1.0, DURACAO_FASE * 0.70)
        return random.uniform(inicio, fim)

    def preparar_coracao_fase(self):
        self.coracao_especial = None
        self.coracao_apareceu_na_fase = False
        self.momento_coracao = self.sortear_momento_coracao()

    def pode_spawnar(self):
        limite = LARGURA - DISTANCIA_MIN_SPAWN

        for obstaculo in self.obstaculos:
            if obstaculo.sprite.x + obstaculo.sprite.width > limite:
                return False

        for inimigo in self.inimigos:
            if inimigo.sprite.x + inimigo.sprite.width > limite:
                return False

        return True

    def nivel_upgrade(self, id_upgrade):
        try:
            return max(0, int(self.dados_save.get('upgrades', {}).get(id_upgrade, 0)))
        except (TypeError, ValueError):
            return 0

    def cooldown_arma_atual(self):
        nivel = self.nivel_upgrade('cadencia')
        return max(0.16, self.arma_atual.cooldown * (0.90 ** nivel))

    def dano_arma_atual(self):
        return self.arma_atual.dano + self.nivel_upgrade('dano')

    def velocidade_tiro_atual(self):
        nivel = self.nivel_upgrade('velocidade_tiro')
        return self.arma_atual.velocidade * (1.12 ** nivel)

    def criar_tiro(self):
        for angulo in self.arma_atual.angulos:
            self.tiros.append(
                Tiro(
                    self.assets,
                    self.player,
                    velocidade=self.velocidade_tiro_atual(),
                    dano=self.dano_arma_atual(),
                    angulo=angulo,
                    penetracao=self.arma_atual.penetracao,
                    id_arma=self.arma_atual.id,
                )
            )

    def criar_obstaculo(self):
        self.obstaculos.append(Obstaculo(self.assets))

    def criar_inimigo(self):
        self.inimigos.append(Inimigo(self.assets, self.fases.fase_atual))

    def criar_boss(self):
        self.tiros.clear()
        self.tiros_boss.clear()
        self.boss = Boss(self.assets, self.fases.fase_atual)

    def preparar_nova_fase(self):
        self.boss = None
        self.tiros.clear()
        self.tiros_boss.clear()
        self.obstaculos.clear()
        self.inimigos.clear()
        self.preparar_coracao_fase()

        self.player.resetar_posicao_horizontal()
        # Cada nova fase sempre comeca com 3 vidas.
        self.player.restaurar_vidas_fase()

        self.tempo_tiro = self.cooldown_arma_atual()
        self.tempo_obstaculo = 0
        self.proximo_obstaculo = self.fases.intervalo_obstaculo()
        self.tempo_inimigo = 0
        self.proximo_inimigo = self.fases.intervalo_inimigo()

        self.abrir_selecao_arma()

    def armas_desbloqueadas(self):
        armas = self.dados_save.get('armas', ['normal'])
        return armas if isinstance(armas, list) and armas else ['normal']

    def abrir_selecao_arma(self):
        desbloqueadas = self.armas_desbloqueadas()
        atual = self.dados_save.get('arma_selecionada', 'normal')
        if atual not in desbloqueadas:
            atual = desbloqueadas[0]
        self.arma_selecao_id = atual
        self.selecao_arma_ativa = True

    def confirmar_arma(self):
        if self.arma_selecao_id not in self.armas_desbloqueadas():
            return

        self.arma_atual = obter_arma(self.arma_selecao_id)
        self.dados_save = self.save.selecionar_arma(
            self.arma_atual.id,
            self.dados_save,
        )
        self.tempo_tiro = self.cooldown_arma_atual()
        self.selecao_arma_ativa = False

    def processar_selecao_arma(self):
        armas = todas_as_armas()
        desbloqueadas = self.armas_desbloqueadas()

        self.player.desenhar_parado()
        self.cenario.desenhar_frente()
        self.interface.desenhar_selecao_arma(
            armas,
            desbloqueadas,
            self.arma_selecao_id,
            self.fases.fase_atual,
            self.dados_save.get('upgrades', {}),
        )

        pygame.event.pump()
        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior
        pos_mouse = self.janela.get_mouse_position()

        if clique_novo:
            arma_id = self.interface.arma_clicada(
                pos_mouse,
                armas,
                desbloqueadas,
            )
            if arma_id is not None:
                self.arma_selecao_id = arma_id
            elif self.interface.clicou_confirmar_arma(pos_mouse):
                self.confirmar_arma()

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def processar_menu(self):
        pygame.event.pump()
        continuar_disponivel = self.save.existe()
        self.interface.desenhar_menu(continuar_disponivel)

        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior
        pos_mouse = self.janela.get_mouse_position()

        if (
            clique_novo
            and continuar_disponivel
            and self.interface.clicou_continuar(pos_mouse)
        ):
            self.continuar_jogo()

        elif clique_novo and self.interface.clicou_novo_jogo(pos_mouse):
            self.iniciar_novo_jogo()

        elif clique_novo and self.interface.clicou_sair(pos_mouse):
            pygame.quit()
            raise SystemExit

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def iniciar_novo_jogo(self):
        self.dados_save = self.save.novo_jogo()
        self.arma_atual = obter_arma(self.dados_save.get('arma_selecionada', 'normal'))
        self.arma_selecao_id = self.arma_atual.id
        self.selecao_arma_ativa = False
        self.opcoes_recompensa = []
        self.fases.reiniciar()
        self.fase_monitorada = self.fases.fase_atual

        self.boss = None
        self.tiros.clear()
        self.tiros_boss.clear()
        self.obstaculos.clear()
        self.inimigos.clear()
        self.preparar_coracao_fase()

        self.player.reiniciar()
        self.player.aplicar_upgrades(self.dados_save.get('upgrades', {}))
        self.player.restaurar_vidas_fase()
        self.cenario = Cenario(self.assets)

        self.tempo_tiro = COOLDOWN_TIRO
        self.tempo_obstaculo = 0
        self.proximo_obstaculo = self.fases.intervalo_obstaculo()
        self.tempo_inimigo = 0
        self.proximo_inimigo = self.fases.intervalo_inimigo()

        self.jogo_iniciado = False
        self.menu_ativo = False

    def continuar_jogo(self):
        self.dados_save = self.save.carregar()
        self.arma_atual = obter_arma(self.dados_save.get('arma_selecionada', 'normal'))
        self.arma_selecao_id = self.arma_atual.id
        self.selecao_arma_ativa = False
        self.opcoes_recompensa = []
        self.fases.carregar_fase(self.dados_save.get('fase', 1))
        self.fase_monitorada = self.fases.fase_atual

        self.boss = None
        self.tiros.clear()
        self.tiros_boss.clear()
        self.obstaculos.clear()
        self.inimigos.clear()
        self.preparar_coracao_fase()

        self.player.reiniciar()
        self.player.aplicar_upgrades(self.dados_save.get('upgrades', {}))
        self.player.restaurar_vidas_fase()
        self.cenario = Cenario(self.assets)

        self.tempo_tiro = COOLDOWN_TIRO
        self.tempo_obstaculo = 0
        self.proximo_obstaculo = self.fases.intervalo_obstaculo()
        self.tempo_inimigo = 0
        self.proximo_inimigo = self.fases.intervalo_inimigo()

        self.jogo_iniciado = False
        self.menu_ativo = False

    def processar_tela_inicial(self):
        self.player.desenhar_parado()
        self.cenario.desenhar_frente()
        self.interface.desenhar_tela_inicial()

        pygame.event.pump()
        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior

        if self.teclado.key_pressed('ENTER') or (
            clique_novo and self.interface.clicou_iniciar(self.janela.get_mouse_position())
        ):
            self.jogo_iniciado = True
            self.abrir_selecao_arma()

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def processar_game_over(self, dt):
        for obstaculo in self.obstaculos:
            obstaculo.desenhar()

        for inimigo in self.inimigos:
            inimigo.desenhar()

        if self.coracao_especial is not None:
            self.coracao_especial.desenhar()

        if self.boss is not None:
            self.boss.desenhar()

        for tiro_boss in self.tiros_boss:
            tiro_boss.desenhar()

        self.player.atualizar_morte(dt)
        self.player.desenhar_morte()
        self.cenario.desenhar_frente()

        self.janela.draw_text(
            'GAME OVER',
            470,
            270,
            size=64,
            color=(255, 255, 255),
            font_name='Calibri',
        )

        self.interface.desenhar_botao_reiniciar()

        pygame.event.pump()
        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior
        pos_mouse = self.janela.get_mouse_position()

        if clique_novo and self.interface.clicou_reiniciar(pos_mouse):
            self.reiniciar_partida()

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def reiniciar_partida(self):
        # Ao morrer, o jogo e o save sempre voltam para o inicio da Fase 1.
        self.dados_save = self.save.resetar_apos_morte(self.dados_save)
        self.fases.reiniciar()
        self.opcoes_recompensa = []
        self.fase_monitorada = self.fases.fase_atual

        self.boss = None
        self.tiros.clear()
        self.tiros_boss.clear()
        self.obstaculos.clear()
        self.inimigos.clear()
        self.preparar_coracao_fase()

        self.player.reiniciar()
        self.player.aplicar_upgrades(self.dados_save.get('upgrades', {}))
        self.player.restaurar_vidas_fase()
        self.cenario = Cenario(self.assets)

        self.tempo_tiro = COOLDOWN_TIRO
        self.tempo_obstaculo = 0
        self.proximo_obstaculo = self.fases.intervalo_obstaculo()
        self.tempo_inimigo = 0
        self.proximo_inimigo = self.fases.intervalo_inimigo()

        self.arma_atual = obter_arma(self.dados_save.get('arma_selecionada', 'normal'))
        self.arma_selecao_id = self.arma_atual.id
        self.abrir_selecao_arma()

    def processar_vitoria(self):
        self.player.atualizar_animacao()
        self.player.desenhar()
        self.cenario.desenhar_frente()
        self.interface.desenhar_coracoes(self.player.vidas)
        self.interface.desenhar_vitoria()

        pygame.event.pump()
        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior
        if clique_novo and self.interface.clicou_voltar_menu(self.janela.get_mouse_position()):
            self.voltar_ao_menu()

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def voltar_ao_menu(self):
        self.menu_ativo = True
        self.jogo_iniciado = False
        self.selecao_arma_ativa = False
        self.opcoes_recompensa = []
        self.boss = None
        self.tiros.clear()
        self.tiros_boss.clear()
        self.obstaculos.clear()
        self.inimigos.clear()
        self.coracao_especial = None

    def atualizar_fase(self, dt):
        tela_limpa = len(self.obstaculos) == 0 and len(self.inimigos) == 0
        self.fases.atualizar(dt, tela_limpa)

        if self.fases.fase_atual != self.fase_monitorada:
            self.fase_monitorada = self.fases.fase_atual
            self.preparar_nova_fase()

    def atualizar_player(self, dt):
        self.player.atualizar_invencibilidade(dt)
        self.player.atualizar_fisica(dt)

        espaco_agora = self.teclado.key_pressed('SPACE')
        novo_toque_espaco = espaco_agora and not self.espaco_pressionado_anterior

        if novo_toque_espaco and self.player.pode_pular():
            if self.fases.em_boss() and self.fases.fase_atual in (3, 4):
                self.player.pular(FORCA_PULO_BOSS_DIFICIL)
            else:
                self.player.pular()

        self.espaco_pressionado_anterior = espaco_agora

        # Na sala do boss o runner vira uma arena: o jogador pode se
        # movimentar para esquerda/direita, mas fica preso na tela.
        if self.fases.em_transicao_boss() or self.fases.em_boss():
            self.player.atualizar_movimento_boss(dt, self.teclado)

        self.player.sincronizar_sprites()

    def atualizar_tiros(self, dt):
        self.tempo_tiro += dt

        if self.teclado.key_pressed('X') and self.tempo_tiro >= self.cooldown_arma_atual():
            self.criar_tiro()
            self.tempo_tiro = 0

        for tiro in self.tiros[:]:
            tiro.atualizar(dt)
            if tiro.saiu_da_tela():
                self.tiros.remove(tiro)

    def atualizar_tiros_boss(self, dt):
        for tiro in self.tiros_boss[:]:
            tiro.atualizar(dt)
            if tiro.saiu_da_tela():
                self.tiros_boss.remove(tiro)

    def atualizar_obstaculos(self, dt):
        if self.fases.pode_spawnar_normais():
            self.tempo_obstaculo += dt

            if self.tempo_obstaculo >= self.proximo_obstaculo and self.pode_spawnar():
                self.criar_obstaculo()
                self.tempo_obstaculo = 0
                self.proximo_obstaculo = self.fases.intervalo_obstaculo()

        for obstaculo in self.obstaculos[:]:
            obstaculo.atualizar(dt)
            if obstaculo.saiu_da_tela():
                self.obstaculos.remove(obstaculo)

    def atualizar_inimigos(self, dt):
        if self.fases.pode_spawnar_normais():
            self.tempo_inimigo += dt

            if self.tempo_inimigo >= self.proximo_inimigo and self.pode_spawnar():
                self.criar_inimigo()
                self.tempo_inimigo = 0
                self.proximo_inimigo = self.fases.intervalo_inimigo()

        for inimigo in self.inimigos[:]:
            inimigo.atualizar(dt)
            if inimigo.saiu_da_tela():
                self.inimigos.remove(inimigo)

    def atualizar_coracao_especial(self, dt):
        # O coracao so existe durante a parte normal da fase, nunca no boss.
        if not self.fases.pode_spawnar_normais():
            self.coracao_especial = None
            return

        tempo_decorrido = DURACAO_FASE - self.fases.tempo_restante

        if (
            not self.coracao_apareceu_na_fase
            and tempo_decorrido >= self.momento_coracao
        ):
            self.coracao_especial = CoracaoEspecial(self.assets)
            self.coracao_apareceu_na_fase = True

        if self.coracao_especial is not None:
            self.coracao_especial.atualizar(dt)
            if self.coracao_especial.saiu_da_tela():
                self.coracao_especial = None

    def colisao_tiros_coracao(self):
        if self.coracao_especial is None:
            return

        for tiro in self.tiros[:]:
            if tiro.sprite.collided(self.coracao_especial.sprite):
                if tiro in self.tiros:
                    self.tiros.remove(tiro)

                destruido = self.coracao_especial.receber_tiro()
                if destruido:
                    self.player.curar(1)
                    self.coracao_especial = None
                break

    def atualizar_boss(self, dt):
        if not self.fases.em_boss():
            return

        if self.boss is None:
            self.criar_boss()

        novos_tiros, invocar = self.boss.atualizar(dt, self.player)
        self.tiros_boss.extend(novos_tiros)

        if invocar:
            self.criar_inimigo()

    def colisao_tiros_inimigos(self):
        for tiro in self.tiros[:]:
            for inimigo in self.inimigos:
                if inimigo.morto or not tiro.pode_acertar(inimigo):
                    continue

                if tiro.sprite.collided(inimigo.sprite):
                    inimigo.receber_tiro(tiro.dano)
                    tiro.registrar_acerto(inimigo)

                    if tiro.esgotou_penetracao():
                        if tiro in self.tiros:
                            self.tiros.remove(tiro)
                        break

    def gerar_opcoes_recompensa(self):
        upgrades = self.dados_save.get('upgrades', {})
        buffs = gerar_buffs(upgrades, 2)
        opcoes = [opcao_buff(id_buff, upgrades) for id_buff in buffs]

        bloqueadas = armas_bloqueadas(self.armas_desbloqueadas())
        if bloqueadas:
            id_arma = random.choice(bloqueadas)
            opcoes.append({
                'tipo': 'arma',
                'id': id_arma,
                'nome': obter_arma(id_arma).nome,
                'descricao': obter_arma(id_arma).descricao,
                'arma': obter_arma(id_arma),
            })
        else:
            # Em uma run normal isso so pode acontecer depois de todas as armas
            # estarem liberadas. Nesse caso oferecemos um terceiro buff.
            extras = [x for x in BUFFS if x not in buffs]
            id_buff = random.choice(extras if extras else list(BUFFS.keys()))
            opcoes.append(opcao_buff(id_buff, upgrades))

        self.opcoes_recompensa = opcoes

    def aplicar_recompensa(self, indice):
        if indice is None or indice < 0 or indice >= len(self.opcoes_recompensa):
            return
        opcao = self.opcoes_recompensa[indice]

        if opcao['tipo'] == 'arma':
            self.dados_save = self.save.desbloquear_arma(opcao['id'], self.dados_save)
        else:
            id_buff = opcao['id']
            max_nivel = BUFFS[id_buff]['max_nivel']
            atual = self.nivel_upgrade(id_buff)
            if atual < max_nivel:
                self.dados_save = self.save.aplicar_upgrade(id_buff, self.dados_save)

        self.player.aplicar_upgrades(self.dados_save.get('upgrades', {}))
        self.opcoes_recompensa = []
        avancou = self.fases.avancar_apos_recompensa()
        if avancou:
            self.fase_monitorada = self.fases.fase_atual
            self.dados_save = self.save.salvar_fase(self.fases.fase_atual, self.dados_save, False)
            self.preparar_nova_fase()

    def processar_recompensa(self):
        if not self.opcoes_recompensa:
            self.gerar_opcoes_recompensa()

        self.player.desenhar_parado()
        self.cenario.desenhar_frente()
        self.interface.desenhar_recompensa(
            self.opcoes_recompensa,
            self.fases.fase_concluida,
        )

        pygame.event.pump()
        mouse_pressionado = pygame.mouse.get_pressed()[0]
        clique_novo = mouse_pressionado and not self.mouse_pressionado_anterior
        if clique_novo:
            indice = self.interface.recompensa_clicada(
                self.janela.get_mouse_position(),
                self.opcoes_recompensa,
            )
            if indice is not None:
                self.aplicar_recompensa(indice)

        self.mouse_pressionado_anterior = mouse_pressionado
        self.janela.update()

    def finalizar_boss(self):
        fase_concluida = self.fases.fase_atual
        self.boss = None
        self.tiros_boss.clear()
        self.inimigos.clear()
        self.tiros.clear()

        if fase_concluida >= 5:
            self.dados_save = self.save.salvar_fase(5, self.dados_save, jogo_concluido=True)
            self.fases.estado = self.fases.ESTADO_VITORIA
        else:
            self.fases.iniciar_recompensa()
            self.gerar_opcoes_recompensa()

    def colisao_tiros_boss(self):
        if self.boss is None or self.boss.morto:
            return

        for tiro in self.tiros[:]:
            if tiro.sprite.collided(self.boss.sprite):
                self.boss.receber_tiro(tiro.dano)

                if tiro in self.tiros:
                    self.tiros.remove(tiro)

                if self.boss.morto:
                    self.finalizar_boss()
                    break

    def colisao_player_obstaculos(self):
        if self.player.tempo_invencivel > 0:
            return

        player_sprite = self.player.sprite_atual()

        for obstaculo in self.obstaculos:
            if obstaculo.colidiu_com_player(player_sprite):
                self.player.tomar_dano()
                break

    def colisao_player_inimigos(self):
        if self.player.tempo_invencivel > 0:
            return

        player_sprite = self.player.sprite_atual()

        for inimigo in self.inimigos:
            if inimigo.morto:
                continue

            if player_sprite.collided(inimigo.sprite):
                self.player.tomar_dano()
                break

    def colisao_player_tiros_boss(self):
        player_sprite = self.player.sprite_atual()

        for tiro in self.tiros_boss[:]:
            if tiro.colidiu_com(player_sprite):
                self.player.tomar_dano()
                if tiro in self.tiros_boss:
                    self.tiros_boss.remove(tiro)

    def colisao_player_boss(self):
        if self.boss is None or self.boss.morto:
            return

        # Encostar fisicamente no boss tambem causa dano. O proprio Player
        # controla o intervalo de invencibilidade para nao perder varias vidas
        # no mesmo instante.
        if self.boss.colidiu_com(self.player.sprite_atual()):
            self.player.tomar_dano()

    def atualizar_musica(self):
        # M alterna mute sem interferir nas quatro trilhas.
        if self.teclado.key_down('M'):
            self.musica.alternar_mudo()

        if self.menu_ativo or not self.jogo_iniciado:
            trilha = 'menu'
        elif self.fases.em_boss() or self.fases.em_transicao_boss():
            trilha = 'boss_final' if self.fases.fase_atual == 5 else 'miniboss'
        elif self.fases.em_vitoria():
            trilha = 'menu'
        else:
            trilha = 'fase'

        self.musica.tocar(trilha)

    def desenhar_jogo(self):
        for obstaculo in self.obstaculos:
            obstaculo.desenhar()

        for inimigo in self.inimigos:
            inimigo.desenhar()

        if self.coracao_especial is not None:
            self.coracao_especial.desenhar()

        if self.boss is not None:
            self.boss.desenhar()

        for tiro in self.tiros:
            tiro.desenhar()

        for tiro in self.tiros_boss:
            tiro.desenhar()

        self.player.atualizar_animacao()
        self.player.desenhar()
        self.cenario.desenhar_frente()

        self.interface.desenhar_coracoes(self.player.vidas)
        self.interface.desenhar_hud_fase(
            self.fases.fase_atual,
            self.fases.tempo_restante,
            self.fases.mostrar_timer(),
        )

        if self.fases.em_transicao_boss():
            self.interface.desenhar_transicao_boss(self.fases.nome_chefe())

        elif self.fases.em_boss():
            self.interface.desenhar_estado_boss(self.fases.nome_chefe())

            if self.boss is not None:
                self.interface.desenhar_barra_boss(
                    self.boss.nome,
                    self.boss.vida,
                    self.boss.vida_maxima,
                    self.boss.protegido,
                    self.boss.fase_final_atual(),
                )



    def executar(self):
        while True:
            # Evita saltos enormes de fisica ao voltar de Alt+Tab/minimizacao.
            dt = min(self.janela.delta_time(), 0.05)
            self.janela.set_background_color((100, 180, 255))
            self.atualizar_musica()

            if self.menu_ativo:
                self.processar_menu()
                continue

            if self.jogo_iniciado and not self.player.game_over and not self.selecao_arma_ativa and not self.fases.em_recompensa():
                # O cenario continua andando normalmente inclusive durante os bosses.
                self.cenario.atualizar(dt)

            self.cenario.desenhar()
            self.player.sincronizar_sprites()

            if not self.jogo_iniciado:
                self.processar_tela_inicial()
                continue

            if self.player.game_over:
                self.processar_game_over(dt)
                continue

            if self.fases.em_recompensa():
                self.processar_recompensa()
                continue

            if self.selecao_arma_ativa:
                self.processar_selecao_arma()
                continue

            if self.fases.em_vitoria():
                self.processar_vitoria()
                continue

            self.atualizar_fase(dt)
            self.atualizar_player(dt)
            self.atualizar_tiros(dt)
            self.atualizar_obstaculos(dt)
            self.atualizar_inimigos(dt)
            self.atualizar_coracao_especial(dt)
            self.atualizar_boss(dt)
            self.atualizar_tiros_boss(dt)

            self.colisao_tiros_inimigos()
            self.colisao_tiros_coracao()
            self.colisao_tiros_boss()
            self.colisao_player_obstaculos()
            self.colisao_player_inimigos()
            self.colisao_player_tiros_boss()
            self.colisao_player_boss()

            self.desenhar_jogo()
            self.janela.update()
            self.mouse_pressionado_anterior = pygame.mouse.get_pressed()[0]
