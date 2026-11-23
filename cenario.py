from PPlay.sprite import Sprite
from config import LARGURA, CHAO_VISUAL_Y, VEL_MUNDO, GRAMA_FRENTE_Y


class Cenario:
    def __init__(self, assets):
        self.fundo = Sprite(assets['fundo'])

        chao_base = Sprite(assets['chao'])
        qtd_chao = int(LARGURA // chao_base.width) + 3
        self.chao_tiles = [chao_base] + [Sprite(assets['chao']) for _ in range(qtd_chao - 1)]

        for i, tile in enumerate(self.chao_tiles):
            tile.set_position(i * tile.width, CHAO_VISUAL_Y)

        # Grama de primeiro plano: rola junto com o mundo e e desenhada
        # depois dos personagens para cobrir levemente os pes.
        grama_base = Sprite(assets['grama_frente'])
        qtd_grama = int(LARGURA // grama_base.width) + 3
        self.grama_tiles = [grama_base] + [Sprite(assets['grama_frente']) for _ in range(qtd_grama - 1)]
        for i, tile in enumerate(self.grama_tiles):
            tile.set_position(i * tile.width, GRAMA_FRENTE_Y)

    def _atualizar_tiles(self, tiles, dt):
        for tile in tiles:
            tile.x -= VEL_MUNDO * dt

        for tile in tiles:
            if tile.x + tile.width <= 0:
                direita = max(outro.x for outro in tiles if outro is not tile)
                tile.x = direita + tile.width

    def atualizar(self, dt):
        self._atualizar_tiles(self.chao_tiles, dt)
        self._atualizar_tiles(self.grama_tiles, dt)

    def desenhar(self):
        self.fundo.draw()
        for tile in self.chao_tiles:
            tile.draw()

    def desenhar_frente(self):
        for tile in self.grama_tiles:
            tile.draw()
