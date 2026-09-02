# O Ritual das 6 Velas

Jogo de sobrevivência e gerenciamento em Python (Pygame) com atmosfera gótica sombria, sintetizador procedural de áudio 8-bits, sistema dinâmico de turnos, iluminação 2D, seletor de dificuldade com ambientação dinâmica (fases da Lua), sistema com 5 Arquétipos de Persona, 5 Artefatos Sagrados e 5 Bênçãos Divinas Pré-Ritual.

## Fluxo de Preparação do Ritual

Ao iniciar o jogo pelo Menu Principal, o jogador personaliza sua experiência em 3 etapas consecutivas:
1. **Escolha de Arquétipo de Persona (1 a 5)**
2. **Escolha de Artefato Sagrado & Tecnológico (1 a 5)**
3. **Escolha de Bênção Divina (1 a 5)** $\rightarrow$ **Início do Ritual**

---

## As 5 Bênçãos Divinas Pré-Ritual

1. **Bênção do Fogo Perpétuo:**
   - Velas que chegam a `0 turnos` **não se extinguem de imediato**; entram em estado de **Brasa Latente** por **+1 rodada extra** de sobrevida antes de apagar definitivamente.

2. **Bênção dos Passos Silenciosos:**
   - Reduz a velocidade de aproximação da criatura em **35%**, mantendo o cerco das sombras contido por mais tempo e ampliando o raio de visão na penumbra.

3. **Bênção da Abundância Ancestral:**
   - Concede **40% de chance** no Altar Central de forjar **Velas Douradas Consagradas** (que queimam pelo **dobro da duração normal** da pilastra).

4. **Bênção da Sincronia Cósmica:**
   - Ao renovar uma vela em qualquer pilastra, se a **pilastra espelhada oposta** (E1 $\leftrightarrow$ D1, E2 $\leftrightarrow$ D2, E3 $\leftrightarrow$ D3) estiver acesa, **ambas ganham +2 turnos de queima sincronizada**.

5. **Bênção do Segundo Fôlego:**
   - Uma única vez por partida, ao apagar todas as 6 velas, o Altar detona uma onda de luz que **reacende 3 pilastras aleatórias (+5t)** e transporta o jogador ao centro.
   - *Penalidade de Exaustão:* O Altar Central fica **exausto por 3 turnos**, impossibilitando reabastecer velas durante esse período.

---

## Os 5 Arquétipos de Persona

1. **O Zelador (Guardião das Brasas — Manutenção & Estabilidade):**
   - **Passiva (Pavio Consagrado):** Ao reacender uma pilastra apagada, concede **+2 turnos extras** de queima inicial.
   - **Ativa [Q] (Reserva de Emergência):** Reabastece 1 vela diretamente no bolso sem ir ao altar (Recarga: 25 turnos).

2. **O Ocultista (Mestre dos Rituais — Afinidade Espiritual & Sombras):**
   - **Passiva (Ressonância Astral):** Recarga acelerada de artefatos (Cruz ativa com 2 velas, Lanterna com 1 turno parado, Câmera +1 carga, Bolsa com 65% de chance de encantamento).
   - **Ativa [Q] (Prece da Luz):** Sacrifica 1 vela do inventário para repelir imediatamente a criatura por 3 turnos (Recarga: 20 turnos).

3. **O Andarilho (Passos nas Trevas — Mobilidade & Fuga):**
   - **Passiva (Passo Leve):** **40% de probabilidade** de se mover entre pilastras vizinhas da mesma coluna **sem gastar turnos** (ação livre de movimento).
   - **Ativa [Q] (Sprint de Fuga):** Teletransporta-se instantaneamente de qualquer pilastra para o Altar Central com custo 0 de turnos (Recarga: 25 turnos).

