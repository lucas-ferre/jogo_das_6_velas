# Guia de Como Jogar — O Ritual das 6 Velas

**O Ritual das 6 Velas** é um jogo de estratégia, sobrevivência e gerenciamento em tempo real/turnos ambientado em um santuário gótico imersivo. Seu objetivo é manter as chamas das 6 pilastras acesas durante a noite contra as forças da escuridão e as criaturas que espreitam nas sombras, resistindo até o amanhecer ou expurgando as trevas.

---

## 1. Fluxo de Preparação do Ritual

Antes de entrar no santuário, o jogador passa por 4 etapas interativas de customização e confirmação:

1. **Escolha de Arquétipo de Persona (1 a 5):** Define suas habilidades passivas e ativas `[Q]`.
2. **Escolha de Artefato Sagrado ou Tecnológico (1 a 5):** Define seu item de suporte e mecânicas auxiliares.
3. **Escolha de Bênção Divina (1 a 5):** Concede um efeito místico permanente para a partida.
4. **Resumo do Ritual (Tela de Confirmação):** Exibe um compêndio completo com o arquétipo escolhido, artefato, bênção e as metas de vitória/condições de derrota da partida antes do início.

---

## 2. Os 5 Arquétipos de Persona

| Arquétipo | Perfil | Habilidade Passiva | Habilidade Ativa `[Q]` |
| :--- | :--- | :--- | :--- |
| **O Zelador** | *Guardião das Brasas* | **Pavio Consagrado:** Reacender pilastras apagadas concede **+2 turnos extras** de queima inicial. | **Reserva de Emergência:** Forja 1 vela diretamente no bolso sem ir ao altar (Recarga: 25t). |
| **O Ocultista** | *Mestre dos Rituais* | **Ressonância Astral:** Recarga acelerada de artefatos (Cruz com 2 velas, Lanterna com 1 repouso, Câmera +1 carga, Bolsa com 65% de encantamento). | **Prece da Luz:** Consome 1 vela para banir e paralisar a criatura por 3 turnos (Recarga: 20t). |
| **O Andarilho** | *Passos nas Trevas* | **Passo Leve:** **40% de chance** de mover-se entre pilastras vizinhas da mesma coluna **sem gastar turnos** (ação livre). | **Sprint de Fuga:** Teletransporta-se instantaneamente de qualquer ponto para o Altar Central com custo 0 de turnos (Recarga: 25t). |
| **Aprendiz de Paladino** | *Espada da Luz* | **Vontade Inabalável:** Cada criatura expurgada eleva **permanentemente o piso de turnos mínimos das velas (+1t por expurgo)**. | **Julgamento Sagrado:** Expurga permanentemente 1 das criaturas das sombras (Recarga: 30t). **5 expurgos = Vitória Instantânea!** |
| **Nascido da Lua** | *Filho do Crepúsculo* | **Afinidade Lunar:** Sob penumbra ($\le 3$ velas acesas), ganha **+2 turnos extras** ao trocar velas e **50% de chance** de passos furtivos gratuitos. | **Eclipse Prateado:** Sob penumbra ($\le 3$ velas acesas), canaliza a luz da Lua e **congela o tempo de queima de todas as velas restantes por 2 rodadas completas** (Recarga: 25t). |

---

## 3. Os 5 Artefatos

1. **Cruz de Prata (Defesa & Ressurreição):**
   - *Bênção Radiante:* +1 turno bônus a todas as velas trocadas.
   - *Ressurreição Sagrada:* Ao apagar todas as 6 velas, explode em luz e **reacende 2 pilastras com fogo sagrado (+4t cada)**.
   - *Recarga:* Recarrega automaticamente quando 3 velas estiverem acesas (2 velas para o Ocultista).

2. **Lampião Espectral (Sustentação Tática & Visão):**
   - A chama da pilastra onde o jogador estiver **não consome turnos** (congelada no tempo).
   - Emite aura azul-celeste própria que expande o campo de visão na penumbra.

3. **Câmera Fotográfica Retrô (Flash de Sobrevivência):**
   - Possui **6 cargas de flash** (7 para o Ocultista).
   - Permite agir e sobreviver na escuridão total (0 velas acesas) gastando 1 carga por ação para ofuscar as criaturas.

4. **Bolsa Verde Musgo (Alquimia & Identificação por Cores):**
   - Expande a capacidade do inventário para **4 velas**.
   - Encanta velas no altar por cor:
     - 🟢 **Verde Esmeralda (Chama Maior):** +4 turnos extras de queima base.
     - 🔵 **Ciano Etéreo (Ação Livre):** Troca de vela com custo 0 de turnos.
     - 🟣 **Púrpura Mística (Altar Adjacente):** Estende a duração da pilastra vizinha em +3 turnos.

