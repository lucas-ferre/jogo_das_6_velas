import sys
import pygame
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    PILLAR_POSITIONS,
    CENTER_POSITION,
    STATE_MENU,
    STATE_PERSONA_SELECT,
    STATE_ARTIFACT_SELECT,
    STATE_BLESSING_SELECT,
    STATE_MODIFIER_SELECT,
    STATE_RITUAL_SUMMARY,
    STATE_UPGRADES,
    STATE_SETTINGS,
    STATE_PLAYING,
    STATE_GAME_OVER,
    PERSONA_CARETAKER,
    PERSONA_OCCULTIST,
    PERSONA_WANDERER,
    PERSONA_PALADIN,
    PERSONA_MOONBORN,
    BLESSING_FIRE,
    BLESSING_STEALTH,
    BLESSING_ABUNDANCE,
    BLESSING_SYNCHRONY,
    BLESSING_ADRENALINE,
    BLESSING_VIGOROUS_BREATH,
    BLESSING_THERMAL_BOND,
    BLESSING_WILL_O_WISP,
    BLESSING_SECOND_BREATH,
    WEATHER_CALM,
    WEATHER_THUNDERSTORM,
    WEATHER_BLOOD_RAIN,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_ENDLESS
)
from game_engine import GameEngine
from renderer import Renderer
from sound_manager import SoundManager

def get_clicked_pillar_or_altar(mouse_pos):
    mx, my = mouse_pos
    cx, cy = CENTER_POSITION
    if (mx - cx) ** 2 + (my - cy) ** 2 <= 40 ** 2:
        return "CENTER"

    for p_id, (px, py) in PILLAR_POSITIONS.items():
        if (mx - px) ** 2 + (my - py) ** 2 <= 35 ** 2:
            return str(p_id)

    return None

