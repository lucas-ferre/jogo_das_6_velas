import math
import random
from constants import INVENTORY_CAPACITY_BASE, PILLAR_POSITIONS, CENTER_POSITION

class Blessing:
    def __init__(self, blessing_type="FIRE"):
        self.type = blessing_type
        self.is_used = False

        if blessing_type == "FIRE":
            self.name = "Fogo Perpétuo"
            self.tag = "SOBREVIDA EM BRASAS"
            self.description = "Velas em 0 turnos ganham 1 rodada de brasa latente antes de se apagarem por completo."
        elif blessing_type == "STEALTH":
            self.name = "Passos Silenciosos"
            self.tag = "CONTROLE DE AMEAÇA"
            self.description = "A velocidade de aproximação da criatura é reduzida em 35% e amplia o raio de visão na penumbra."
        elif blessing_type == "ABUNDANCE":
            self.name = "Abundância Ancestral"
            self.tag = "VELAS DOURADAS"
            self.description = "40% de chance no Altar de obter Velas Douradas que queimam pelo dobro da duração normal."
        elif blessing_type == "SYNCHRONY":
            self.name = "Sincronia Cósmica"
            self.tag = "RESSONÂNCIA ESPELHADA"
            self.description = "Ao trocar uma vela, se a pilastra oposta espelhada estiver acesa, ambas ganham +2 turnos de queima."
        elif blessing_type in ("ADRENALINE", "SECOND_BREATH"):
            self.name = "Sobrecarga de Adrenalina"
            self.tag = "SURTO DE VELOCIDADE"
            self.description = "Sob perigo crítico (<= 2 velas acesas), concede 2 movimentos sem custo de turnos. Recarrega ao ter >= 4 velas."
        elif blessing_type == "VIGOROUS_BREATH":
            self.name = "Fôlego Vigoroso"
            self.tag = "PULSO DO ALTAR"
            self.description = "Ao retornar ao Altar Central com 0 velas no inventário, concede +1 turno de queima a todas as velas acesas."
        elif blessing_type == "THERMAL_BOND":
            self.name = "Vínculo Térmico"
            self.tag = "CALOR COMPARTILHADO"
            self.description = "Se uma vela estiver com 1t, absorve 1t de uma vela com >5t e ganha +2t (pode ser usado 1 vez a cada 4 turnos)."
        elif blessing_type == "WILL_O_WISP":
            self.name = "Fogo Fátuo"
            self.tag = "CINZAS ESPIRITUAIS"
            self.description = "Ao apagar uma vela, ganha 1 Fogo Fátuo (máx. capacidade de velas). Ao trocar vela, consome tudo para +2t e -3t de recarga em [Q] por fogo fátuo."

class Persona:
    def __init__(self, archetype_id="CARETAKER"):
        self.archetype_id = archetype_id
        self.cooldown = 0
        self.light_prayer_turns = 0
        self.purged_creatures = 0

        if archetype_id == "CARETAKER":
            self.name = "O Zelador"
            self.title = "Guardião das Brasas"
            self.passive_name = "Pavio Consagrado"
            self.passive_desc = "Ao reacender pilastra apagada, concede +2t extras de queima inicial."
            self.active_name = "Reserva de Emergência"
            self.active_desc = "[Q] Reabastece 1 vela no inventário sem ir ao altar (Recarga: 25t)."
            self.max_cooldown = 25
        elif archetype_id == "OCCULTIST":
            self.name = "O Ocultista"
            self.title = "Mestre dos Rituais"
            self.passive_name = "Ressonância Astral"
            self.passive_desc = "Recarga acelerada de artefatos (Cruz ativa com 2 velas, Lanterna 1t parado, Câmera +1 carga, Bolsa 65%)."
            self.active_name = "Prece da Luz"
            self.active_desc = "[Q] Consome 1 vela para repelir sombras e afastar a criatura (Recarga: 20t)."
            self.max_cooldown = 20
        elif archetype_id == "WANDERER":
            self.name = "O Andarilho"
            self.title = "Passos nas Trevas"
            self.passive_name = "Passo Leve"
            self.passive_desc = "40% de probabilidade de mover entre pilastras vizinhas da mesma coluna sem gastar turnos."
            self.active_name = "Sprint de Fuga"
            self.active_desc = "[Q] Teletransporta-se instantaneamente para o Altar Central com custo 0 de turnos (Recarga: 25t)."
            self.max_cooldown = 25
        elif archetype_id == "PALADIN":
            self.name = "Aprendiz de Paladino"
            self.title = "Espada da Luz"
            self.passive_name = "Vontade Inabalável"
            self.passive_desc = "Cada criatura expurgada eleva permanentemente os turnos mínimos de queima (+1t por expurgo)."
            self.active_name = "Julgamento Sagrado"
            self.active_desc = "[Q] Expurga permanentemente 1 criatura das sombras, reduzindo a ameaça e subindo o piso mínimo (Recarga: 30t)."
            self.max_cooldown = 30
        elif archetype_id == "MOONBORN":
            self.name = "Nascido da Lua"
            self.title = "Filho do Crepúsculo"
            self.passive_name = "Afinidade Lunar"
            self.passive_desc = "Sob penumbra (<= 3 velas acesas), ganha +2t de queima bônus em trocas e 50% de chance de movimento livre."
            self.active_name = "Eclipse Prateado"
            self.active_desc = "[Q] Sob penumbra (<= 3 velas acesas), congela o decaimento de TODAS as velas acesas por 2 rodadas (Recarga: 25t)."
            self.max_cooldown = 25

