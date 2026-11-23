import math
import pygame
from PPlay.sprite import Sprite
from config import LARGURA, ALTURA, TAM_CORACAO, ESPACO_CORACOES


class Interface:
    def __init__(self, janela, assets):
        self.janela = janela
        self.assets = assets
        self.fundo_menu = Sprite(assets['fundo_menu'])

        self.coracoes = [Sprite(assets['coracao']) for _ in range(5)]
        for i, coracao in enumerate(self.coracoes):
            coracao.set_position(24 + i * (TAM_CORACAO + ESPACO_CORACOES), 18)

        self.rect_continuar = pygame.Rect(LARGURA // 2 - 180, 345, 360, 68)
        self.rect_novo_jogo = pygame.Rect(LARGURA // 2 - 180, 430, 360, 68)
        self.rect_sair = pygame.Rect(LARGURA // 2 - 180, 515, 360, 68)
        self.rect_reiniciar = pygame.Rect(LARGURA // 2 - 180, 400, 360, 72)
        self.rect_voltar_menu = pygame.Rect(LARGURA // 2 - 180, 430, 360, 68)
        self.rect_iniciar = pygame.Rect(LARGURA // 2 - 230, 330, 460, 78)


        self.rect_confirmar_arma = pygame.Rect(LARGURA // 2 - 155, 628, 310, 56)
        self.rects_recompensa = self._rects_recompensa()

        self.previews_armas = {}
        for id_arma in ('normal', 'rapida', 'pesada', 'tripla', 'perfurante'):
            caminho = assets.get(f'tiro_{id_arma}')
            if caminho:
                self.previews_armas[id_arma] = pygame.image.load(caminho).convert_alpha()

    # ------------------------------------------------------------------
    # BASICO / HELPERS
    # ------------------------------------------------------------------
    def _texto_centralizado(self, texto, y, tamanho, cor, fonte='Arial Black'):
        f = pygame.font.SysFont(fonte, tamanho)
        largura, _ = f.size(texto)
        self.janela.draw_text(
            texto,
            (LARGURA - largura) // 2,
            y,
            size=tamanho,
            color=cor,
            font_name=fonte,
        )

    def _desenhar_botao(self, rect, texto, ativo=True, tamanho=30):
        tela = self.janela.screen
        hover = ativo and rect.collidepoint(self.janela.get_mouse_position())

        if not ativo:
            cor, borda, cor_texto = (70, 70, 70), (125, 125, 125), (190, 190, 190)
        elif hover:
            cor, borda, cor_texto = (238, 208, 132), (255, 248, 225), (25, 27, 30)
        else:
            cor, borda, cor_texto = (28, 33, 39), (190, 195, 198), (245, 245, 242)

        pygame.draw.rect(tela, cor, rect, border_radius=12)
        pygame.draw.rect(tela, borda, rect, 3, border_radius=12)

        fonte = pygame.font.SysFont('Arial Black', tamanho)
        lw, lh = fonte.size(texto)
        self.janela.draw_text(
            texto,
            rect.centerx - lw // 2,
            rect.centery - lh // 2 - 2,
            size=tamanho,
            color=cor_texto,
            font_name='Arial Black',
        )

    def _desenhar_blur_fundo(self, escurecer=105):
        """Blur leve usando downscale/upscale do frame atual."""
        tela = self.janela.screen
        captura = tela.copy()
        largura_peq = max(1, LARGURA // 14)
        altura_peq = max(1, ALTURA // 14)
        pequeno = pygame.transform.smoothscale(captura, (largura_peq, altura_peq))
        borrado = pygame.transform.smoothscale(pequeno, (LARGURA, ALTURA))
        tela.blit(borrado, (0, 0))

        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((5, 8, 12, escurecer))
        tela.blit(overlay, (0, 0))

    def _chamfer_points(self, rect, corte=16):
        return [
            (rect.x + corte, rect.y),
            (rect.right - corte, rect.y),
            (rect.right, rect.y + corte),
            (rect.right, rect.bottom - corte),
            (rect.right - corte, rect.bottom),
            (rect.x + corte, rect.bottom),
            (rect.x, rect.bottom - corte),
            (rect.x, rect.y + corte),
        ]

    def _desenhar_carta(self, rect, destaque=False, bloqueada=False, hover=False, accent=(205, 210, 214)):
        """Carta escura com moldura metalica inspirada na referencia enviada."""
        tela = self.janela.screen

        sombra = rect.move(7, 9)
        pygame.draw.polygon(tela, (10, 12, 14), self._chamfer_points(sombra, 18))

        externa = rect.copy()
        pygame.draw.polygon(tela, (178, 182, 184), self._chamfer_points(externa, 18))

        meio = rect.inflate(-10, -10)
        pygame.draw.polygon(tela, (68, 74, 78), self._chamfer_points(meio, 14))

        interna = rect.inflate(-18, -18)
        base = (18, 24, 27)
        if hover and not bloqueada:
            base = (24, 31, 35)
        if bloqueada:
            base = (20, 21, 23)
        pygame.draw.polygon(tela, base, self._chamfer_points(interna, 11))

        borda = accent if destaque else (90, 102, 106)
        largura = 4 if destaque else 2
        pygame.draw.polygon(tela, borda, self._chamfer_points(interna, 11), largura)

        # Detalhes de canto, no estilo de card de upgrade.
        deco = (96, 110, 114) if not destaque else accent
        c = 18
        linhas = [
            ((interna.x + 8, interna.y + c), (interna.x + 8, interna.y + 8), (interna.x + c, interna.y + 8)),
            ((interna.right - c, interna.y + 8), (interna.right - 8, interna.y + 8), (interna.right - 8, interna.y + c)),
            ((interna.x + 8, interna.bottom - c), (interna.x + 8, interna.bottom - 8), (interna.x + c, interna.bottom - 8)),
            ((interna.right - c, interna.bottom - 8), (interna.right - 8, interna.bottom - 8), (interna.right - 8, interna.bottom - c)),
        ]
        for pontos in linhas:
            pygame.draw.lines(tela, deco, False, pontos, 2)

        if bloqueada:
            camada = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            camada.fill((0, 0, 0, 95))
            tela.blit(camada, rect.topleft)

    def _quebrar_texto(self, texto, fonte, largura_max):
        palavras = texto.split()
        linhas = []
        atual = ''
        for palavra in palavras:
            teste = palavra if not atual else atual + ' ' + palavra
            if fonte.size(teste)[0] <= largura_max:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
        return linhas

    def _texto_multilinha(self, texto, rect, y, tamanho=17, cor=(235, 238, 240), fonte_nome='Calibri', centralizado=True, espacamento=3):
        fonte = pygame.font.SysFont(fonte_nome, tamanho)
        linhas = self._quebrar_texto(texto, fonte, rect.width - 38)
        for linha in linhas:
            lw, lh = fonte.size(linha)
            x = rect.centerx - lw // 2 if centralizado else rect.x + 19
            self.janela.draw_text(
                linha,
                x,
                y,
                size=tamanho,
                color=cor,
                font_name=fonte_nome,
            )
            y += lh + espacamento
        return y

    # ------------------------------------------------------------------
    # MENU
    # ------------------------------------------------------------------
    def desenhar_menu(self, continuar_disponivel):
        self.fundo_menu.draw()
        # Titulo final do jogo
        self._texto_centralizado('CHICKEN:', 176, 78, (75, 42, 24), 'Arial Black')
        self._texto_centralizado('CHICKEN:', 170, 78, (255, 205, 75), 'Arial Black')
        self._texto_centralizado('THE GAME', 252, 46, (72, 43, 28), 'Arial Black')
        self._texto_centralizado('THE GAME', 248, 46, (250, 243, 215), 'Arial Black')
        self._desenhar_botao(self.rect_continuar, 'CONTINUAR', continuar_disponivel, 30)
        self._desenhar_botao(self.rect_novo_jogo, 'NOVO JOGO', True, 30)
        self._desenhar_botao(self.rect_sair, 'SAIR', True, 30)
        self._texto_centralizado('F11: TELA CHEIA   |   M: MUSICA', 612, 16, (238, 238, 235), 'Calibri')

    def clicou_continuar(self, pos):
        return self.rect_continuar.collidepoint(pos)

    def clicou_novo_jogo(self, pos):
        return self.rect_novo_jogo.collidepoint(pos)

    def clicou_sair(self, pos):
        return self.rect_sair.collidepoint(pos)

    def desenhar_tela_inicial(self):
        # Mantem o jogo visivel ao fundo, mas desfocado ate o jogador iniciar.
        self._desenhar_blur_fundo(112)
        self._texto_centralizado('PRONTO PARA CORRER?', 230, 42, (250, 250, 246))
        self._desenhar_botao(self.rect_iniciar, 'ENTER PARA COMECAR', True, 30)
        self._texto_centralizado('ou clique no botao', 425, 17, (215, 220, 222), 'Calibri')

    def clicou_iniciar(self, pos):
        return self.rect_iniciar.collidepoint(pos)

    def desenhar_botao_reiniciar(self):
        self._desenhar_botao(self.rect_reiniciar, 'REINICIAR', True, 34)

    def clicou_reiniciar(self, pos):
        return self.rect_reiniciar.collidepoint(pos)

    # ------------------------------------------------------------------
    # CARTAS DE ARMA
    # ------------------------------------------------------------------
    def _rects_armas(self, quantidade):
        largura_card, altura_card, espaco = 210, 378, 16
        total = quantidade * largura_card + (quantidade - 1) * espaco
        inicio_x = (LARGURA - total) // 2
        return [
            pygame.Rect(inicio_x + i * (largura_card + espaco), 205, largura_card, altura_card)
            for i in range(quantidade)
        ]

    def _barra_stat(self, rect, y, nome, valor, maximo, cor):
        self.janela.draw_text(nome, rect.x + 18, y - 1, size=14, color=(232, 234, 235), font_name='Calibri')
        bx, by, bw, bh = rect.x + 18, y + 18, rect.width - 36, 7
        pygame.draw.rect(self.janela.screen, (45, 49, 51), (bx, by, bw, bh), border_radius=4)
        pct = max(0.06, min(1.0, valor / maximo))
        pygame.draw.rect(self.janela.screen, cor, (bx, by, int(bw * pct), bh), border_radius=4)

    def _preview_arma(self, id_arma, rect, bloqueada=False, centro_y=None):
        img = self.previews_armas.get(id_arma)
        if img is None:
            return

        escala = min(2.5, 108 / max(img.get_width(), img.get_height()))
        w = max(1, int(img.get_width() * escala))
        h = max(1, int(img.get_height() * escala))
        prev = pygame.transform.smoothscale(img, (w, h))
        if bloqueada:
            prev = prev.copy()
            prev.set_alpha(65)

        y_centro = rect.y + 92 if centro_y is None else centro_y
        self.janela.screen.blit(prev, (rect.centerx - w // 2, int(y_centro - h // 2)))

    def desenhar_selecao_arma(self, armas, desbloqueadas, selecionada, fase, upgrades=None):
        self._desenhar_blur_fundo(120)

        self._texto_centralizado(f'ARSENAL - FASE {fase}', 52, 39, (250, 250, 246))
        self._texto_centralizado(
            'Escolha uma das armas desbloqueadas para entrar na proxima fase',
            105,
            21,
            (225, 229, 231),
            'Calibri',
        )

        rects = self._rects_armas(len(armas))
        mouse = self.janela.get_mouse_position()

        for arma, rect in zip(armas, rects):
            desbloq = arma.id in desbloqueadas
            escolhida = arma.id == selecionada and desbloq
            hover = desbloq and rect.collidepoint(mouse)

            self._desenhar_carta(
                rect,
                destaque=escolhida,
                bloqueada=not desbloq,
                hover=hover,
                accent=arma.cor,
            )

            # Etiqueta superior
            etiqueta = 'EQUIPADA' if escolhida else ('DISPONIVEL' if desbloq else 'BLOQUEADA')
            tag = pygame.Rect(rect.centerx - 62, rect.y + 22, 124, 25)
            pygame.draw.rect(self.janela.screen, (31, 37, 40), tag, border_radius=7)
            pygame.draw.rect(self.janela.screen, arma.cor if desbloq else (100, 102, 104), tag, 2, border_radius=7)
            fonte_tag = pygame.font.SysFont('Arial Black', 12)
            tw = fonte_tag.size(etiqueta)[0]
            self.janela.draw_text(
                etiqueta,
                tag.centerx - tw // 2,
                tag.y + 5,
                size=12,
                color=(245, 245, 242) if desbloq else (160, 160, 160),
                font_name='Arial Black',
            )

            self._preview_arma(arma.id, rect, not desbloq, rect.y + 92)

            fonte_nome = pygame.font.SysFont('Arial Black', 21)
            lw = fonte_nome.size(arma.nome)[0]
            self.janela.draw_text(
                arma.nome,
                rect.centerx - lw // 2,
                rect.y + 137,
                size=21,
                color=(250, 250, 247) if desbloq else (135, 135, 135),
                font_name='Arial Black',
            )

            self._texto_multilinha(
                arma.descricao,
                rect,
                rect.y + 173,
                tamanho=15,
                cor=(224, 227, 229) if desbloq else (125, 125, 125),
            )

            cor_stat = arma.cor if desbloq else (90, 90, 90)
            self._barra_stat(rect, rect.y + 225, 'DANO', min(arma.dano, 4), 4, cor_stat)
            cad = max(0.05, 1.2 - arma.cooldown)
            self._barra_stat(rect, rect.y + 267, 'CADENCIA', cad, 1.0, cor_stat)
            self._barra_stat(rect, rect.y + 309, 'VELOCIDADE', arma.velocidade, 950, cor_stat)

            if hover:
                self._texto_multilinha(
                    'Clique para selecionar',
                    rect,
                    rect.bottom - 38,
                    tamanho=13,
                    cor=(245, 245, 242),
                )

        self._desenhar_botao(self.rect_confirmar_arma, 'EQUIPAR E JOGAR', True, 23)

    def arma_clicada(self, pos, armas, desbloqueadas):
        for arma, rect in zip(armas, self._rects_armas(len(armas))):
            if arma.id in desbloqueadas and rect.collidepoint(pos):
                return arma.id
        return None

    def clicou_confirmar_arma(self, pos):
        return self.rect_confirmar_arma.collidepoint(pos)

    # ------------------------------------------------------------------
    # CARTAS DE RECOMPENSA
    # ------------------------------------------------------------------
    def _rects_recompensa(self):
        largura, altura, espaco = 304, 392, 38
        total = 3 * largura + 2 * espaco
        x = (LARGURA - total) // 2
        return [pygame.Rect(x + i * (largura + espaco), 205, largura, altura) for i in range(3)]

    def _desenhar_icone_buff(self, id_buff, rect, cor):
        tela = self.janela.screen
        cx = rect.centerx
        cy = rect.y + 105

        pygame.draw.circle(tela, (25, 31, 34), (cx, cy), 47)
        pygame.draw.circle(tela, cor, (cx, cy), 43, 3)

        if id_buff == 'dano':
            pontos = [(cx - 8, cy - 30), (cx + 10, cy - 8), (cx + 1, cy - 8), (cx + 13, cy + 29), (cx - 14, cy + 4), (cx - 4, cy + 4)]
            pygame.draw.polygon(tela, cor, pontos)
        elif id_buff == 'cadencia':
            for dy in (-15, 0, 15):
                pygame.draw.polygon(tela, cor, [(cx - 22, cy + dy - 7), (cx + 2, cy + dy), (cx - 22, cy + dy + 7)])
                pygame.draw.polygon(tela, cor, [(cx + 2, cy + dy - 7), (cx + 26, cy + dy), (cx + 2, cy + dy + 7)])
        elif id_buff == 'velocidade_tiro':
            pygame.draw.line(tela, cor, (cx - 26, cy), (cx + 20, cy), 7)
            pygame.draw.polygon(tela, cor, [(cx + 30, cy), (cx + 10, cy - 16), (cx + 10, cy + 16)])
        elif id_buff == 'velocidade_player':
            pygame.draw.arc(tela, cor, (cx - 30, cy - 23, 52, 46), math.pi, math.pi * 2, 6)
            pygame.draw.line(tela, cor, (cx - 20, cy + 18), (cx + 18, cy + 18), 6)
            pygame.draw.line(tela, cor, (cx + 18, cy + 18), (cx + 29, cy + 6), 6)
        elif id_buff == 'vida_extra':
            # Coracao simples para representar +1 vida inicial/maxima.
            pygame.draw.circle(tela, cor, (cx - 12, cy - 8), 15)
            pygame.draw.circle(tela, cor, (cx + 12, cy - 8), 15)
            pygame.draw.polygon(tela, cor, [(cx - 27, cy - 4), (cx + 27, cy - 4), (cx, cy + 30)])
            pygame.draw.line(tela, (245, 245, 242), (cx, cy - 19), (cx, cy + 12), 5)
            pygame.draw.line(tela, (245, 245, 242), (cx - 14, cy - 3), (cx + 14, cy - 3), 5)
        elif id_buff == 'double_jump':
            # Duas setas empilhadas para representar os dois saltos.
            for off in (-12, 15):
                pygame.draw.polygon(tela, cor, [(cx, cy - 24 + off), (cx - 22, cy - 2 + off), (cx - 8, cy - 2 + off), (cx - 8, cy + 12 + off), (cx + 8, cy + 12 + off), (cx + 8, cy - 2 + off), (cx + 22, cy - 2 + off)])
        else:  # invencibilidade
            pontos = [(cx, cy - 30), (cx + 25, cy - 18), (cx + 19, cy + 16), (cx, cy + 31), (cx - 19, cy + 16), (cx - 25, cy - 18)]
            pygame.draw.polygon(tela, cor, pontos, 5)
            pygame.draw.circle(tela, cor, (cx, cy), 8)

    def desenhar_recompensa(self, opcoes, fase):
        self._desenhar_blur_fundo(125)

        self._texto_centralizado(f'FASE {fase} CONCLUIDA!', 48, 42, (250, 250, 246))
        self._texto_centralizado(
            'Escolha UMA carta: dois buffs ou uma nova arma',
            103,
            22,
            (225, 229, 231),
            'Calibri',
        )

        mouse = self.janela.get_mouse_position()
        for opcao, rect in zip(opcoes, self.rects_recompensa):
            arma = opcao.get('arma')
            cor = arma.cor if opcao['tipo'] == 'arma' and arma else opcao.get('cor', (190, 195, 198))
            hover = rect.collidepoint(mouse)

            self._desenhar_carta(rect, destaque=hover, hover=hover, accent=cor)

            etiqueta = 'ARMA NOVA' if opcao['tipo'] == 'arma' else 'UPGRADE'
            tag = pygame.Rect(rect.centerx - 67, rect.y + 23, 134, 28)
            pygame.draw.rect(self.janela.screen, (28, 34, 37), tag, border_radius=7)
            pygame.draw.rect(self.janela.screen, cor, tag, 2, border_radius=7)
            ftag = pygame.font.SysFont('Arial Black', 13)
            tw = ftag.size(etiqueta)[0]
            self.janela.draw_text(
                etiqueta,
                tag.centerx - tw // 2,
                tag.y + 5,
                size=13,
                color=(245, 245, 242),
                font_name='Arial Black',
            )

            if opcao['tipo'] == 'arma' and arma:
                self._preview_arma(arma.id, rect, False, rect.y + 112)
                nome = arma.nome
                desc = arma.descricao
                extra = 'Desbloqueia esta arma permanentemente.'
            else:
                self._desenhar_icone_buff(opcao['id'], rect, cor)
                nome = opcao['nome']
                desc = opcao['descricao']
                extra = f"Nivel {opcao.get('nivel_atual', 0)}  ->  {opcao.get('nivel_novo', 1)}"

            fonte_nome = pygame.font.SysFont('Arial Black', 25)
            lw = fonte_nome.size(nome)[0]
            self.janela.draw_text(
                nome,
                rect.centerx - lw // 2,
                rect.y + 176,
                size=25,
                color=(250, 250, 247),
                font_name='Arial Black',
            )

            y = self._texto_multilinha(
                desc,
                rect,
                rect.y + 224,
                tamanho=18,
                cor=(232, 234, 235),
                fonte_nome='Calibri',
            )
            self._texto_multilinha(
                extra,
                rect,
                max(rect.y + 294, y + 12),
                tamanho=15,
                cor=(185, 191, 194),
                fonte_nome='Calibri',
            )

            if hover:
                barra = pygame.Rect(rect.x + 34, rect.bottom - 49, rect.width - 68, 29)
                pygame.draw.rect(self.janela.screen, (30, 36, 39), barra, border_radius=8)
                pygame.draw.rect(self.janela.screen, cor, barra, 2, border_radius=8)
                f = pygame.font.SysFont('Arial Black', 13)
                texto = 'CLIQUE PARA ESCOLHER'
                tw = f.size(texto)[0]
                self.janela.draw_text(
                    texto,
                    barra.centerx - tw // 2,
                    barra.y + 6,
                    size=13,
                    color=(247, 247, 244),
                    font_name='Arial Black',
                )

    def recompensa_clicada(self, pos, opcoes):
        for i, rect in enumerate(self.rects_recompensa):
            if i < len(opcoes) and rect.collidepoint(pos):
                return i
        return None

    # ------------------------------------------------------------------
    # HUD / BOSS
    # ------------------------------------------------------------------
    def desenhar_coracoes(self, vidas):
        for i in range(min(vidas, len(self.coracoes))):
            self.coracoes[i].draw()

    def desenhar_hud_fase(self, fase, tempo_restante, mostrar_tempo=True):
        # HUD limpo: sem caixa/painel ao fundo, apenas texto com sombra para legibilidade.
        x = LARGURA - 215
        y = 18

        texto_fase = f'FASE {fase}'
        # Sombra discreta para manter contraste sem criar uma caixa atrás do HUD.
        self.janela.draw_text(
            texto_fase,
            x + 3,
            y + 3,
            size=27,
            color=(20, 20, 20),
            font_name='Arial Black',
        )
        self.janela.draw_text(
            texto_fase,
            x,
            y,
            size=27,
            color=(255, 231, 145),
            font_name='Arial Black',
        )

        if mostrar_tempo:
            segundos = max(0, int(math.ceil(tempo_restante)))
            texto_tempo = f'TEMPO {segundos}s'
            self.janela.draw_text(
                texto_tempo,
                x + 3,
                y + 39 + 3,
                size=22,
                color=(20, 20, 20),
                font_name='Arial Black',
            )
            self.janela.draw_text(
                texto_tempo,
                x,
                y + 39,
                size=22,
                color=(250, 250, 247),
                font_name='Arial Black',
            )

    def desenhar_transicao_boss(self, nome_chefe):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 115))
        self.janela.screen.blit(overlay, (0, 0))
        self._texto_centralizado(nome_chefe, 275, 54, (255, 225, 90))
        self._texto_centralizado('PREPARE-SE!', 350, 34, (255, 255, 255), 'Calibri')

    def desenhar_estado_boss(self, nome_chefe):
        self._texto_centralizado(nome_chefe, 18, 32, (255, 225, 90))

    def desenhar_barra_boss(self, nome, vida, vida_maxima, protegido=False, etapa_final=0):
        tela = self.janela.screen
        largura, altura = 520, 24
        x = (LARGURA - largura) // 2
        y = 64
        fundo = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(tela, (32, 24, 24), fundo, border_radius=8)
        pygame.draw.rect(tela, (240, 235, 215), fundo, 3, border_radius=8)
        pct = 0 if vida_maxima <= 0 else max(0, min(1, vida / vida_maxima))
        w = int((largura - 8) * pct)
        if w > 0:
            pygame.draw.rect(
                tela,
                (80, 185, 235) if protegido else (218, 57, 57),
                pygame.Rect(x + 4, y + 4, w, altura - 8),
                border_radius=5,
            )
        if protegido:
            self.janela.draw_text('PROTEGIDO', x + largura + 18, y - 2, size=20, color=(190, 240, 255), font_name='Calibri')
        if etapa_final > 0:
            self.janela.draw_text(f'ETAPA {etapa_final}/3', x + largura + 18, y + 24, size=18, color=(255, 230, 160), font_name='Calibri')

    def desenhar_vitoria(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        self.janela.screen.blit(overlay, (0, 0))
        self._texto_centralizado('VOCE VENCEU!', 235, 64, (255, 225, 90))
        self._texto_centralizado('BOSS FINAL DERROTADO', 325, 34, (255, 255, 255), 'Calibri')
        self._desenhar_botao(self.rect_voltar_menu, 'VOLTAR AO MENU', True, 27)

    def clicou_voltar_menu(self, pos):
        return self.rect_voltar_menu.collidepoint(pos)
