import random
from constants import (
    INITIAL_MIN_TURNS,
    INITIAL_MAX_TURNS,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    PILLAR_POSITIONS,
    CENTER_POSITION,
    get_target_victory_turns
)
from models import Pillar, Player, Creature, CandleItem

class GameEngine:
    def __init__(self, artifact_type="CROSS", persona_id="CARETAKER", difficulty=DIFFICULTY_NORMAL, blessing_type="FIRE"):
        self.silver_burst = 0.0
        self.camera_flash = 0.0
        self.beam_target = None
        self.beam_timer = 0.0
        self.difficulty = difficulty
        self.altar_disabled_turns = 0
        self.adrenaline_moves_left = 0
        self.adrenaline_ready = True
        self.thermal_bond_cooldown = 0
        self.will_o_wisps = 0
        self.target_victory_turns = get_target_victory_turns(persona_id, difficulty)
        self.victory_reason = ""
        self.reset(artifact_type, persona_id, difficulty, blessing_type)

    def reset(self, artifact_type="CROSS", persona_id="CARETAKER", difficulty=DIFFICULTY_NORMAL, blessing_type="FIRE"):
        self.turn = 1
        self.game_over = False
        self.victory = False
        self.victory_reason = ""
        self.target_victory_turns = get_target_victory_turns(persona_id, difficulty)
        self.silver_burst = 0.0
        self.camera_flash = 0.0
        self.purge_burst = 0.0
        self.screen_shake_trigger = 0.0
        self.beam_target = None
        self.beam_timer = 0.0
        self.difficulty = difficulty
        self.altar_disabled_turns = 0
        self.adrenaline_moves_left = 0
        self.adrenaline_ready = True
        self.thermal_bond_cooldown = 0
        self.will_o_wisps = 0
        self.player = Player(artifact_type, persona_id, blessing_type)
        self.creature = Creature()
        self.pillars = []
        
        for i in range(6):
            if self.difficulty == DIFFICULTY_EASY:
                initial_turns = random.randint(INITIAL_MIN_TURNS + 1, INITIAL_MAX_TURNS + 1)
            elif self.difficulty == DIFFICULTY_HARD:
                initial_turns = random.randint(2, max(3, INITIAL_MAX_TURNS - 2))
            else:
                initial_turns = random.randint(INITIAL_MIN_TURNS, INITIAL_MAX_TURNS)
            pillar = Pillar(i, PILLAR_POSITIONS[i], initial_turns)
            self.pillars.append(pillar)

        diff_names = {
            DIFFICULTY_EASY: "Suave",
            DIFFICULTY_NORMAL: "Padrão",
            DIFFICULTY_HARD: "Noite de Horror"
        }
        self.log_messages = [f"Ritual iniciado [{self.player.persona.name} | {self.player.blessing.name}]. Mantenha as velas acesas."]
        self.last_action_success = True

    @property
    def extinguished_count(self):
        return sum(1 for p in self.pillars if not p.candle.is_lit)

    @property
    def active_candles_count(self):
        return 6 - self.extinguished_count

    @property
    def current_min_turns(self):
        paladin_bonus = self.player.persona.purged_creatures if self.player.persona.archetype_id == "PALADIN" else 0
        if self.difficulty == DIFFICULTY_EASY:
            base = max(2, (INITIAL_MIN_TURNS + 1) - self.extinguished_count)
        elif self.difficulty == DIFFICULTY_HARD:
            base = 1
        else:
            base = max(1, INITIAL_MIN_TURNS - self.extinguished_count)
        return base + paladin_bonus

    @property
    def current_max_turns(self):
        min_val = self.current_min_turns
        paladin_bonus = self.player.persona.purged_creatures if self.player.persona.archetype_id == "PALADIN" else 0
        if self.difficulty == DIFFICULTY_EASY:
            base = max(min_val + 1, (INITIAL_MAX_TURNS + 1) - self.extinguished_count)
        elif self.difficulty == DIFFICULTY_HARD:
            base = max(min_val + 1, max(2, INITIAL_MAX_TURNS - self.extinguished_count * 2))
        else:
            base = max(min_val + 1, INITIAL_MAX_TURNS - self.extinguished_count)
        return base + paladin_bonus

    def add_log(self, text):
        self.log_messages.append(text)
        if len(self.log_messages) > 5:
            self.log_messages.pop(0)

    def update_timers(self, dt):
        if self.silver_burst > 0.0:
            self.silver_burst = max(0.0, self.silver_burst - dt * 1.2)
        if self.camera_flash > 0.0:
            self.camera_flash = max(0.0, self.camera_flash - dt * 2.5)
        if self.beam_timer > 0.0:
            self.beam_timer = max(0.0, self.beam_timer - dt * 2.0)
            if self.beam_timer <= 0.0:
                self.beam_target = None
        if self.purge_burst > 0.0:
            self.purge_burst = max(0.0, self.purge_burst - dt * 1.5)

    def check_stationary_recharge(self):
        if self.player.artifact.type == "FLASHLIGHT":
            req_turns = 1 if self.player.persona.archetype_id == "OCCULTIST" else 2
            if self.player.stationary_turns >= req_turns:
                recovered = self.player.artifact.recharge_flashlight(3)
                self.player.stationary_turns = 0
                if recovered > 0:
                    self.add_log(f"Descanso: A Lanterna recuperou +{recovered} baterias ({self.player.artifact.charges}/9)!")

    def advance_turn(self, consume_turn=True):
        if self.game_over:
            return

        if consume_turn:
            if self.player.persona.cooldown > 0:
                self.player.persona.cooldown -= 1
            if self.player.persona.light_prayer_turns > 0:
                self.player.persona.light_prayer_turns -= 1
            if self.altar_disabled_turns > 0:
                self.altar_disabled_turns -= 1
            if self.thermal_bond_cooldown > 0:
                self.thermal_bond_cooldown -= 1

        if self.player.blessing.type == "THERMAL_BOND" and self.thermal_bond_cooldown == 0:
            crit_pillars = [p for p in self.pillars if p.candle.is_lit and p.candle.turns_left == 1]
            if crit_pillars:
                target_p = crit_pillars[0]
                donor_candidates = [p for p in self.pillars if p.candle.is_lit and p.candle.turns_left > 5 and p.id != target_p.id]
                if donor_candidates:
                    donor_p = max(donor_candidates, key=lambda p: p.candle.turns_left)
                    donor_p.candle.turns_left -= 1
                    target_p.candle.turns_left += 2
                    target_p.candle.max_turns = max(target_p.candle.max_turns, target_p.candle.turns_left)
                    target_p.candle.check_overcharge()
                    self.thermal_bond_cooldown = 4
                    self.add_log(f"Vínculo Térmico: {self.get_pillar_label(target_p.id)} absorveu 1t de {self.get_pillar_label(donor_p.id)} (+2t ganhos, recarga 4t)!")

        frozen_pillar_id = None
        if self.player.artifact.type == "LANTERN" and self.player.current_location != "CENTER":
            frozen_pillar_id = int(self.player.current_location)

        has_perp = (self.player.blessing.type == "FIRE")
        just_extinguished = False
        for pillar in self.pillars:
            if pillar.candle.is_lit:
                if frozen_pillar_id is not None and pillar.id == frozen_pillar_id:
                    continue
                pillar.candle.tick(has_perpetual_fire=has_perp)
                if not pillar.candle.is_lit:
                    just_extinguished = True
                    self.add_log(f"A vela {self.get_pillar_label(pillar.id)} apagou!")
                    if self.player.blessing.type == "WILL_O_WISP":
                        max_wisps = self.player.max_inventory
                        if self.will_o_wisps < max_wisps:
                            self.will_o_wisps += 1
                            self.add_log(f"Fogo Fátuo: 1 chama espiritual absorvida ({self.will_o_wisps}/{max_wisps})!")

        if just_extinguished:
            self.screen_shake_trigger = max(self.screen_shake_trigger, 4.5)

        ext_count = self.extinguished_count
        purged = self.player.persona.purged_creatures
        is_stealth = (self.player.blessing.type == "STEALTH")

        if self.player.blessing.type in ("ADRENALINE", "SECOND_BREATH"):
            if self.adrenaline_ready and self.active_candles_count <= 2 and ext_count < len(self.pillars):
                self.adrenaline_ready = False
                self.adrenaline_moves_left = 2
                self.screen_shake_trigger = max(self.screen_shake_trigger, 6.0)
                self.add_log("Sobrecarga de Adrenalina ativada! Seus próximos 2 movimentos não gastam turnos!")
            elif not self.adrenaline_ready and self.active_candles_count >= 4:
                self.adrenaline_ready = True
                self.add_log("Sobrecarga de Adrenalina recarregada (Salão estabilizado)!")

        if ext_count == len(self.pillars):
            if self.player.artifact.type == "CROSS" and self.player.artifact.trigger_cross():
                self.silver_burst = 1.0
                self.screen_shake_trigger = 9.5
                self.creature.target_proximity = 0.2
                ext_pillars = [p for p in self.pillars if not p.candle.is_lit]
                revived = 0
                for p in ext_pillars[:2]:
                    p.replace_candle(4)
                    revived += 1
                self.add_log(f"A Cruz de Prata ressuscitou {revived} pilastra(s) com fogo sagrado!")
                if consume_turn:
                    self.turn += 1
            elif self.player.artifact.type == "CAMERA" and self.player.artifact.use_camera_charge():
                self.camera_flash = 1.0
                self.screen_shake_trigger = 5.5
                self.creature.target_proximity = 0.5
                self.add_log(f"Flash da Câmera disparado ({self.player.artifact.charges} restantes)! Ação permitida nas sombras.")
                if consume_turn:
                    self.turn += 1
            else:
                self.creature.update_target(ext_count, len(self.pillars), purged, is_stealth)
                self.game_over = True
                self.screen_shake_trigger = 8.0
                self.add_log("Todas as velas se apagaram. A criatura consumiu o salão.")
        else:
            self.creature.update_target(ext_count, len(self.pillars), purged, is_stealth)
            if self.player.persona.light_prayer_turns > 0:
                self.creature.target_proximity = max(0.0, self.creature.target_proximity - 0.4)

            if self.player.artifact.type == "CROSS":
                if self.player.artifact.check_cross_recharge(self.active_candles_count):
                    self.add_log("A Cruz de Prata recuperou sua carga sagrada!")
            if consume_turn:
                self.turn += 1

        if not self.game_over:
            if self.player.persona.purged_creatures >= 5:
                self.victory = True
                self.game_over = True
                self.victory_reason = "Todas as 5 criaturas das sombras foram expurgadas pelo Julgamento Sagrado!"
                self.add_log("VITÓRIA SAGRADA! O salão foi completamente purificado!")
            elif self.target_victory_turns is not None and self.turn >= self.target_victory_turns:
                self.victory = True
                self.game_over = True
                self.victory_reason = f"Você sobreviveu por {self.turn} rodadas e o Sol nasceu, banindo a escuridão!"
                self.add_log(f"RITUAL CONCLUÍDO! O Sol nasceu e iluminou todo o salão após {self.turn} rodadas!")

    def get_pillar_label(self, pillar_id):
        if pillar_id < 3:
            return f"E{pillar_id + 1}"
        return f"D{pillar_id - 2}"

    def move_to(self, destination):
        if self.game_over:
            return False

        if destination == self.player.current_location:
            return False

        prev_loc = self.player.current_location
        self.player.stationary_turns = 0
        self.player.has_replaced_at_current_pillar = False
        self.player.current_location = destination

        free_move = False
        if self.adrenaline_moves_left > 0:
            free_move = True
            self.adrenaline_moves_left -= 1
            self.add_log(f"Sobrecarga de Adrenalina: Movimento livre ({self.adrenaline_moves_left} restante(s))!")
        elif self.player.persona.archetype_id == "WANDERER" and prev_loc != "CENTER" and destination != "CENTER":
            p1 = int(prev_loc)
            p2 = int(destination)
            is_adj_col = (p1 in (0, 1, 2) and p2 in (0, 1, 2) and abs(p1 - p2) == 1) or (p1 in (3, 4, 5) and p2 in (3, 4, 5) and abs(p1 - p2) == 1)
            if is_adj_col and random.random() < 0.40:
                free_move = True
                self.add_log("Passo Leve: Movimento ágil sem gastar turnos (40% ativado)!")
        elif self.player.persona.archetype_id == "MOONBORN" and self.active_candles_count <= 3:
            if random.random() < 0.50:
                free_move = True
                self.add_log("Afinidade Lunar: Movimento furtivo nas sombras sem gastar turnos (50% ativado)!")

        if destination == "CENTER":
            self.player.target_location = "CENTER"
            self.player.pos_x = float(CENTER_POSITION[0])
            self.player.pos_y = float(CENTER_POSITION[1])
            if self.altar_disabled_turns > 0:
                self.add_log(f"Altar Central exausto ({self.altar_disabled_turns} turnos restantes).")
            else:
                prev_inv_count = len(self.player.inventory)
                added = self.player.restock()

                if self.player.blessing.type == "VIGOROUS_BREATH" and prev_inv_count == 0:
                    boosted = 0
                    for p in self.pillars:
                        if p.candle.is_lit:
                            p.candle.turns_left += 1
                            p.candle.max_turns = max(p.candle.max_turns, p.candle.turns_left)
                            p.candle.check_overcharge()
                            boosted += 1
                    if boosted > 0:
                        self.add_log(f"Fôlego Vigoroso: Retorno ao Altar com 0 velas revigorou {boosted} pilastra(s) (+1t em todas)!")

                if added > 0:
                    self.add_log(f"Você pegou {added} vela(s) no altar.")
                else:
                    self.add_log("Você voltou ao centro.")
        else:
            pillar_id = int(destination)
            target_pos = PILLAR_POSITIONS[pillar_id]
            self.player.target_location = str(pillar_id)
            self.player.pos_x = float(target_pos[0])
            self.player.pos_y = float(target_pos[1])
            self.add_log(f"Você foi até a Pilastra {self.get_pillar_label(pillar_id)}.")

        self.advance_turn(consume_turn=not free_move)
        return True

    def replace_candle_at_current(self):
        if self.game_over:
            return False

        if self.player.current_location == "CENTER":
            if self.altar_disabled_turns > 0:
                self.add_log(f"O Altar Central está exausto ({self.altar_disabled_turns} turnos restantes)!")
                return False
            prev_inv_count = len(self.player.inventory)
            added = self.player.restock()
            if self.player.blessing.type == "VIGOROUS_BREATH" and prev_inv_count == 0:
                boosted = 0
                for p in self.pillars:
                    if p.candle.is_lit:
                        p.candle.turns_left += 1
                        p.candle.max_turns = max(p.candle.max_turns, p.candle.turns_left)
                        p.candle.check_overcharge()
                        boosted += 1
                if boosted > 0:
                    self.add_log(f"Fôlego Vigoroso: Altar com 0 velas revigorou {boosted} pilastra(s) (+1t em todas)!")

            if added > 0:
                self.add_log(f"Você reabasteceu {added} vela(s) no altar.")
            else:
                self.add_log("Seu inventário já está cheio de velas.")
            self.player.stationary_turns += 1
            self.check_stationary_recharge()
            self.advance_turn()
            return True

        pillar_id = int(self.player.current_location)
        pillar = self.pillars[pillar_id]

        if self.player.has_replaced_at_current_pillar and pillar.candle.is_lit:
            self.add_log(f"A Pilastra {self.get_pillar_label(pillar_id)} já foi renovada nesta visita. Mova-se para outra.")
            return False

        candle_item = self.player.pop_candle()
        if candle_item is None:
            self.add_log("Sem velas no inventário! Vá até o altar no centro.")
            return False

        new_turns = random.randint(self.current_min_turns, self.current_max_turns)
        
        if self.player.artifact.type == "CROSS" and self.player.artifact.is_charged:
            new_turns += 1

        was_extinguished = not pillar.candle.is_lit

        if self.player.persona.archetype_id == "CARETAKER" and was_extinguished:
            new_turns += 2
            self.add_log("Pavio Consagrado: +2t bônus por reacender vela apagada!")
        elif self.player.persona.archetype_id == "MOONBORN" and self.active_candles_count <= 3:
            new_turns += 2
            self.add_log("Afinidade Lunar: +2t bônus por trocar vela sob a penumbra!")

        if self.player.blessing.type == "WILL_O_WISP" and self.will_o_wisps > 0:
            bonus_t = self.will_o_wisps * 2
            cd_red = self.will_o_wisps * 3
            new_turns += bonus_t
            if self.player.persona.cooldown > 0:
                self.player.persona.cooldown = max(0, self.player.persona.cooldown - cd_red)
            self.add_log(f"Fogo Fátuo: {self.will_o_wisps} chama(s) consumida(s) (+{bonus_t}t de queima, -{cd_red}t recarga [Q])!")
            self.will_o_wisps = 0

        is_free_action = False
        if candle_item.enchantment == "GOLDEN":
            new_turns *= 2
            self.add_log("Vela Dourada Consagrada (Duração dobrada)!")
        elif candle_item.enchantment == "GREATER_FLAME":
            new_turns += 4
            self.add_log("Vela com Chama Maior (+4t bônus)!")
        elif candle_item.enchantment == "ADJACENT":
            adj_id = self.get_adjacent_pillar_id(pillar_id)
            if adj_id is not None:
                adj_p = self.pillars[adj_id]
                adj_p.candle.turns_left += 3
                adj_p.candle.max_turns = max(adj_p.candle.max_turns, adj_p.candle.turns_left)
                adj_p.candle.is_lit = True
                adj_p.candle.check_overcharge()
                self.add_log(f"Encantamento: O fogo saltou para {self.get_pillar_label(adj_id)} (+3t)!")
        elif candle_item.enchantment == "FREE_ACTION":
            is_free_action = True
            self.add_log("Encantamento: Ação Livre (0 turnos consumidos)!")

        if self.player.blessing.type == "SYNCHRONY":
            mirrored_map = {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
            opp_id = mirrored_map.get(pillar_id)
            if opp_id is not None and self.pillars[opp_id].candle.is_lit:
                new_turns += 2
                opp_p = self.pillars[opp_id]
                opp_p.candle.turns_left += 2
                opp_p.candle.max_turns = max(opp_p.candle.max_turns, opp_p.candle.turns_left)
                opp_p.candle.check_overcharge()
                self.add_log(f"Sincronia Cósmica: Ressonância com {self.get_pillar_label(opp_id)} (+2t em ambas)!")

        pillar.replace_candle(new_turns)
        pillar.candle.check_overcharge()
        self.player.has_replaced_at_current_pillar = True

        if was_extinguished:
            self.add_log(f"Você reacendeu a Pilastra {self.get_pillar_label(pillar_id)} (+{new_turns}t).")
        else:
            self.add_log(f"Vela trocada na Pilastra {self.get_pillar_label(pillar_id)} (+{new_turns}t).")

        self.player.stationary_turns += 1
        self.check_stationary_recharge()

        self.advance_turn(consume_turn=not is_free_action)
        return True

    def get_adjacent_pillar_id(self, p_id):
        adj_map = {0: 1, 1: 0, 2: 1, 3: 4, 4: 3, 5: 4}
        return adj_map.get(p_id)

    def fire_flashlight_at(self, target_id):
        if self.game_over or self.player.artifact.type != "FLASHLIGHT":
            return False

        pillar_id = int(target_id)
        pillar = self.pillars[pillar_id]
        power = min(self.player.artifact.selected_power, self.player.artifact.charges)

        if power <= 0:
            self.add_log("Bateria da Lanterna esgotada! Fique parado para recarregar.")
            return False

        self.player.artifact.use_flashlight_charges(power)
        
        if pillar.candle.is_lit:
            pillar.candle.turns_left += power
            pillar.candle.max_turns = max(pillar.candle.max_turns, pillar.candle.turns_left)
        else:
            pillar.replace_candle(power)

        pillar.candle.check_overcharge()

        self.beam_target = pillar_id
        self.beam_timer = 1.0
        self.screen_shake_trigger = 3.5
        
        lock_msg = " [Decaimento travado por 2 rodadas!]" if pillar.candle.freeze_turns_left > 0 else ""
        self.add_log(f"Feixe da Lanterna: {self.get_pillar_label(pillar_id)} (+{power}t, total {pillar.candle.turns_left}t){lock_msg}.")
        return True

    def use_persona_ability(self):
        if self.game_over:
            return False

        p = self.player.persona
        if p.cooldown > 0:
            self.add_log(f"Habilidade em recarga ({p.cooldown} turnos restantes).")
            return False

        if p.archetype_id == "CARETAKER":
            if len(self.player.inventory) < self.player.max_inventory:
                self.player.inventory.append(CandleItem())
                p.cooldown = p.max_cooldown
                self.add_log("Reserva de Emergência: O Zelador pegou 1 vela de seu bolso!")
                return True
            else:
                self.add_log("Seu inventário de velas já está cheio!")
                return False

        elif p.archetype_id == "OCCULTIST":
            if len(self.player.inventory) > 0:
                self.player.pop_candle()
                self.creature.target_proximity = max(0.0, self.creature.target_proximity - 0.5)
                p.light_prayer_turns = 3
                p.cooldown = p.max_cooldown
                self.screen_shake_trigger = 6.0
                self.add_log("Prece da Luz: Vela sacrificada! As sombras foram repelidas por 3 turnos.")
                return True
            else:
                self.add_log("Você precisa de 1 vela para canalizar a Prece da Luz!")
                return False

        elif p.archetype_id == "WANDERER":
            if self.player.current_location != "CENTER":
                self.player.current_location = "CENTER"
                self.player.target_location = "CENTER"
                self.player.has_replaced_at_current_pillar = False
                self.player.pos_x = float(CENTER_POSITION[0])
                self.player.pos_y = float(CENTER_POSITION[1])
                added = self.player.restock() if self.altar_disabled_turns == 0 else 0
                p.cooldown = p.max_cooldown
                self.screen_shake_trigger = 4.0
                if self.altar_disabled_turns > 0:
                    self.add_log("Sprint de Fuga: Você correu direto ao Altar Central (Altar exausto)!")
                else:
                    self.add_log(f"Sprint de Fuga: Você correu direto ao Altar Central e pegou {added} vela(s)!")
                return True
            else:
                self.add_log("Você já está no Altar Central!")
                return False

        elif p.archetype_id == "PALADIN":
            p.purged_creatures += 1
            p.cooldown = p.max_cooldown
            self.purge_burst = 1.0
            self.screen_shake_trigger = 8.5
            self.creature.target_proximity = max(0.0, self.creature.target_proximity - 0.3)
            self.add_log(f"Julgamento Sagrado: 1 criatura expurgada permanentemente (+1t mínimo fixo, Total: {p.purged_creatures})!")
            if p.purged_creatures >= 5:
                self.victory = True
                self.game_over = True
                self.screen_shake_trigger = 10.0
                self.victory_reason = "Todas as 5 criaturas das sombras foram expurgadas pelo Julgamento Sagrado!"
                self.add_log("VITÓRIA SAGRADA! A 5ª criatura foi expurgada! O salão foi completamente purificado!")
            return True

        elif p.archetype_id == "MOONBORN":
            if self.active_candles_count <= 3:
                for pl in self.pillars:
                    if pl.candle.is_lit:
                        pl.candle.freeze_turns_left = max(pl.candle.freeze_turns_left, 2)
                p.cooldown = p.max_cooldown
                self.screen_shake_trigger = 6.0
                self.add_log("Eclipse Prateado: O tempo de queima de todas as velas foi congelado por 2 rodadas!")
                return True
            else:
                self.add_log("Eclipse Prateado exige penumbra (3 ou menos velas acesas) para ativar!")
                return False

        return False

    def interact_with(self, target):
        if self.game_over:
            return False

        if target == "CENTER":
            if self.player.current_location == "CENTER":
                return self.replace_candle_at_current()
            else:
                return self.move_to("CENTER")
        else:
            pillar_id = int(target)
            if self.player.current_location == str(pillar_id):
                return self.replace_candle_at_current()
            else:
                self.move_to(str(pillar_id))
                return True

    def wait_turn(self):
        if self.game_over:
            return False
        self.player.stationary_turns += 1
        self.check_stationary_recharge()
        self.add_log("Você esperou um turno...")
        self.advance_turn()
        return True
