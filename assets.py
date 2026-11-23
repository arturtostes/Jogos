import os
import pygame
from config import *

PASTA_AJUSTADOS = '_sprites_ajustados'


def garantir_pasta():
    if not os.path.exists(PASTA_AJUSTADOS):
        os.mkdir(PASTA_AJUSTADOS)


def preparar_cenario():
    garantir_pasta()

    fundo_original = pygame.image.load('fundo.png').convert_alpha()
    fundo_ajustado = pygame.transform.scale(fundo_original, (LARGURA, ALTURA))
    caminho_fundo = os.path.join(PASTA_AJUSTADOS, 'fundo_ajustado.png')
    pygame.image.save(fundo_ajustado, caminho_fundo)

    fundo_menu_base = pygame.transform.smoothscale(fundo_original, (LARGURA, ALTURA))
    fundo_blur = pygame.transform.smoothscale(fundo_menu_base, (480, 270))
    fundo_blur = pygame.transform.smoothscale(fundo_blur, (LARGURA, ALTURA))

    camada_escura = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada_escura.fill((0, 0, 0, 45))
    fundo_blur.blit(camada_escura, (0, 0))

    caminho_fundo_menu = os.path.join(PASTA_AJUSTADOS, 'fundo_menu_blur.png')
    pygame.image.save(fundo_blur, caminho_fundo_menu)

    chao_original = pygame.image.load('chao.png').convert_alpha()
    rect_chao = chao_original.get_bounding_rect()

    if rect_chao.width > 0 and rect_chao.height > 0:
        chao_recortado = chao_original.subsurface(rect_chao).copy()
    else:
        chao_recortado = chao_original

    escala_chao = ALTURA_CHAO_VISUAL / chao_recortado.get_height()
    largura_chao = max(1, int(chao_recortado.get_width() * escala_chao))
    chao_ajustado = pygame.transform.scale(
        chao_recortado,
        (largura_chao, ALTURA_CHAO_VISUAL),
    )

    caminho_chao = os.path.join(PASTA_AJUSTADOS, 'chao_ajustado.png')
    pygame.image.save(chao_ajustado, caminho_chao)

    caminho_grama = 'grama_frente.png'
    return caminho_fundo, caminho_fundo_menu, caminho_chao, caminho_grama


def preparar_coracao():
    garantir_pasta()

    canvas = pygame.Surface((TAM_CORACAO, TAM_CORACAO), pygame.SRCALPHA)

    desenho = [
        '..###...###..',
        '.#####.#####.',
        '#############',
        '#############',
        '#############',
        '.###########.',
        '..#########..',
        '...#######...',
        '....#####....',
        '.....###.....',
        '......#......',
    ]

    tamanho_pixel = 3
    largura_desenho = len(desenho[0]) * tamanho_pixel
    altura_desenho = len(desenho) * tamanho_pixel
    origem_x = (TAM_CORACAO - largura_desenho) // 2
    origem_y = (TAM_CORACAO - altura_desenho) // 2

    matriz = [[c == '#' for c in linha] for linha in desenho]
    linhas = len(matriz)
    colunas = len(matriz[0])

    for y in range(linhas):
        for x in range(colunas):
            if matriz[y][x]:
                pygame.draw.rect(
                    canvas,
                    (92, 20, 28, 255),
                    (
                        origem_x + x * tamanho_pixel,
                        origem_y + y * tamanho_pixel,
                        tamanho_pixel,
                        tamanho_pixel,
                    ),
                )

    for y in range(1, linhas - 1):
        for x in range(1, colunas - 1):
            if not matriz[y][x]:
                continue

            vizinhos = (
                matriz[y - 1][x]
                and matriz[y + 1][x]
                and matriz[y][x - 1]
                and matriz[y][x + 1]
            )

            if vizinhos:
                pygame.draw.rect(
                    canvas,
                    (235, 48, 62, 255),
                    (
                        origem_x + x * tamanho_pixel,
                        origem_y + y * tamanho_pixel,
                        tamanho_pixel,
                        tamanho_pixel,
                    ),
                )

    for x, y in [(3, 2), (4, 2), (3, 3)]:
        pygame.draw.rect(
            canvas,
            (255, 214, 218, 255),
            (
                origem_x + x * tamanho_pixel,
                origem_y + y * tamanho_pixel,
                tamanho_pixel,
                tamanho_pixel,
            ),
        )

    caminho = os.path.join(PASTA_AJUSTADOS, 'coracao_ajustado.png')
    pygame.image.save(canvas, caminho)
    return caminho