def main():
    pygame.init()
    pygame.font.init()
    
    is_fullscreen = False
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
    pygame.display.set_caption("O Ritual das 6 Velas")
    clock = pygame.time.Clock()

    sound_mgr = SoundManager()
    selected_artifact = "CROSS"
    current_persona = PERSONA_CARETAKER
    selected_blessing = BLESSING_FIRE
    selected_weather = WEATHER_CALM
    has_eclipse = False
    current_difficulty = DIFFICULTY_NORMAL
    current_state = STATE_MENU
    
    engine = GameEngine(selected_artifact, current_persona, current_difficulty, selected_blessing, selected_weather, has_eclipse)
    renderer = Renderer(screen)

    last_hovered_element = None

    def toggle_screen_mode():
        nonlocal is_fullscreen, screen, renderer
        is_fullscreen = not is_fullscreen
        flags = pygame.SCALED | (pygame.FULLSCREEN if is_fullscreen else 0)
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        renderer.screen = screen

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        current_hover = None
        if current_state == STATE_MENU:
            btn_w, btn_h = 320, 50
            btn_x = WINDOW_WIDTH // 2 - btn_w // 2
            if pygame.Rect(btn_x, 242, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "menu_start"
            elif pygame.Rect(btn_x, 310, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "menu_upgrades"
            elif pygame.Rect(btn_x, 378, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "menu_settings"
            elif pygame.Rect(btn_x, 446, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "menu_exit"

        elif current_state == STATE_PERSONA_SELECT:
            card_w, card_h = 175, 135
            top_pers = [PERSONA_CARETAKER, PERSONA_OCCULTIST, PERSONA_WANDERER]
            for idx, p_id in enumerate(top_pers):
                if pygame.Rect(180 + idx * 205, 85, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"pers_top_{p_id}"
            bot_pers = [PERSONA_PALADIN, PERSONA_MOONBORN]
            for idx, p_id in enumerate(bot_pers):
                if pygame.Rect(285 + idx * 225, 235, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"pers_bot_{p_id}"
            if pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44).collidepoint(mouse_pos):
                current_hover = "pers_fwd"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36).collidepoint(mouse_pos):
                current_hover = "pers_back"

        elif current_state == STATE_ARTIFACT_SELECT:
            card_w, card_h = 175, 135
            for idx, a_type in enumerate(["CROSS", "LANTERN", "CAMERA"]):
                if pygame.Rect(180 + idx * 205, 85, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"art_top_{a_type}"
            for idx, a_type in enumerate(["BAG", "FLASHLIGHT"]):
                if pygame.Rect(285 + idx * 225, 235, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"art_bot_{a_type}"
            if pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44).collidepoint(mouse_pos):
                current_hover = "art_fwd"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36).collidepoint(mouse_pos):
                current_hover = "art_back"

        elif current_state == STATE_BLESSING_SELECT:
            card_w, card_h = 175, 135
            start_x = 112
            top_bless = [BLESSING_FIRE, BLESSING_STEALTH, BLESSING_ABUNDANCE, BLESSING_SYNCHRONY]
            for idx, b_id in enumerate(top_bless):
                if pygame.Rect(start_x + idx * 200, 85, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"bless_top_{b_id}"
            bot_bless = [BLESSING_ADRENALINE, BLESSING_VIGOROUS_BREATH, BLESSING_THERMAL_BOND, BLESSING_WILL_O_WISP]
            for idx, b_id in enumerate(bot_bless):
                if pygame.Rect(start_x + idx * 200, 235, card_w, card_h).collidepoint(mouse_pos):
                    current_hover = f"bless_bot_{b_id}"
            if pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44).collidepoint(mouse_pos):
                current_hover = "bless_start"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36).collidepoint(mouse_pos):
                current_hover = "bless_back"

        elif current_state == STATE_MODIFIER_SELECT:
            cards_y = 196
            col_w = 400
            c1_x = WINDOW_WIDTH // 2 - col_w - 15
            c2_x = WINDOW_WIDTH // 2 + 15
            card_h = 75
            card_gap = 8
            if pygame.Rect(c1_x, cards_y + 24, col_w, card_h).collidepoint(mouse_pos):
                current_hover = "mod_calm"
            elif pygame.Rect(c1_x, cards_y + 24 + card_h + card_gap, col_w, card_h).collidepoint(mouse_pos):
                current_hover = "mod_storm"
            elif pygame.Rect(c1_x, cards_y + 24 + (card_h + card_gap) * 2, col_w, card_h).collidepoint(mouse_pos):
                current_hover = "mod_blood"
            elif pygame.Rect(c2_x, cards_y + 24, col_w, card_h * 3 + card_gap * 2).collidepoint(mouse_pos):
                current_hover = "mod_eclipse"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44).collidepoint(mouse_pos):
                current_hover = "mod_fwd"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36).collidepoint(mouse_pos):
                current_hover = "mod_back"

        elif current_state == STATE_RITUAL_SUMMARY:
            back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 310, WINDOW_HEIGHT - 68, 290, 44)
            start_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT - 68, 290, 44)
            if back_btn.collidepoint(mouse_pos):
                current_hover = "summary_back"
            elif start_btn.collidepoint(mouse_pos):
                current_hover = "summary_start"

        elif current_state == STATE_UPGRADES:
            if pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 68, 280, 42).collidepoint(mouse_pos):
                current_hover = "upgrades_back"

        elif current_state == STATE_SETTINGS:
            panel_x = WINDOW_WIDTH // 2 - 360
            panel_y = 68
            if pygame.Rect(panel_x + 35, panel_y + 44, 280, 42).collidepoint(mouse_pos):
                current_hover = "set_screen"
            elif pygame.Rect(panel_x + 35, panel_y + 132, 230, 42).collidepoint(mouse_pos):
                current_hover = "set_mute"
            elif pygame.Rect(panel_x + 295, panel_y + 139, 32, 28).collidepoint(mouse_pos):
                current_hover = "set_vol_minus"
            elif pygame.Rect(panel_x + 638, panel_y + 139, 32, 28).collidepoint(mouse_pos):
                current_hover = "set_vol_plus"
            elif pygame.Rect(panel_x + 35, panel_y + 225, 152, 44).collidepoint(mouse_pos):
                current_hover = "set_diff_easy"
            elif pygame.Rect(panel_x + 35 + 166, panel_y + 225, 152, 44).collidepoint(mouse_pos):
                current_hover = "set_diff_norm"
            elif pygame.Rect(panel_x + 35 + 166 * 2, panel_y + 225, 152, 44).collidepoint(mouse_pos):
                current_hover = "set_diff_hard"
            elif pygame.Rect(panel_x + 35 + 166 * 3, panel_y + 225, 152, 44).collidepoint(mouse_pos):
                current_hover = "set_diff_endless"
            elif pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 65, 280, 42).collidepoint(mouse_pos):
                current_hover = "set_back"

        elif current_state == STATE_GAME_OVER:
            btn_w, btn_h = 280, 46
            if pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 - 10, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "gov_restart"
            elif pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 50, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "gov_change"
            elif pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 110, btn_w, btn_h).collidepoint(mouse_pos):
                current_hover = "gov_menu"

        if current_hover != last_hovered_element:
            if current_hover is not None:
                sound_mgr.play("menu_hover")
            last_hovered_element = current_hover

        prev_ext_count = engine.extinguished_count
        prev_game_over = engine.game_over
        prev_burst = engine.silver_burst
        prev_flash = engine.camera_flash
        prev_purge = engine.purge_burst
        prev_blood = getattr(engine, 'blood_burst', 0.0)
        prev_lightning = getattr(engine, 'lightning_flash', 0.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEMOTION:
                if current_state == STATE_PLAYING:
                    renderer.hovered_target = get_clicked_pillar_or_altar(event.pos)
                else:
                    renderer.hovered_target = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    def go_to_state(target, cb=None):
                        renderer.start_fade_transition(target, cb)

                    if current_state == STATE_MENU:
                        btn_w, btn_h = 320, 50
                        btn_x = WINDOW_WIDTH // 2 - btn_w // 2
                        start_rect = pygame.Rect(btn_x, 242, btn_w, btn_h)
                        upg_rect = pygame.Rect(btn_x, 310, btn_w, btn_h)
                        set_rect = pygame.Rect(btn_x, 378, btn_w, btn_h)
                        exit_rect = pygame.Rect(btn_x, 446, btn_w, btn_h)

                        if start_rect.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_PERSONA_SELECT)
                        elif upg_rect.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_UPGRADES)
                        elif set_rect.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_SETTINGS)
                        elif exit_rect.collidepoint(event.pos):
                            running = False

                    elif current_state == STATE_PERSONA_SELECT:
                        card_w, card_h = 175, 135
                        top_pers = [PERSONA_CARETAKER, PERSONA_OCCULTIST, PERSONA_WANDERER]
                        for idx, p_id in enumerate(top_pers):
                            c_rect = pygame.Rect(180 + idx * 205, 85, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                current_persona = p_id

                        bot_pers = [PERSONA_PALADIN, PERSONA_MOONBORN]
                        for idx, p_id in enumerate(bot_pers):
                            c_rect = pygame.Rect(285 + idx * 225, 235, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                current_persona = p_id

                        fwd_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

                        if fwd_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_ARTIFACT_SELECT)
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_MENU)

                    elif current_state == STATE_ARTIFACT_SELECT:
                        card_w, card_h = 175, 135
                        start_x_top = 180
                        top_y = 85
                        top_types = ["CROSS", "LANTERN", "CAMERA"]
                        for idx, a_type in enumerate(top_types):
                            c_rect = pygame.Rect(start_x_top + idx * (card_w + 30), top_y, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                selected_artifact = a_type

                        bot_types = ["BAG", "FLASHLIGHT"]
                        start_x_bot = 285
                        bot_y = 235
                        for idx, a_type in enumerate(bot_types):
                            c_rect = pygame.Rect(start_x_bot + idx * (card_w + 50), bot_y, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                selected_artifact = a_type

                        fwd_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

                        if fwd_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_BLESSING_SELECT)
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_PERSONA_SELECT)

                    elif current_state == STATE_BLESSING_SELECT:
                        card_w, card_h = 175, 135
                        start_x = 112
                        top_bless = [BLESSING_FIRE, BLESSING_STEALTH, BLESSING_ABUNDANCE, BLESSING_SYNCHRONY]
                        for idx, b_id in enumerate(top_bless):
                            c_rect = pygame.Rect(start_x + idx * 200, 85, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                selected_blessing = b_id

                        bot_bless = [BLESSING_ADRENALINE, BLESSING_VIGOROUS_BREATH, BLESSING_THERMAL_BOND, BLESSING_WILL_O_WISP]
                        for idx, b_id in enumerate(bot_bless):
                            c_rect = pygame.Rect(start_x + idx * 200, 235, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                sound_mgr.play("menu_move")
                                selected_blessing = b_id

                        start_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

                        if start_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_MODIFIER_SELECT)
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_ARTIFACT_SELECT)

                    elif current_state == STATE_MODIFIER_SELECT:
                        cards_y = 196
                        col_w = 400
                        c1_x = WINDOW_WIDTH // 2 - col_w - 15
                        c2_x = WINDOW_WIDTH // 2 + 15
                        card_h = 75
                        card_gap = 8
                        rect_calm = pygame.Rect(c1_x, cards_y + 24, col_w, card_h)
                        rect_storm = pygame.Rect(c1_x, cards_y + 24 + card_h + card_gap, col_w, card_h)
                        rect_blood = pygame.Rect(c1_x, cards_y + 24 + (card_h + card_gap) * 2, col_w, card_h)
                        rect_eclipse = pygame.Rect(c2_x, cards_y + 24, col_w, card_h * 3 + card_gap * 2)

                        fwd_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

                        if rect_calm.collidepoint(event.pos):
                            selected_weather = WEATHER_CALM
                            sound_mgr.play("menu_move")
                        elif rect_storm.collidepoint(event.pos):
                            selected_weather = WEATHER_THUNDERSTORM
                            sound_mgr.play("wind_gust")
                        elif rect_blood.collidepoint(event.pos):
                            selected_weather = WEATHER_BLOOD_RAIN
                            has_eclipse = True
                            sound_mgr.play("blood_strike")
                        elif rect_eclipse.collidepoint(event.pos):
                            if selected_weather == WEATHER_BLOOD_RAIN:
                                sound_mgr.play("screen_impact")
                            else:
                                has_eclipse = not has_eclipse
                                sound_mgr.play("menu_select")
                        elif fwd_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_RITUAL_SUMMARY)
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_BLESSING_SELECT)

                    elif current_state == STATE_RITUAL_SUMMARY:
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 310, WINDOW_HEIGHT - 68, 290, 44)
                        start_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT - 68, 290, 44)

                        if start_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_PLAYING, lambda: engine.reset(selected_artifact, current_persona, current_difficulty, selected_blessing, selected_weather, has_eclipse))
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_MODIFIER_SELECT)

                    elif current_state == STATE_UPGRADES:
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 68, 280, 42)
                        if back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_MENU)

                    elif current_state == STATE_SETTINGS:
                        panel_x = WINDOW_WIDTH // 2 - 360
                        panel_y = 68
                        screen_btn_rect = pygame.Rect(panel_x + 35, panel_y + 44, 280, 42)
                        mute_btn_rect = pygame.Rect(panel_x + 35, panel_y + 132, 230, 42)
                        v_minus_rect = pygame.Rect(panel_x + 295, panel_y + 139, 32, 28)
                        v_plus_rect = pygame.Rect(panel_x + 638, panel_y + 139, 32, 28)
                        d_easy_rect = pygame.Rect(panel_x + 35, panel_y + 225, 152, 44)
                        d_norm_rect = pygame.Rect(panel_x + 35 + 166, panel_y + 225, 152, 44)
                        d_hard_rect = pygame.Rect(panel_x + 35 + 166 * 2, panel_y + 225, 152, 44)
                        d_endless_rect = pygame.Rect(panel_x + 35 + 166 * 3, panel_y + 225, 152, 44)
                        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 65, 280, 42)

                        if screen_btn_rect.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            toggle_screen_mode()
                        elif mute_btn_rect.collidepoint(event.pos):
                            sound_mgr.toggle_mute()
                            sound_mgr.play("menu_move")
                        elif v_minus_rect.collidepoint(event.pos):
                            sound_mgr.set_volume(sound_mgr.volume - 0.1)
                            sound_mgr.play("menu_move")
                        elif v_plus_rect.collidepoint(event.pos):
                            sound_mgr.set_volume(sound_mgr.volume + 0.1)
                            sound_mgr.play("menu_move")
                        elif d_easy_rect.collidepoint(event.pos):
                            current_difficulty = DIFFICULTY_EASY
                            engine.difficulty = DIFFICULTY_EASY
                            sound_mgr.play("menu_select")
                        elif d_norm_rect.collidepoint(event.pos):
                            current_difficulty = DIFFICULTY_NORMAL
                            engine.difficulty = DIFFICULTY_NORMAL
                            sound_mgr.play("menu_select")
                        elif d_hard_rect.collidepoint(event.pos):
                            current_difficulty = DIFFICULTY_HARD
                            engine.difficulty = DIFFICULTY_HARD
                            sound_mgr.play("menu_select")
                        elif d_endless_rect.collidepoint(event.pos):
                            current_difficulty = DIFFICULTY_ENDLESS
                            engine.difficulty = DIFFICULTY_ENDLESS
                            sound_mgr.play("menu_select")
                        elif back_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_MENU)

                    elif current_state == STATE_PLAYING:
                        if engine.game_over:
                            current_state = STATE_GAME_OVER
                        else:
                            if engine.player.artifact.type == "FLASHLIGHT":
                                art_x = 30 + engine.player.max_inventory * 32 + 12
                                art_slot_rect = pygame.Rect(art_x, WINDOW_HEIGHT - 65, 155, 32)
                                p_minus_rect = pygame.Rect(art_slot_rect.x + 30, art_slot_rect.y + 6, 16, 20)
                                p_plus_rect = pygame.Rect(art_slot_rect.x + 85, art_slot_rect.y + 6, 16, 20)

                                if p_minus_rect.collidepoint(event.pos):
                                    sound_mgr.play("menu_move")
                                    engine.player.artifact.selected_power = max(1, engine.player.artifact.selected_power - 1)
                                    continue
                                elif p_plus_rect.collidepoint(event.pos):
                                    sound_mgr.play("menu_move")
                                    engine.player.artifact.selected_power = min(9, engine.player.artifact.selected_power + 1)
                                    continue

                            art_x = 30 + engine.player.max_inventory * 32 + 12
                            pers_x = art_x + 155 + 12
                            skill_rect = pygame.Rect(pers_x, WINDOW_HEIGHT - 65, 175, 32)
                            if skill_rect.collidepoint(event.pos):
                                if engine.use_persona_ability():
                                    sound_mgr.play("divine_cross")
                                continue

                            target = get_clicked_pillar_or_altar(event.pos)
                            if target is not None:
                                if engine.interact_with(target):
                                    sound_mgr.play("candle_light")
                                else:
                                    sound_mgr.play("menu_move")

                    elif current_state == STATE_GAME_OVER:
                        btn_w, btn_h = 280, 44 if engine.victory else 46
                        base_y = WINDOW_HEIGHT // 2 + 40 if engine.victory else WINDOW_HEIGHT // 2 - 10
                        gap_y = 55 if engine.victory else 60
                        restart_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, base_y, btn_w, btn_h)
                        change_art_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, base_y + gap_y, btn_w, btn_h)
                        menu_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, base_y + gap_y * 2, btn_w, btn_h)

                        if restart_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_select")
                            go_to_state(STATE_PLAYING, lambda: engine.reset(selected_artifact, current_persona, current_difficulty, selected_blessing))
                        elif change_art_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_PERSONA_SELECT)
                        elif menu_btn.collidepoint(event.pos):
                            sound_mgr.play("menu_move")
                            go_to_state(STATE_MENU)

                elif event.button == 3:
                    if current_state == STATE_PLAYING and not engine.game_over:
                        if engine.player.artifact.type == "FLASHLIGHT":
                            target = get_clicked_pillar_or_altar(event.pos)
                            if target is not None and target != "CENTER":
                                if engine.fire_flashlight_at(target):
                                    sound_mgr.play("beam")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_screen_mode()

                elif event.key == pygame.K_ESCAPE:
                    if current_state in (STATE_PERSONA_SELECT, STATE_ARTIFACT_SELECT, STATE_BLESSING_SELECT, STATE_UPGRADES, STATE_SETTINGS, STATE_GAME_OVER):
                        sound_mgr.play("menu_move")
                        current_state = STATE_MENU
                    elif current_state == STATE_PLAYING:
                        sound_mgr.play("menu_move")
                        current_state = STATE_MENU
                    elif current_state == STATE_MENU:
                        running = False
                        break

                elif current_state == STATE_MENU:
                    if event.key in (pygame.K_1, pygame.K_RETURN, pygame.K_SPACE):
                        sound_mgr.play("menu_select")
                        current_state = STATE_PERSONA_SELECT
                    elif event.key == pygame.K_2:
                        sound_mgr.play("menu_move")
                        current_state = STATE_UPGRADES
                    elif event.key == pygame.K_3:
                        sound_mgr.play("menu_move")
                        current_state = STATE_SETTINGS
                    elif event.key in (pygame.K_4, pygame.K_q):
                        running = False

                elif current_state == STATE_PERSONA_SELECT:
                    p_list = [PERSONA_CARETAKER, PERSONA_OCCULTIST, PERSONA_WANDERER, PERSONA_PALADIN, PERSONA_MOONBORN]
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                        sound_mgr.play("menu_move")
                        current_persona = p_list[event.key - pygame.K_1]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sound_mgr.play("menu_select")
                        current_state = STATE_ARTIFACT_SELECT

                elif current_state == STATE_ARTIFACT_SELECT:
                    order = ["CROSS", "LANTERN", "CAMERA", "BAG", "FLASHLIGHT"]
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                        sound_mgr.play("menu_move")
                        idx = event.key - pygame.K_1
                        selected_artifact = order[idx]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sound_mgr.play("menu_select")
                        current_state = STATE_BLESSING_SELECT

                elif current_state == STATE_BLESSING_SELECT:
                    b_list = [
                        BLESSING_FIRE,
                        BLESSING_STEALTH,
                        BLESSING_ABUNDANCE,
                        BLESSING_SYNCHRONY,
                        BLESSING_ADRENALINE,
                        BLESSING_VIGOROUS_BREATH,
                        BLESSING_THERMAL_BOND,
                        BLESSING_WILL_O_WISP
                    ]
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                        sound_mgr.play("menu_move")
                        idx = event.key - pygame.K_1
                        selected_blessing = b_list[idx]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sound_mgr.play("menu_select")
                        current_state = STATE_RITUAL_SUMMARY
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                        sound_mgr.play("menu_move")
                        current_state = STATE_ARTIFACT_SELECT

                elif current_state == STATE_RITUAL_SUMMARY:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sound_mgr.play("menu_select")
                        engine.reset(selected_artifact, current_persona, current_difficulty, selected_blessing)
                        current_state = STATE_PLAYING
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                        sound_mgr.play("menu_move")
                        current_state = STATE_BLESSING_SELECT

                elif current_state in (STATE_UPGRADES, STATE_SETTINGS):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_BACKSPACE):
                        sound_mgr.play("menu_move")
                        current_state = STATE_MENU

                elif current_state == STATE_PLAYING:
                    if engine.game_over:
                        current_state = STATE_GAME_OVER
                    else:
                        is_shift = bool(pygame.key.get_mods() & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL))

                        if event.key == pygame.K_q:
                            if engine.use_persona_ability():
                                sound_mgr.play("divine_cross")

                        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                            if engine.player.artifact.type == "FLASHLIGHT":
                                sound_mgr.play("menu_move")
                                engine.player.artifact.selected_power = max(1, engine.player.artifact.selected_power - 1)
                        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                            if engine.player.artifact.type == "FLASHLIGHT":
                                sound_mgr.play("menu_move")
                                engine.player.artifact.selected_power = min(9, engine.player.artifact.selected_power + 1)
                        
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
                            target_p = str(event.key - pygame.K_1)
                            if is_shift and engine.player.artifact.type == "FLASHLIGHT":
                                if engine.fire_flashlight_at(target_p):
                                    sound_mgr.play("beam")
                            else:
                                if engine.interact_with(target_p):
                                    sound_mgr.play("candle_light")
                                else:
                                    sound_mgr.play("menu_move")

                        elif event.key in (pygame.K_c, pygame.K_0):
                            if engine.interact_with("CENTER"):
                                sound_mgr.play("candle_light")
                            else:
                                sound_mgr.play("menu_move")
                        elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_r):
                            if engine.replace_candle_at_current():
                                sound_mgr.play("candle_light")
                            else:
                                sound_mgr.play("menu_move")
                        elif event.key == pygame.K_w:
                            engine.wait_turn()
                            sound_mgr.play("menu_move")
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if engine.player.current_location == "CENTER":
                                engine.interact_with("1")
                            elif engine.player.current_location in ("3", "4", "5"):
                                engine.interact_with("CENTER")
                            sound_mgr.play("candle_light")
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if engine.player.current_location == "CENTER":
                                engine.interact_with("4")
                            elif engine.player.current_location in ("0", "1", "2"):
                                engine.interact_with("CENTER")
                            sound_mgr.play("candle_light")
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            if engine.player.current_location in ("1", "2"):
                                engine.interact_with("0")
                            elif engine.player.current_location in ("4", "5"):
                                engine.interact_with("3")
                            sound_mgr.play("candle_light")
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if engine.player.current_location in ("0", "1"):
                                engine.interact_with("2")
                            elif engine.player.current_location in ("3", "4"):
                                engine.interact_with("5")
                            sound_mgr.play("candle_light")

                elif current_state == STATE_GAME_OVER:
                    if event.key in (pygame.K_SPACE, pygame.K_r, pygame.K_RETURN):
                        sound_mgr.play("menu_select")
                        engine.reset(selected_artifact, current_persona, current_difficulty, selected_blessing, selected_weather, has_eclipse)
                        current_state = STATE_PLAYING
                    elif event.key in (pygame.K_t, pygame.K_TAB):
                        sound_mgr.play("menu_move")
                        current_state = STATE_PERSONA_SELECT
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                        sound_mgr.play("menu_move")
                        current_state = STATE_MENU

        if current_state == STATE_PLAYING:
            if not engine.game_over:
                sound_mgr.start_weather_ambient(engine.weather_type)
            else:
                sound_mgr.stop_weather_ambient()

            if engine.extinguished_count > prev_ext_count:
                sound_mgr.play("candle_out")
                sound_mgr.play("screen_impact")
            if engine.silver_burst > 0.0 and prev_burst == 0.0:
                sound_mgr.play("divine_cross")
                sound_mgr.play("screen_impact")
            if engine.purge_burst > 0.0 and prev_purge == 0.0:
                sound_mgr.play("divine_cross")
                sound_mgr.play("screen_impact")
            if engine.camera_flash > 0.0 and prev_flash == 0.0:
                sound_mgr.play("flash")
            if getattr(engine, 'blood_burst', 0.0) > 0.5 and prev_blood <= 0.5:
                sound_mgr.play("blood_strike")
                sound_mgr.play("screen_impact")
            if getattr(engine, 'lightning_flash', 0.0) > 0.5 and prev_lightning <= 0.5:
                sound_mgr.play("thunder_strike")
                sound_mgr.play("screen_impact")
            if engine.game_over and not prev_game_over:
                sound_mgr.play("game_over")
                sound_mgr.play("screen_impact")
        else:
            sound_mgr.stop_weather_ambient()

        if current_state == STATE_MENU:
            renderer.update_animation(dt, engine)
            renderer.draw_menu(mouse_pos, current_difficulty)
        elif current_state == STATE_PERSONA_SELECT:
            renderer.update_animation(dt, engine)
            renderer.draw_persona_selection(current_persona, mouse_pos)
        elif current_state == STATE_ARTIFACT_SELECT:
            renderer.update_animation(dt, engine)
            renderer.draw_artifact_selection(selected_artifact, mouse_pos)
        elif current_state == STATE_BLESSING_SELECT:
            renderer.update_animation(dt, engine)
            renderer.draw_blessing_selection(selected_blessing, mouse_pos)
        elif current_state == STATE_MODIFIER_SELECT:
            renderer.update_animation(dt, engine)
            renderer.draw_modifier_selection(selected_weather, has_eclipse, current_difficulty, mouse_pos)
        elif current_state == STATE_RITUAL_SUMMARY:
            renderer.update_animation(dt, engine)
            renderer.draw_ritual_summary(current_persona, selected_artifact, selected_blessing, current_difficulty, selected_weather, has_eclipse, mouse_pos)
        elif current_state == STATE_UPGRADES:
            renderer.update_animation(dt, engine)
            renderer.draw_upgrades_screen(mouse_pos)
        elif current_state == STATE_SETTINGS:
            renderer.update_animation(dt, engine)
            renderer.draw_settings_screen(mouse_pos, is_fullscreen, sound_mgr.enabled, sound_mgr.volume, current_difficulty)
        elif current_state in (STATE_PLAYING, STATE_GAME_OVER):
            renderer.update_animation(dt, engine)
            renderer.render_gameplay(engine, mouse_pos)
            if engine.game_over and current_state != STATE_GAME_OVER:
                current_state = STATE_GAME_OVER

        # Update smooth screen transitions & overlay
        current_state, _ = renderer.update_fade(dt, current_state)
        renderer.draw_fade_overlay()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