4. **Aprendiz de Paladino (Espada da Luz — Expurgo Sagrado & Piso de Turnos):**
   - **Passiva (Vontade Inabalável):** Cada criatura expurgada eleva **permanentemente o piso de turnos mínimos das velas (+1t por expurgo)**, amortecendo as perdas no ritual.
   - **Ativa [Q] (Julgamento Sagrado):** Expurga permanentemente 1 criatura das sombras, reduzindo o cerco da ameaça e aumentando a duração mínima das velas (Recarga: 30 turnos).

5. **Nascido da Lua (Filho do Crepúsculo — Poder na Penumbra):**
   - **Passiva (Afinidade Lunar):** Sob penumbra (com **3 ou menos velas acesas**), ganha **+2 turnos extras** de queima ao trocar velas e **50% de probabilidade** de realizar movimentos furtivos com custo 0 de turnos.
   - **Ativa [Q] (Eclipse Prateado):** Sob penumbra (<= 3 velas acesas), canaliza a luz da Lua e **congela o tempo de queima de todas as velas restantes por 2 rodadas completas** (Recarga: 25 turnos).

---

## Os 5 Artefatos Sagrados & Tecnológicos

1. **Cruz de Prata (Defesa & Ressurreição):**
   - *Bênção Radiante:* +1 turno bônus a todas as velas trocadas.
   - *Ressurreição Sagrada:* Ao apagar todas as 6 velas, explode em luz e **reacende 2 pilastras com fogo sagrado (+4t cada)**.
   - *Recarga:* Recarregada com 3 velas acesas (2 velas para o Ocultista).

2. **Lampião Espectral (Sustentação Tática & Visão):**
   - A chama da pilastra onde o jogador estiver **não consome turnos** (congelada no tempo).
   - Emite aura azul-celeste própria que expande o campo de visão.

3. **Câmera Fotográfica Retrô (Flash de Sobrevivência):**
   - Possui **6 cargas de flash** (7 para o Ocultista).
   - Permite agir na escuridão total (0 velas acesas) gastando 1 carga por ação para ofuscar as criaturas.

4. **Bolsa Verde Musgo (Alquimia & Identificação por Cores):**
   - Expande a capacidade do inventário para **4 velas**.
   - Encanta velas no altar por cor:
     - 🟢 **Verde Esmeralda (Chama Maior):** +4 turnos extras de queima.
     - 🔵 **Ciano Etéreo (Ação Livre):** Troca de vela com custo 0 de turnos.
     - 🟣 **Púrpura Mística (Altar Adjacente):** Estende a pilastra vizinha em +3 turnos.

5. **Lanterna Moderna (Feixe de Longo Alcance & Recarga por Repouso):**
   - **9 cargas de bateria** e seletor de potência (`-` e `+`) no HUD.
   - Dispara feixes à distância sem gastar turnos.
   - **Recarga por Repouso:** Ficar parado por 2 turnos (1 turno para o Ocultista) recupera **+3 cargas de bateria**.
   - **Super Queima:** Velas com mais de 10 turnos travam o decaimento por 2 rodadas.

---

## Regras de Troca de Velas & Travas de Ação

- **Troca Única por Visita:** Ao chegar a uma pilastra, o jogador só pode substituir a vela **uma única vez por visita**. 
- Tentativas subsequentes na mesma pilastra sem se mover para outro ponto são bloqueadas, prevenindo perdas acidentais de velas e turnos.

---

## Controles

- `1` a `6` / `Clique Esquerdo`: Mover até a Pilastra
- `Q` / `Botão HUD`: Usar Habilidade Ativa do Arquétipo
- `Clique Direito` / `Shift + 1..6`: Disparar feixe da Lanterna Moderna
- `C` ou `0`: Mover para o Altar Central / Reabastecer
- `Espaço` / `Enter` / `R` / `E`: Trocar vela na pilastra atual
- `-` / `+`: Ajustar potência da Lanterna Moderna
- `W`: Esperar um turno
- `Setas` / `WASD`: Navegação direcional
- `F11`: Alternar Tela Cheia / Janela
- `ESC`: Voltar ao Menu

## Instalação e Execução

```bash
pip install -r requirements.txt
python main.py
```
