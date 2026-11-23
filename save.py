import json
import os
import shutil


class GerenciadorSave:
    def __init__(self, nome_arquivo='save.json'):
        # Save fora dos arquivos empacotados para funcionar também no .exe one-file.
        if os.name == 'nt':
            base = os.environ.get('APPDATA') or os.path.expanduser('~')
            pasta_save = os.path.join(base, 'ChickenTheGame')
        else:
            pasta_save = os.path.join(os.path.expanduser('~'), '.chicken_the_game')

        os.makedirs(pasta_save, exist_ok=True)
        self.caminho = os.path.join(pasta_save, nome_arquivo)

        # Migra automaticamente um save antigo da pasta do projeto, se existir.
        pasta_projeto = os.path.dirname(os.path.abspath(__file__))
        save_antigo = os.path.join(pasta_projeto, nome_arquivo)
        if not os.path.isfile(self.caminho) and os.path.isfile(save_antigo):
            try:
                shutil.copy2(save_antigo, self.caminho)
            except OSError:
                pass

    def dados_padrao(self):
        return {
            'fase': 1,
            'armas': ['normal'],
            'arma_selecionada': 'normal',
            'upgrades': {},
            'jogo_concluido': False,
        }

    def existe(self):
        return os.path.isfile(self.caminho)

    def carregar(self):
        if not self.existe():
            return self.dados_padrao()
        try:
            with open(self.caminho, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
        except (OSError, json.JSONDecodeError):
            return self.dados_padrao()
        padrao = self.dados_padrao()
        padrao.update(dados)
        try:
            padrao['fase'] = max(1, min(5, int(padrao.get('fase', 1))))
        except (TypeError, ValueError):
            padrao['fase'] = 1
        if not isinstance(padrao.get('armas'), list) or not padrao['armas']:
            padrao['armas'] = ['normal']
        if 'normal' not in padrao['armas']:
            padrao['armas'].insert(0, 'normal')
        if not isinstance(padrao.get('upgrades'), dict):
            padrao['upgrades'] = {}
        if padrao.get('arma_selecionada') not in padrao['armas']:
            padrao['arma_selecionada'] = padrao['armas'][0]
        padrao['jogo_concluido'] = bool(padrao.get('jogo_concluido', False))
        return padrao

    def salvar(self, dados):
        try:
            with open(self.caminho, 'w', encoding='utf-8') as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=4)
            return True
        except OSError:
            return False

    def novo_jogo(self):
        dados = self.dados_padrao()
        self.salvar(dados)
        return dados

    def salvar_fase(self, fase, dados_atuais=None, jogo_concluido=False):
        dados = dados_atuais.copy() if isinstance(dados_atuais, dict) else self.carregar()
        dados['fase'] = max(1, min(5, int(fase)))
        dados['jogo_concluido'] = bool(jogo_concluido)
        self.salvar(dados)
        return dados

    def desbloquear_arma(self, id_arma, dados_atuais=None):
        dados = dados_atuais.copy() if isinstance(dados_atuais, dict) else self.carregar()
        armas = list(dados.get('armas', ['normal']))
        if id_arma not in armas:
            armas.append(id_arma)
        dados['armas'] = armas
        self.salvar(dados)
        return dados

    def aplicar_upgrade(self, id_upgrade, dados_atuais=None):
        dados = dados_atuais.copy() if isinstance(dados_atuais, dict) else self.carregar()
        upgrades = dict(dados.get('upgrades', {}))
        try:
            atual = int(upgrades.get(id_upgrade, 0))
        except (TypeError, ValueError):
            atual = 0
        upgrades[id_upgrade] = atual + 1
        dados['upgrades'] = upgrades
        self.salvar(dados)
        return dados

    def selecionar_arma(self, id_arma, dados_atuais=None):
        dados = dados_atuais.copy() if isinstance(dados_atuais, dict) else self.carregar()
        armas = list(dados.get('armas', ['normal']))
        if id_arma in armas:
            dados['arma_selecionada'] = id_arma
            self.salvar(dados)
        return dados

    def resetar_apos_morte(self, dados_atuais=None):
        dados = dados_atuais.copy() if isinstance(dados_atuais, dict) else self.carregar()
        dados['fase'] = 1
        dados['jogo_concluido'] = False
        self.salvar(dados)
        return dados
