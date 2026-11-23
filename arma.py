import math


class Arma:
    def __init__(self, id_arma, nome, descricao, cooldown, velocidade, dano,
                 angulos=None, penetracao=1, cor=(255,255,255), asset_key=None):
        self.id = id_arma
        self.nome = nome
        self.descricao = descricao
        self.cooldown = cooldown
        self.velocidade = velocidade
        self.dano = dano
        self.angulos = angulos if angulos is not None else [0.0]
        self.penetracao = penetracao
        self.cor = cor
        self.asset_key = asset_key or f'tiro_{id_arma}'


ARSENAL = {
    'normal': Arma('normal', 'NORMAL', 'Equilibrada e confiavel', 0.60, 750, 1,
                   cor=(255, 222, 86)),
    'rapida': Arma('rapida', 'RAPIDA', 'Cadencia muito alta', 0.28, 900, 1,
                   cor=(88, 225, 255)),
    'pesada': Arma('pesada', 'PESADA', 'Muito dano por disparo', 1.00, 650, 3,
                   cor=(255, 105, 72)),
    'tripla': Arma('tripla', 'TRIPLA', 'Dispara em tres direcoes', 0.75, 720, 1,
                   angulos=[math.radians(-11), 0.0, math.radians(11)],
                   cor=(205, 118, 255)),
    'perfurante': Arma('perfurante', 'PERFURANTE', 'Atravessa ate 3 inimigos', 0.85, 800, 1,
                       penetracao=3, cor=(102, 245, 157)),
}

ORDEM_ARMAS = ['normal', 'rapida', 'pesada', 'tripla', 'perfurante']


def obter_arma(id_arma):
    return ARSENAL.get(id_arma, ARSENAL['normal'])


def todas_as_armas():
    return [ARSENAL[id_arma] for id_arma in ORDEM_ARMAS]


def armas_bloqueadas(desbloqueadas):
    return [id_arma for id_arma in ORDEM_ARMAS if id_arma not in desbloqueadas]