def criar_imagem_botao(nome, texto, cor_principal, cor_hover):
    garantir_pasta()

    pygame.font.init()
    fonte = pygame.font.SysFont('Arial Black', 34)
    caminhos = []

    for sufixo, cor in [('normal', cor_principal), ('hover', cor_hover)]:
        largura = 340
        altura = 78
        superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)

        pygame.draw.rect(
            superficie,
            (54, 35, 23, 255),
            pygame.Rect(0, 0, largura, altura),
            border_radius=16,
        )

        corpo = pygame.Rect(5, 5, largura - 10, altura - 10)
        pygame.draw.rect(superficie, cor, corpo, border_radius=12)

        sombra_cor = tuple(max(0, c - 45) for c in cor)
        pygame.draw.rect(
            superficie,
            sombra_cor,
            pygame.Rect(8, altura - 19, largura - 16, 11),
            border_radius=5,
        )

        pygame.draw.rect(
            superficie,
            (255, 245, 205, 120),
            pygame.Rect(12, 10, largura - 24, 5),
            border_radius=3,
        )

        texto_sombra = fonte.render(texto, True, (62, 35, 22))
        texto_branco = fonte.render(texto, True, (255, 255, 255))
        rect_texto = texto_branco.get_rect(center=(largura // 2, altura // 2 - 1))

        superficie.blit(texto_sombra, (rect_texto.x + 3, rect_texto.y + 3))
        superficie.blit(texto_branco, rect_texto)

        caminho = os.path.join(PASTA_AJUSTADOS, f'{nome}_{sufixo}.png')
        pygame.image.save(superficie, caminho)
        caminhos.append(caminho)

    return caminhos[0], caminhos[1]


def ajustar_sheet(nome, frames, largura_frame, altura_frame, normalizar_por_frame=False, espelhar=False):
    garantir_pasta()
    imagem = pygame.image.load(nome).convert_alpha()
    largura_original = imagem.get_width()
    altura_original = imagem.get_height()
    largura_original_frame = largura_original // frames
    recortes = []
    maior_largura = 0
    maior_altura = 0

    for i in range(frames):
        frame = imagem.subsurface((i * largura_original_frame, 0, largura_original_frame, altura_original))
        rect = frame.get_bounding_rect()
        recortes.append(rect)
        maior_largura = max(maior_largura, rect.width)
        maior_altura = max(maior_altura, rect.height)

    if maior_largura > 0 and maior_altura > 0:
        escala_unica = min(largura_frame * 0.95 / maior_largura, altura_frame * 0.95 / maior_altura)
    else:
        escala_unica = 1

    nova_sheet = pygame.Surface((largura_frame * frames, altura_frame), pygame.SRCALPHA)

    for i in range(frames):
        frame_original = imagem.subsurface((i * largura_original_frame, 0, largura_original_frame, altura_original))
        rect = recortes[i]
        if rect.width == 0 or rect.height == 0:
            continue

        frame = frame_original.subsurface(rect)
        if espelhar:
            frame = pygame.transform.flip(frame, True, False)

        if normalizar_por_frame:
            escala = min(largura_frame * 0.92 / frame.get_width(), altura_frame * 0.92 / frame.get_height())
        else:
            escala = escala_unica

        nova_largura = int(frame.get_width() * escala)
        nova_altura = int(frame.get_height() * escala)
        frame = pygame.transform.scale(frame, (nova_largura, nova_altura))
        x = i * largura_frame + (largura_frame - nova_largura) // 2
        y = altura_frame - nova_altura
        nova_sheet.blit(frame, (x, y))

    caminho = os.path.join(PASTA_AJUSTADOS, nome)
    pygame.image.save(nova_sheet, caminho)
    return caminho


def ajustar_tiro(nome, frames):
    garantir_pasta()
    imagem = pygame.image.load(nome).convert_alpha()
    largura_original = imagem.get_width()
    altura_original = imagem.get_height()
    colunas_ocupadas = []

    for x in range(largura_original):
        ocupada = False
        for y in range(altura_original):
            if imagem.get_at((x, y)).a > 10:
                ocupada = True
                break
        colunas_ocupadas.append(ocupada)

    blocos = []
    inicio = None

    for x in range(largura_original):
        if colunas_ocupadas[x] and inicio is None:
            inicio = x
        if inicio is not None:
            terminou = not colunas_ocupadas[x] or x == largura_original - 1
            if terminou:
                fim = x - 1
                if x == largura_original - 1 and colunas_ocupadas[x]:
                    fim = x
                blocos.append((inicio, fim))
                inicio = None

    if len(blocos) != frames:
        xs_visiveis = [x for x, ocupado in enumerate(colunas_ocupadas) if ocupado]
        if not xs_visiveis:
            raise ValueError('tiro.png não possui pixels visíveis')

        primeiro = xs_visiveis[0]
        ultimo = xs_visiveis[-1]
        gaps = []
        gap_inicio = None

        for x in range(primeiro, ultimo + 1):
            if not colunas_ocupadas[x] and gap_inicio is None:
                gap_inicio = x
            if gap_inicio is not None:
                terminou_gap = colunas_ocupadas[x] or x == ultimo
                if terminou_gap:
                    gap_fim = x - 1
                    if x == ultimo and not colunas_ocupadas[x]:
                        gap_fim = x
                    gaps.append((gap_fim - gap_inicio + 1, gap_inicio, gap_fim))
                    gap_inicio = None

        gaps.sort(reverse=True)
        separadores = sorted(gaps[:frames - 1], key=lambda g: g[1])
        limites = [primeiro]

        for _, a, b in separadores:
            limites.append((a + b) // 2)

        limites.append(ultimo + 1)
        blocos = []

        for i in range(frames):
            blocos.append((limites[i], limites[i + 1] - 1))

    frames_recortados = []
    maior_largura = 0
    maior_altura = 0

    for inicio_x, fim_x in blocos[:frames]:
        largura_bloco = fim_x - inicio_x + 1
        trecho = imagem.subsurface((inicio_x, 0, largura_bloco, altura_original)).copy()
        rect = trecho.get_bounding_rect()

        if rect.width == 0 or rect.height == 0:
            frame = pygame.Surface((1, 1), pygame.SRCALPHA)
        else:
            frame = trecho.subsurface(rect).copy()

        frames_recortados.append(frame)
        maior_largura = max(maior_largura, frame.get_width())
        maior_altura = max(maior_altura, frame.get_height())

    if len(frames_recortados) != frames:
        raise ValueError(f'Foram encontrados {len(frames_recortados)} frames no tiro.png, mas deveriam existir {frames}.')

    escala = min(LARG_TIRO * 0.92 / maior_largura, ALT_TIRO * 0.86 / maior_altura)
    nova_sheet = pygame.Surface((LARG_TIRO * frames, ALT_TIRO), pygame.SRCALPHA)

    for i, frame in enumerate(frames_recortados):
        nova_largura = max(1, int(frame.get_width() * escala))
        nova_altura = max(1, int(frame.get_height() * escala))
        frame = pygame.transform.scale(frame, (nova_largura, nova_altura))
        x = i * LARG_TIRO + (LARG_TIRO - nova_largura) // 2
        y = (ALT_TIRO - nova_altura) // 2
        nova_sheet.blit(frame, (x, y))

    caminho = os.path.join(PASTA_AJUSTADOS, 'tiro_ajustado.png')
    pygame.image.save(nova_sheet, caminho)
    return caminho


def preparar_obstaculos(nome):
    garantir_pasta()
    imagem = pygame.image.load(nome).convert_alpha()
    recortes = [
        pygame.Rect(42, 294, 195, 186),
        pygame.Rect(279, 283, 197, 203),
        pygame.Rect(513, 298, 239, 185),
        pygame.Rect(771, 299, 276, 189),
        pygame.Rect(1070, 291, 218, 197),
        pygame.Rect(1318, 257, 218, 231),
        pygame.Rect(1544, 336, 306, 152),
        pygame.Rect(1866, 307, 272, 181),
    ]

    nova_sheet = pygame.Surface((LARG_OBSTACULO * 8, ALT_OBSTACULO), pygame.SRCALPHA)
    hitboxes = []

    for i in range(8):
        rect = recortes[i]
        obstaculo = imagem.subsurface(rect).copy()
        escala = min(
            LARG_OBSTACULO * 0.92 / obstaculo.get_width(),
            ALT_OBSTACULO * 0.92 / obstaculo.get_height(),
        )
        nova_largura = int(obstaculo.get_width() * escala)
        nova_altura = int(obstaculo.get_height() * escala)
        obstaculo = pygame.transform.scale(obstaculo, (nova_largura, nova_altura))

        x_local = (LARG_OBSTACULO - nova_largura) // 2
        y_local = ALT_OBSTACULO - nova_altura
        x_sheet = i * LARG_OBSTACULO + x_local
        nova_sheet.blit(obstaculo, (x_sheet, y_local))

        hitbox = obstaculo.get_bounding_rect()
        hitbox.x += x_local
        hitbox.y += y_local
        hitboxes.append(hitbox)

    caminho = os.path.join(PASTA_AJUSTADOS, 'obstaculos_ajustados.png')
    pygame.image.save(nova_sheet, caminho)
    return caminho, hitboxes



def preparar_sheet_boss(caminho_base, fase, tamanho, multiplicador_cor):
    """Cria o visual final do chefe a partir da arte-base do jogo.

    Mantem a animacao original, mas aplica identidade de cor, contorno forte
    e alinhamento por frame. O contorno acompanha apenas os pixels visiveis,
    entao nao cria circulos/blocos no fundo transparente.
    """
    garantir_pasta()

    imagem = pygame.image.load(caminho_base).convert_alpha()
    frames = 4
    largura_frame = imagem.get_width() // frames
    altura_frame = imagem.get_height()
    sheet = pygame.Surface((tamanho * frames, tamanho), pygame.SRCALPHA)

    cores_contorno = {
        1: (55, 145, 210, 210),
        2: (185, 125, 45, 220),
        3: (80, 135, 75, 220),
        4: (125, 70, 185, 225),
        5: (150, 25, 35, 235),
    }
    cor_contorno = cores_contorno.get(fase, (70, 70, 70, 210))
    espessura = 4 if fase < 5 else 6

    for i in range(frames):
        original = imagem.subsurface((i * largura_frame, 0, largura_frame, altura_frame)).copy()
        rect_original = original.get_bounding_rect()
        if rect_original.width == 0 or rect_original.height == 0:
            continue

        original = original.subsurface(rect_original).copy()
        escala = min((tamanho - espessura * 4) / original.get_width(),
                     (tamanho - espessura * 4) / original.get_height())
        nw = max(1, int(original.get_width() * escala))
        nh = max(1, int(original.get_height() * escala))
        frame = pygame.transform.smoothscale(original, (nw, nh))
        frame.fill((*multiplicador_cor, 255), special_flags=pygame.BLEND_RGBA_MULT)

        canvas = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        x = (tamanho - nw) // 2
        y = tamanho - nh - espessura * 2 if fase in (2, 3) else (tamanho - nh) // 2

        mask = pygame.mask.from_surface(frame)
        silhueta = mask.to_surface(
            setcolor=cor_contorno,
            unsetcolor=(0, 0, 0, 0),
        ).convert_alpha()

        # Contorno escuro + contorno colorido: deixa o chefe legivel contra o fundo.
        sombra = mask.to_surface(
            setcolor=(18, 20, 22, 235),
            unsetcolor=(0, 0, 0, 0),
        ).convert_alpha()
        for dx, dy in ((-espessura, 0), (espessura, 0), (0, -espessura), (0, espessura),
                       (-espessura, -espessura), (espessura, -espessura),
                       (-espessura, espessura), (espessura, espessura)):
            canvas.blit(sombra, (x + dx, y + dy))

        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            canvas.blit(silhueta, (x + dx, y + dy))

        canvas.blit(frame, (x, y))

        # Pequenos brilhos recortados no proprio personagem para dar acabamento,
        # sem preencher o fundo transparente.
        brilho = frame.copy()
        brilho.fill((32, 32, 32, 0), special_flags=pygame.BLEND_RGB_ADD)
        brilho.set_alpha(48 if fase < 5 else 70)
        canvas.blit(brilho, (x - 1, y - 1))

        sheet.blit(canvas, (i * tamanho, 0))

    caminho = os.path.join(PASTA_AJUSTADOS, f'boss_{fase}.png')
    pygame.image.save(sheet, caminho)
    return caminho

def preparar_tiros_boss():
    garantir_pasta()

    caminhos = []
    for nome, tamanho, forte in [
        ('tiro_boss.png', TAM_TIRO_BOSS, False),
        ('tiro_boss_forte.png', TAM_TIRO_BOSS + 10, True),
    ]:
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = tamanho // 2
        raio = tamanho // 2 - 2

        pygame.draw.circle(surf, (255, 112, 38, 95), (centro, centro), raio)
        pygame.draw.circle(surf, (255, 66, 35, 235), (centro, centro), max(3, raio - 4))
        pygame.draw.circle(
            surf,
            (255, 235, 120, 255) if not forte else (255, 245, 210, 255),
            (centro - 3, centro - 3),
            max(2, raio // 3),
        )

        if forte:
            pygame.draw.circle(surf, (255, 225, 105, 220), (centro, centro), raio, 3)

        caminho = os.path.join(PASTA_AJUSTADOS, nome)
        pygame.image.save(surf, caminho)
        caminhos.append(caminho)

    return caminhos[0], caminhos[1]



def preparar_tiros_armas():
    """Cria cinco projeteis visuais diferentes, um para cada arma."""
    garantir_pasta()
    caminhos = {}

    # NORMAL - bala dourada curta com nucleo branco
    surf = pygame.Surface((44, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 188, 55, 150), (0, 3, 44, 12))
    pygame.draw.ellipse(surf, (255, 226, 95, 255), (8, 4, 32, 10))
    pygame.draw.ellipse(surf, (255, 255, 225, 255), (27, 6, 12, 6))
    caminhos['normal'] = os.path.join(PASTA_AJUSTADOS, 'tiro_normal.png')
    pygame.image.save(surf, caminhos['normal'])

    # RAPIDA - dardo fino azul/ciano
    surf = pygame.Surface((54, 12), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (50, 180, 255, 120), [(0,6),(22,1),(54,6),(22,11)])
    pygame.draw.polygon(surf, (105, 235, 255, 255), [(10,6),(30,3),(52,6),(30,9)])
    pygame.draw.line(surf, (235,255,255,255), (25,6), (49,6), 2)
    caminhos['rapida'] = os.path.join(PASTA_AJUSTADOS, 'tiro_rapida.png')
    pygame.image.save(surf, caminhos['rapida'])

    # PESADA - esfera/bola de energia laranja, bem maior
    surf = pygame.Surface((38, 38), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 82, 38, 105), (19,19), 18)
    pygame.draw.circle(surf, (255, 112, 55, 255), (19,19), 14)
    pygame.draw.circle(surf, (255, 212, 105, 255), (15,15), 7)
    pygame.draw.circle(surf, (255, 250, 220, 255), (13,13), 3)
    caminhos['pesada'] = os.path.join(PASTA_AJUSTADOS, 'tiro_pesada.png')
    pygame.image.save(surf, caminhos['pesada'])

    # TRIPLA - cristal roxo, funciona bem mesmo quando viaja na diagonal
    surf = pygame.Surface((34, 24), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (110, 45, 180, 130), [(0,12),(17,0),(34,12),(17,24)])
    pygame.draw.polygon(surf, (202, 102, 255, 255), [(7,12),(17,4),(29,12),(17,20)])
    pygame.draw.polygon(surf, (244, 215, 255, 255), [(16,7),(25,12),(16,12)])
    caminhos['tripla'] = os.path.join(PASTA_AJUSTADOS, 'tiro_tripla.png')
    pygame.image.save(surf, caminhos['tripla'])

    # PERFURANTE - lanca verde longa
    surf = pygame.Surface((66, 16), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (70, 245, 135, 105), [(0,8),(48,1),(66,8),(48,15)])
    pygame.draw.rect(surf, (102, 245, 157, 255), (13,5,42,6), border_radius=3)
    pygame.draw.polygon(surf, (222, 255, 230, 255), [(48,3),(65,8),(48,13)])
    caminhos['perfurante'] = os.path.join(PASTA_AJUSTADOS, 'tiro_perfurante.png')
    pygame.image.save(surf, caminhos['perfurante'])

    return caminhos

def preparar_assets():
    fundo_path, fundo_menu_path, chao_path, grama_path = preparar_cenario()
    coracao_path = preparar_coracao()

    botao_jogar_path, botao_jogar_hover_path = criar_imagem_botao(
        'botao_jogar', 'JOGAR', (74, 166, 66), (99, 205, 86)
    )
    botao_sair_path, botao_sair_hover_path = criar_imagem_botao(
        'botao_sair', 'SAIR', (185, 66, 54), (224, 82, 64)
    )

    galinha_andando_path = ajustar_sheet('galinha_andando.png', 6, 96, 96, False)
    galinha_pulando_path = ajustar_sheet('galinha_pulando.png', 6, 96, 96, False)
    galinha_morre_path = ajustar_sheet('galinha_morre.png', 4, 96, 96, False)
    galinha_parada_path = ajustar_sheet('galinha_parada.png', 1, 96, 96, False)

    tiro_path = ajustar_tiro('tiro.png', 8)
    tiros_armas = preparar_tiros_armas()
    obstaculos_path, hitboxes_obstaculos = preparar_obstaculos('obstaculos.png')

    lesma_andando_path = ajustar_sheet('lesma_andando.png', 4, 96, 96, False, True)
    lesma_morre_path = ajustar_sheet('lesma_morre.png', 4, 96, 96, False, True)

    porco_andando_path = ajustar_sheet('porco_andando.png', 4, 96, 96, False, True)
    porco_morre_path = ajustar_sheet('porco_morre.png', 4, 96, 96, False, True)

    passaro_voando_path = ajustar_sheet('passaro_voando.png', 4, 96, 96, False, True)
    passaro_morre_path = ajustar_sheet('passaro_morre.png', 4, 96, 96, False, True)

    carangueijo_andando_path = ajustar_sheet('carangueijo_andando.png', 4, 96, 96, False, True)
    carangueijo_morre_path = None
    if os.path.exists('carangueijo_morre.png'):
        carangueijo_morre_path = ajustar_sheet('carangueijo_morre.png', 4, 96, 96, False, True)

    # Visuais finais dos chefes: cada um recebe identidade de cor e contorno
    # proprio, preservando as animacoes originais do projeto.
    boss_1_path = preparar_sheet_boss(passaro_voando_path, 1, TAM_BOSS, (145, 220, 255))
    boss_2_path = preparar_sheet_boss(lesma_andando_path, 2, TAM_BOSS, (255, 205, 135))
    boss_3_path = preparar_sheet_boss(porco_andando_path, 3, TAM_BOSS, (185, 255, 190))
    boss_4_path = preparar_sheet_boss(passaro_voando_path, 4, TAM_BOSS, (215, 155, 255))
    boss_5_path = preparar_sheet_boss(passaro_voando_path, 5, TAM_BOSS_FINAL, (255, 110, 110))
    tiro_boss_path, tiro_boss_forte_path = preparar_tiros_boss()

    return {
        'fundo': fundo_path,
        'fundo_menu': fundo_menu_path,
        'chao': chao_path,
        'grama_frente': grama_path,
        'coracao': coracao_path,
        'botao_jogar': botao_jogar_path,
        'botao_jogar_hover': botao_jogar_hover_path,
        'botao_sair': botao_sair_path,
        'botao_sair_hover': botao_sair_hover_path,
        'galinha_andando': galinha_andando_path,
        'galinha_pulando': galinha_pulando_path,
        'galinha_morre': galinha_morre_path,
        'galinha_parada': galinha_parada_path,
        'tiro': tiro_path,
        'tiro_normal': tiros_armas['normal'],
        'tiro_rapida': tiros_armas['rapida'],
        'tiro_pesada': tiros_armas['pesada'],
        'tiro_tripla': tiros_armas['tripla'],
        'tiro_perfurante': tiros_armas['perfurante'],
        'obstaculos': obstaculos_path,
        'hitboxes_obstaculos': hitboxes_obstaculos,
        'lesma_andando': lesma_andando_path,
        'lesma_morre': lesma_morre_path,
        'porco_andando': porco_andando_path,
        'porco_morre': porco_morre_path,
        'passaro_voando': passaro_voando_path,
        'passaro_morre': passaro_morre_path,
        'carangueijo_andando': carangueijo_andando_path,
        'carangueijo_morre': carangueijo_morre_path,
        'boss_1': boss_1_path,
        'boss_2': boss_2_path,
        'boss_3': boss_3_path,
        'boss_4': boss_4_path,
        'boss_5': boss_5_path,
        'tiro_boss': tiro_boss_path,
        'tiro_boss_forte': tiro_boss_forte_path,
    }
