# O Ritual das 6 Velas — Arquitetura Técnica & Documentação de Engenharia

Um motor de jogo tático de sobrevivência em turnos com iluminação 2D dinâmica, sintetizador de áudio procedural puramente matemático, máquina de estados desacoplada e renderização gráfica em camadas com Pygame.

Para instruções de gameplay, arquétipos e regras de jogo, consulte o [GUIA_DE_COMO_JOGAR.md](GUIA_DE_COMO_JOGAR.md).

---

## Demonstração Visual

### Tela Inicial
![Tela Inicial do Ritual das 6 Velas](tela%20inicial.gif)

### Exemplo de Gameplay
<video src="exemplo%20de%20gameplay.mp4" width="100%" controls></video>

---

## 1. Arquitetura do Sistema & Padrões de Projeto

O projeto adota uma arquitetura inspirada em **MVC (Model-View-Controller)** com forte desacoplamento entre simulação lógica, renderização gráfica e síntese sonora:

```
                  ┌─────────────────────────────────┐
                  │             main.py             │
                  │ (Game Loop, Eventos & FSM)      │
                  └───────────────┬─────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  game_engine.py  │    │   renderer.py    │    │ sound_manager.py │
│ (Lógica & Turnos)│    │(Pipeline Gráfico)│    │(Áudio Procedural)│
└────────┬─────────┘    └────────┬─────────┘    └──────────────────┘
         │                       │
         ▼                       │
┌──────────────────┐             │
│    models.py     │◄────────────┘
│ (Modelos & Dados)│
└──────────────────┘
```

### Padrões de Projeto Utilizados:
* **Finite State Machine (FSM):** Gerencia transições entre telas (`MENU`, `PERSONA_SELECT`, `ARTIFACT_SELECT`, `BLESSING_SELECT`, `RITUAL_SUMMARY`, `PLAYING`, `UPGRADES`, `SETTINGS`, `GAME_OVER`).
* **Model-View-Controller (MVC):** `models.py` (Dados puros), `renderer.py` (View desacoplada que aceita superfícies/estados), `game_engine.py` (Controller/Regras de domínio).
* **Flyweight & Data Classes:** Encantamentos, velas e modificadores de arquétipos encapsulados em instâncias leves.
* **Observer / Callback Hooking:** Notificações de eventos e gatilhos de sobrevida/ressurreição desacoplados.

---

## 2. Estrutura Modular dos Componentes

| Módulo | Responsabilidade Técnica | Principais Classes & Funções |
| :--- | :--- | :--- |
| [`main.py`](main.py) | Ponto de entrada, loop principal a 60 FPS, despacho de eventos (teclado/mouse), interpolação de delta time e controle da FSM. | `main()`, `toggle_screen_mode()` |
| [`game_engine.py`](game_engine.py) | Mecânicas de jogo, regras de queima dinâmica, turnos de espera, travas de ação por visita, sinergias de arquétipo e vitória/derrota. | `GameEngine` |
| [`models.py`](models.py) | Estruturas de dados das entidades: pilastras, velas, itens, arquétipos, artefatos, bênçãos e a criatura da penumbra. | `Pillar`, `Candle`, `Player`, `Artifact`, `Persona`, `Blessing`, `Creature`, `CandleItem` |
| [`renderer.py`](renderer.py) | Pipeline visual completo: iluminação subtrativa 2D, renderização da vidraça gótica, nuvens em paralaxe, feixes volumétricos, interpolações e HUD. | `Renderer` |
| [`sound_manager.py`](sound_manager.py) | Sintetizador de áudio 8-bits baseado em NumPy e Pygame Sound, gerando ondas quadradas, dente de serra e ruído proceduralmente sem arquivos de mídia externos. | `SoundManager` |
| [`constants.py`](constants.py) | Dicionários de cores hex/RGB, posições dos nós do salão, constantes de estado, mapeamento de dificuldades e metas de vitória. | `PILLAR_POSITIONS`, `get_target_victory_turns()` |

---

## 3. Pipeline de Renderização & Iluminação 2D

A renderização do gameplay em [`renderer.py`](renderer.py) é executada em camadas estritas (*render passes*) para garantir fidelidade visual, sombras dinâmicas e efeitos de pós-processamento:

```
[Fill Background]
       │
       ▼
[Draw Floor & Corridors]
       │
       ▼
[Draw Gothic Window (Céu, Lua/Sol, Nuvens Parallax, Moldura em Arco)]
       │
       ▼
[Draw Altar & 6 Pillars]
       │
       ▼
[Draw Particles & Player Sprite]
       │
       ▼
[Draw Subtractive Lighting & Encroaching Creature Eyes]
       │
       ▼
[Draw Window Volumetric Beams (God Rays / Moonbeams)]
       │
       ▼
[Draw Special FX (Camera Flash, Silver Burst, Purge Burst, Laser Beam)]
       │
       ▼
[Draw HUD & Compendium Modals]
```