5. **Lanterna Moderna (Feixe de Longo Alcance & Recarga por Repouso):**
   - **9 cargas de bateria** e seletor de potência (`-` e `+`) no HUD.
   - Dispara feixes à distância sem gastar turnos (botão direito ou `Shift + 1..6`).
   - **Recarga por Repouso:** Ficar parado por 2 turnos (1 turno para o Ocultista) recupera **+3 cargas de bateria**.
   - **Super Queima:** Velas que atingirem $\ge 10$ turnos travam o decaimento por 3 rodadas.

---

## 4. As 5 Bênçãos Divinas

1. **Bênção do Fogo Perpétuo:**
   - Velas que chegam a `0 turnos` não se extinguem de imediato; entram em estado de **Brasa Latente** por **+1 rodada extra** de sobrevida antes de apagar definitivamente.
2. **Bênção dos Passos Silenciosos:**
   - Reduz a velocidade de aproximação da criatura em **35%**, mantendo o cerco contido por mais tempo e ampliando o raio de visão.
3. **Bênção da Abundância Ancestral:**
   - Concede **40% de chance** no Altar Central de forjar **Velas Douradas Consagradas** (que queimam pelo **dobro da duração normal** da pilastra).
4. **Bênção da Sincronia Cósmica:**
   - Ao renovar uma vela em qualquer pilastra, se a pilastra espelhada oposta (E1 $\leftrightarrow$ D1, E2 $\leftrightarrow$ D2, E3 $\leftrightarrow$ D3) estiver acesa, **ambas ganham +2 turnos de queima sincronizada**.
5. **Bênção da Sobrecarga de Adrenalina:**
   - Uma única vez por partida, ao apagar todas as 6 velas, o Altar detona uma onda de luz que **reacende 3 pilastras aleatórias (+5t)**, concede **2 movimentos com custo 0 de turnos**, e transporta o jogador ao centro (o Altar fica exausto por 3 turnos).

---

## 5. Modos de Jogo & Metas de Vitória

### Metas por Arquétipo e Dificuldade
Para vencer pelo tempo, mantenha o salão aceso até que a meta de turnos seja atingida. Ao completar a meta, a Lua se põe, o Sol dourado surge no vitral gótico e a luz matinal banha todo o salão, selando as trevas:

| Arquétipo | Suave (Lua Azul, $-10$t) | Padrão (Lua Prateada) | Horror (Lua Vermelha, $+15$t) | Noite Sem Fim (Lua Violeta) |
| :--- | :---: | :---: | :---: | :---: |
| **Nascido da Lua** | **50 Rodadas** | **60 Rodadas** | **75 Rodadas** | $\infty$ |
| **O Ocultista** | **55 Rodadas** | **65 Rodadas** | **80 Rodadas** | $\infty$ |
| **O Andarilho** | **60 Rodadas** | **70 Rodadas** | **85 Rodadas** | $\infty$ |
| **O Zelador** | **65 Rodadas** | **75 Rodadas** | **90 Rodadas** | $\infty$ |
| **Aprendiz de Paladino** | **70 Rodadas** | **80 Rodadas** | **95 Rodadas** | $\infty$ *(ou 5 Expurgos)* |

* **Vitória Sagrada Alternativa (Paladino):** Expurgar todas as 5 criaturas com `[Q]` garante vitória instantânea a qualquer momento.
* **Modo Noite Sem Fim:** Não há meta de turnos e o sol nunca nasce; o objetivo é sobreviver ao máximo de turnos possível.

---

## 6. Comandos e Atalhos

* `1` a `6` ou `Clique Esquerdo`: Mover até a Pilastra correspondente
* `Q` ou `Botão HUD`: Usar Habilidade Ativa do Arquétipo
* `Clique Direito` ou `Shift + 1..6`: Disparar feixe da Lanterna Moderna à distância
* `C` ou `0`: Mover para o Altar Central / Reabastecer velas
* `Espaço` / `Enter` / `R` / `E`: Trocar vela na pilastra atual
* `-` / `+`: Ajustar potência da Lanterna Moderna no HUD
* `W`: Esperar / Passar o turno (Recarrega Lanterna ao ficar parado)
* `F11`: Alternar modo Janela / Tela Cheia
* `ESC`: Pausar / Voltar ao Menu
