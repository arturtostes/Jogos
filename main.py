import os

# Garante que sprites e soundtracks sejam encontrados mesmo se o jogo
# for iniciado por atalho ou a partir de outra pasta.
PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))
os.chdir(PASTA_JOGO)

from jogo import Jogo


if __name__ == '__main__':
    jogo = Jogo()
    jogo.executar()