class CandleItem:
    def __init__(self, enchantment=None):
        self.enchantment = enchantment

class Artifact:
    def __init__(self, artifact_type, persona_id="CARETAKER"):
        self.type = artifact_type
        self.persona_id = persona_id

        if self.type == "CROSS":
            self.name = "Cruz de Prata"
            self.tag = "DEFESA & RESSURREIÇÃO"
            self.description = "Concede +1t bônus a velas trocadas. Se todas as 6 velas apagarem, explode em luz sagrada, afasta as sombras e reacende 2 pilastras automaticamente (+4t). Recarrega com 3 velas acesas (2 para Ocultista)."
            self.is_charged = True
            self.recharge_threshold = 2 if persona_id == "OCCULTIST" else 3
        elif self.type == "LANTERN":
            self.name = "Lampião Espectral"
            self.tag = "SUSTENTAÇÃO TÁTICA"
            self.description = "A chama da pilastra onde o jogador estiver não consome turnos de queima. Expande a área de visão."
            self.is_charged = True
            self.recharge_threshold = 0
        elif self.type == "CAMERA":
            self.name = "Câmera Retrô"
            self.tag = "FLASH DE SOBREVIVÊNCIA"
            self.description = "Possui cargas de flash. Permite mover-se e agir livremente na escuridão total (com 0 velas acesas), gastando 1 carga por ação para cegar as criaturas."
            init_charges = 7 if persona_id == "OCCULTIST" else 6
            self.charges = init_charges
            self.max_charges = init_charges
        elif self.type == "BAG":
            self.name = "Bolsa Verde Musgo"
            self.tag = "ALQUIMIA & ESPAÇO"
            self.description = "Expande para 4 velas. Encanta velas no altar por cor: Verde (Chama Maior +4t), Ciano (Ação Livre 0t) e Púrpura (Altar Adjacente +3t)."
            self.extra_capacity = 1
        elif self.type == "FLASHLIGHT":
            self.name = "Lanterna Moderna"
            self.tag = "FEIXE DE LONGO ALCANCE"
            self.description = "Possui 9 cargas de bateria. Dispara à distância sem gastar turnos. Ficar parado recupera +3 baterias. Velas com >=10t travam o decaimento por 3 rodadas."
            self.charges = 9
            self.max_charges = 9
            self.selected_power = 3

    def trigger_cross(self):
        if self.type == "CROSS" and self.is_charged:
            self.is_charged = False
            return True
        return False

    def check_cross_recharge(self, active_candles):
        if self.type == "CROSS" and not self.is_charged:
            if active_candles >= self.recharge_threshold:
                self.is_charged = True
                return True
        return False

    def use_camera_charge(self):
        if self.type == "CAMERA" and self.charges > 0:
            self.charges -= 1
            return True
        return False

    def use_flashlight_charges(self, amount):
        if self.type == "FLASHLIGHT" and self.charges >= amount and amount > 0:
            self.charges -= amount
            return True
        return False

    def recharge_flashlight(self, amount=3):
        if self.type == "FLASHLIGHT" and self.charges < self.max_charges:
            recovered = min(self.max_charges - self.charges, amount)
            self.charges += recovered
            return recovered
        return 0

