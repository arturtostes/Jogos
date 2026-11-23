CHICKEN: THE GAME — RELEASE FINAL

COMO JOGAR A VERSAO DE CODIGO:
    py -3.12 main.py

CONTROLES:
- ENTER ou clique no botao inicial: comecar.
- ESPACO: pular.
- X: atirar.
- A/D ou setas: mover para os lados durante as lutas de boss.
- Mouse: menus, recompensas, arsenal e reinicio.
- F11: alternar tela cheia/janela.
- M: mutar/desmutar a musica.

PROGRESSAO:
- 5 fases com 60 segundos cada.
- Fases 1 a 4 terminam com miniboss.
- Fase 5 termina com o boss final.
- Ao terminar as fases 1 a 4, escolha 1 entre 3 cartas:
  2 buffs diferentes ou 1 arma nova.
- Depois da recompensa, escolha no arsenal qual arma desbloqueada usar.
- Cada fase nova normalmente comeca com 3 vidas.
- Com VIDA EXTRA, passa a comecar com 4 vidas e o maximo sobe de 4 para 5.
- O coracao especial recupera 1 vida ate o maximo atual.
- Ao morrer, a run volta para a Fase 1.
- Armas e upgrades conquistados permanecem salvos.

ARMAS:
- Normal.
- Rapida.
- Pesada.
- Tripla.
- Perfurante.
Cada arma possui projetil, dano, velocidade e cadencia proprios.

UPGRADES:
- Dano.
- Cadencia.
- Velocidade do tiro.
- Agilidade durante bosses.
- Tempo de invencibilidade.
- VIDA EXTRA: +1 vida inicial e +1 no maximo. Nivel unico.
- DOUBLE JUMP: permite um segundo pulo no ar. Nivel unico.

BALANCEAMENTO:
- Vida dos inimigos normais por fase: 2, 3, 4, 6 e 8.
- Boss final: 120 de vida.
- Lesma Colossal dispara uma rajada de 3 tiros em sequencia mirando o jogador,
  com ondulacao leve para manter o ataque legivel e esquivavel.
- Javali de Ferro investe ate o lado esquerdo da arena antes de retornar.

CHEFES:
1. FALCAO DA TEMPESTADE
2. LESMA COLOSSAL
3. JAVALI DE FERRO
4. GUARDIAO VIOLETA
5. IMPERADOR CARMESIM

SOM:
- menu.wav: menu/tela inicial.
- fase.wav: fases normais.
- miniboss.wav: minibosses 1 a 4.
- boss_final.wav: boss final.
As quatro trilhas sao originais e fazem parte do jogo.

SAVE:
Na versao final, o progresso fica fora dos arquivos do jogo.
No Windows ele e salvo em:
    %APPDATA%\ChickenTheGame\save.json
Isso permite que o save continue funcionando mesmo usando o executavel one-file.

TELA CHEIA:
O jogo usa resolucao logica 1280x720 e escala para o monitor sem alterar
colisoes, HUD ou coordenadas dos menus.

GERAR O EXECUTAVEL DO WINDOWS:
1. Tenha Python 3.12 instalado.
2. Dê dois cliques em GERAR_EXECUTAVEL.bat.
3. O script instala pygame/PyInstaller se necessario e gera:
       dist\CHICKEN_THE_GAME.exe
4. Para distribuir o jogo, voce pode enviar apenas esse .exe.
   O codigo-fonte nao precisa acompanhar o jogador.

OBSERVACAO:
O executavel e gerado como one-file e sem janela de console.
Na primeira abertura o Windows pode demorar alguns segundos para extrair
internamente os arquivos temporarios do jogo.
