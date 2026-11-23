import random


BUFFS = {
    'dano': {
        'nome': 'DANO +',
        'descricao': 'Todos os tiros causam +1 de dano.',
        'max_nivel': 2,
        'cor': (255, 117, 102),
    },
    'cadencia': {
        'nome': 'CADENCIA +',
        'descricao': 'Recarga das armas fica 10% menor.',
        'max_nivel': 3,
        'cor': (255, 205, 86),
    },
    'velocidade_tiro': {
        'nome': 'TIRO VELOZ',
        'descricao': 'Projeteis ficam 12% mais rapidos.',
        'max_nivel': 3,
        'cor': (95, 210, 255),
    },
    'velocidade_player': {
        'nome': 'AGILIDADE',
        'descricao': 'Movimento lateral nos bosses fica 10% maior.',
        'max_nivel': 3,
        'cor': (118, 239, 165),
    },
    'vida_extra': {
        'nome': 'VIDA EXTRA',
        'descricao': 'Comece cada fase com +1 vida e aumente o maximo de vida em +1.',
        'max_nivel': 1,
        'cor': (255, 92, 118),
    },
    'double_jump': {
        'nome': 'DOUBLE JUMP',
        'descricao': 'Permite realizar um segundo pulo enquanto estiver no ar.',
        'max_nivel': 1,
        'cor': (108, 224, 255),
    },
    'invencibilidade': {
        'nome': 'RESISTENCIA',
        'descricao': 'Invencibilidade apos dano dura +0.5s.',
        'max_nivel': 3,
        'cor': (190, 140, 255),
    },
}


def nivel(upgrades, id_buff):
    try:
        return max(0, int(upgrades.get(id_buff, 0)))
    except (TypeError, ValueError):
        return 0


def gerar_buffs(upgrades, quantidade=2):
    disponiveis = [
        id_buff for id_buff, dados in BUFFS.items()
        if nivel(upgrades, id_buff) < dados['max_nivel']
    ]
    if len(disponiveis) >= quantidade:
        ids = random.sample(disponiveis, quantidade)
    else:
        ids = disponiveis[:]
        restantes = [x for x in BUFFS if x not in ids]
        while len(ids) < quantidade and restantes:
            ids.append(restantes.pop(0))
    return ids


def opcao_buff(id_buff, upgrades):
    dados = BUFFS[id_buff]
    atual = nivel(upgrades, id_buff)
    return {
        'tipo': 'buff',
        'id': id_buff,
        'nome': dados['nome'],
        'descricao': dados['descricao'],
        'nivel_atual': atual,
        'nivel_novo': min(dados['max_nivel'], atual + 1),
        'cor': dados['cor'],
    }