class Candle:
    def __init__(self, turns):
        self.max_turns = turns
        self.turns_left = turns
        self.freeze_turns_left = 0
        self.latent_embers = 0
        if self.turns_left >= 10:
            self.freeze_turns_left = 3
        self.is_lit = True

    def check_overcharge(self):
        if self.turns_left >= 10:
            self.freeze_turns_left = max(self.freeze_turns_left, 3)

    def tick(self, has_perpetual_fire=False):
        if self.is_lit:
            if self.freeze_turns_left > 0:
                self.freeze_turns_left -= 1
                return
            
            if self.turns_left > 0:
                self.turns_left -= 1
                if self.turns_left == 0:
                    if has_perpetual_fire and self.latent_embers == 0:
                        self.latent_embers = 1
                    else:
                        self.is_lit = False
            elif self.latent_embers > 0:
                self.latent_embers -= 1
                if self.latent_embers == 0:
                    self.is_lit = False
            else:
                self.is_lit = False

    def relight(self, turns):
        self.max_turns = turns
        self.turns_left = turns
        self.freeze_turns_left = 0
        self.latent_embers = 0
        if self.turns_left >= 10:
            self.freeze_turns_left = 3
        self.is_lit = True

    @property
    def ratio(self):
        if self.max_turns <= 0:
            return 0.0
        return max(0.0, min(1.0, self.turns_left / self.max_turns))

    @property
    def state(self):
        if not self.is_lit or (self.turns_left == 0 and self.latent_embers == 0):
            return "EXTINGUISHED"
        if self.latent_embers > 0 or self.turns_left <= 2 or self.ratio <= 0.3:
            return "FAILING"
        if self.ratio <= 0.6:
            return "DIM"
        return "BRIGHT"

class Pillar:
    def __init__(self, pillar_id, position, initial_turns):
        self.id = pillar_id
        self.position = position
        self.candle = Candle(initial_turns)

    def replace_candle(self, turns):
        self.candle.relight(turns)

class Player:
    def __init__(self, artifact_type="CROSS", persona_id="CARETAKER", blessing_type="FIRE"):
        self.current_location = "CENTER"
        self.target_location = "CENTER"
        self.stationary_turns = 0
        self.has_replaced_at_current_pillar = False
        self.pos_x = float(CENTER_POSITION[0])
        self.pos_y = float(CENTER_POSITION[1])
        self.persona = Persona(persona_id)
        self.artifact = Artifact(artifact_type, persona_id)
        self.blessing = Blessing(blessing_type)
        
        cap = INVENTORY_CAPACITY_BASE
        if self.artifact.type == "BAG":
            cap += 1
        self.max_inventory = cap
        self.inventory = []
        self.restock()

    def restock(self):
        added = 0
        chance = 0.65 if self.persona.archetype_id == "OCCULTIST" else 0.50
        while len(self.inventory) < self.max_inventory:
            enchant = None
            if self.blessing.type == "ABUNDANCE" and random.random() < 0.40:
                enchant = "GOLDEN"
            elif self.artifact.type == "BAG" and random.random() < chance:
                enchant = random.choice(["GREATER_FLAME", "FREE_ACTION", "ADJACENT"])
            self.inventory.append(CandleItem(enchant))
            added += 1
        return added

    def pop_candle(self):
        if len(self.inventory) > 0:
            return self.inventory.pop(0)
        return None

class Creature:
    def __init__(self):
        self.proximity = 0.0
        self.target_proximity = 0.0
        self.pulse = 0.0
        self.visible = False

    def update_target(self, extinguished_count, total_pillars=6, purged_count=0, is_stealth=False):
        effective_ext = max(0, extinguished_count - purged_count)
        if effective_ext == 0:
            self.target_proximity = 0.0
            self.visible = False
        else:
            self.visible = True
            rate = 0.65 if is_stealth else 1.0
            self.target_proximity = (effective_ext / total_pillars) * rate

    def update(self, dt):
        self.pulse += dt * 2.0
        self.proximity += (self.target_proximity - self.proximity) * min(1.0, dt * 3.0)