### Iluminação Subtrativa com Alpha Blending
Para simular a escuridão do salão e o campo de visão das chamas:
1. Uma superfície de escuridão opaca `dark_surf` preenche toda a tela com cor base `(8, 12, 20, base_darkness)`.
2. Para cada vela acesa, gera-se uma superfície radial com gradiente de luz e aplica-se `special_flags=pygame.BLEND_RGBA_SUB`.
3. Fontes de luz adicionais (Altar, Lampião, Feixes) subtraem a escuridão em tempo real, criando iluminação dinâmica com círculos de luz suaves.

### Vidraça & Nuvens Procedurais
* **Geometria de Máscara:** Arco semicircular esticado recortado através de `pygame.draw.ellipse` e `pygame.draw.rect` aplicado com `BLEND_RGBA_MIN`.
* **Paralaxe Contínuo:** Três camadas de nuvens (`cloud_col_back`, `cloud_col_mid`, `cloud_col_fore`) deslocadas por funções lineares contínuas moduladas no tempo (`t = time_elapsed`), operando a 60 FPS independentemente do avanço de turnos do jogador.
* **Trajetória Celestial:** A posição da Lua é calculada por interpolação parabólica `(x, y) = f(prog, t)`:
  $$x = 50 + \text{prog} \cdot (W - 100) + 7 \cdot \sin(0.7t)$$
  $$y = 92 - 44 \cdot \sin(\text{prog} \cdot \pi) + 4 \cdot \cos(0.5t)$$

---

## 4. Síntese de Áudio Procedural

O módulo [`sound_manager.py`](sound_manager.py) sintetiza todos os efeitos sonoros da partida em tempo de execução via **NumPy**, sem depender de arquivos `.wav` ou `.mp3` no disco:

* **Taxa de Amostragem:** $22.050\text{ Hz}$, $16\text{-bit signed mono}$.
* **Formas de Onda:**
  * **Onda Quadrada (Square):** $\text{sign}(\sin(2\pi f t))$
  * **Onda Dente de Serra (Sawtooth):** $2(f t - \lfloor f t + 0.5 \rfloor)$
  * **Onda Senoidal Pura (Sine):** $\sin(2\pi f t)$
  * **Ruído Branco (Noise):** Distribuição uniforme $U(-1, 1)$
* **Envelopes ADSR:** Modulação linear e exponencial de amplitude para evitar estalos (*clicks*) e conferir textura sonora retro/8-bits.

---

## 5. Mecânicas de Simulação & Queima

A simulação de turnos em [`game_engine.py`](game_engine.py) opera de forma determinística:

1. **Decaimento Dinâmico:** A cada ação que consome turno, as velas ativas reduzem em $1$ turno de queima (exceto sob travas de congelamento como *Lampião Espectral*, *Eclipse Prateado* ou *Super Queima da Lanterna*).
2. **Piso Mínimo de Duração:** Ao reacender uma pilastra, a nova duração é calculada dinamicamente:
   $$\text{duração} = \max(\text{min\_floor}, \text{base\_burn} - \text{extinguished\_count} + \text{bonuses})$$
3. **Aproximação da Criatura:**
   $$\text{target\_proximity} = \frac{\max(0, \text{extinguished} - \text{purged})}{6} \times \text{stealth\_rate}$$
   O deslocamento dos olhos das criaturas no salão interpola continuamente em direção ao Altar Central via aproximação assintótica.

---

## 6. Instalação, Execução & Requisitos

### Pré-requisitos
* Python 3.9 ou superior
* Pip

### Dependências
As dependências do projeto estão listadas em [`requirements.txt`](requirements.txt):
* `pygame>=2.5.0`
* `numpy>=1.24.0`

### Instalação & Execução

```bash
# 1. Clone o repositório ou navegue até a pasta do projeto:
cd "jogo de 6 velas"

# 2. Instale as dependências:
pip install -r requirements.txt

# 3. Inicie o jogo:
python main.py
```

---

## 7. Testes Automatizados & Verificação Headless

O jogo suporta execução de testes automatizados e benchmarks em modo *headless* (sem display físico ou servidor X11) através do driver virtual SDL:

```bash
python -c "
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame, constants, game_engine, renderer

pygame.init()
screen = pygame.display.set_mode((1000, 700))
eng = game_engine.GameEngine('CROSS', constants.PERSONA_CARETAKER, constants.DIFFICULTY_NORMAL, constants.BLESSING_FIRE)
rend = renderer.Renderer(screen)
rend.render_gameplay(eng, (500, 350))
print('Simulação Headless executada com sucesso!')
"
```
