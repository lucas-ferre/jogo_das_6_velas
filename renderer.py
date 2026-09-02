import math
import random
import pygame
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLOR_BG,
    COLOR_FLOOR,
    COLOR_FLOOR_GRID,
    COLOR_PILLAR,
    COLOR_PILLAR_BORDER,
    COLOR_PILLAR_SHADOW,
    COLOR_ALTAR,
    COLOR_ALTAR_GLOW,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_FLAME_CORE,
    COLOR_FLAME_INNER,
    COLOR_FLAME_OUTER,
    COLOR_SILVER_LIGHT,
    COLOR_SILVER_MID,
    COLOR_SILVER_DARK,
    COLOR_SILVER_GLOW,
    COLOR_LANTERN_BRASS,
    COLOR_LANTERN_FLAME,
    COLOR_LANTERN_CORE,
    COLOR_LANTERN_AURA,
    COLOR_MOSS_LIGHT,
    COLOR_MOSS_MID,
    COLOR_MOSS_DARK,
    COLOR_MOSS_RUNE,
    COLOR_ENCHANT_FLAME,
    COLOR_ENCHANT_FREE,
    COLOR_ENCHANT_ADJACENT,
    COLOR_ENCHANT_GOLD,
    COLOR_CAMERA_BODY,
    COLOR_CAMERA_CHROME,
    COLOR_CAMERA_LENS,
    COLOR_CAMERA_FLASH,
    COLOR_MODERN_BODY,
    COLOR_MODERN_BEZEL,
    COLOR_BATTERY_BAR,
    COLOR_CREATURE_EYES,
    COLOR_UI_PANEL,
    COLOR_UI_PANEL_HOVER,
    COLOR_UI_BORDER,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_AMBER,
    COLOR_PALADIN_GOLD,
    COLOR_MOONBORN_SILVER,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_ENDLESS,
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
    PILLAR_POSITIONS,
    CENTER_POSITION,
    get_target_victory_turns
)

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("georgia, segoeui, serif", 40, bold=True)
        self.font_large = pygame.font.SysFont("segoeui, arial, sans-serif", 26, bold=True)
        self.font_mid = pygame.font.SysFont("segoeui, arial, sans-serif", 17, bold=True)
        self.font_small = pygame.font.SysFont("consolas, segoeui, monospace", 13)
        self.font_tiny = pygame.font.SysFont("consolas, monospace", 11)
        self.time_elapsed = 0.0
        self.particles = []
        self.hovered_target = None
        self.player_visual_x = float(CENTER_POSITION[0])
        self.player_visual_y = float(CENTER_POSITION[1])

    def update_animation(self, dt, engine):
        self.time_elapsed += dt
        engine.update_timers(dt)
        engine.creature.update(dt)

        target_x, target_y = CENTER_POSITION
        if engine.player.current_location != "CENTER":
            p_id = int(engine.player.current_location)
            target_x, target_y = PILLAR_POSITIONS[p_id]

        dx = target_x - self.player_visual_x
        dy = target_y - self.player_visual_y
        self.player_visual_x += dx * min(1.0, dt * 10.0)
        self.player_visual_y += dy * min(1.0, dt * 10.0)

        for pillar in engine.pillars:
            if pillar.candle.is_lit:
                px, py = pillar.position
                if random.random() < 0.35:
                    jitter = random.uniform(-4, 4)
                    speed_y = random.uniform(-25, -10)
                    life = random.uniform(0.4, 0.8)
                    self.particles.append({
                        "x": px + jitter,
                        "y": py - 28,
                        "vx": jitter * 0.5,
                        "vy": speed_y,
                        "life": life,
                        "max_life": life,
                        "size": random.uniform(2.0, 4.0),
                        "type": "FIRE"
                    })

        if engine.player.artifact.type == "LANTERN":
            if random.random() < 0.25:
                lx = self.player_visual_x + random.uniform(-10, 10)
                ly = self.player_visual_y + random.uniform(-10, 10)
                self.particles.append({
                    "x": lx,
                    "y": ly,
                    "vx": random.uniform(-6, 6),
                    "vy": random.uniform(-18, -8),
                    "life": 0.6,
                    "max_life": 0.6,
                    "size": random.uniform(2.0, 3.5),
                    "type": "CYAN"
                })

        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw_button(self, rect, text, is_hovered, icon=None, subtext=None, primary=False):
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_col = COLOR_UI_PANEL_HOVER if is_hovered else COLOR_UI_PANEL
        if primary and is_hovered:
            bg_col = (35, 55, 90, 245)

        border_col = COLOR_ACCENT_BLUE if is_hovered else COLOR_UI_BORDER
        pygame.draw.rect(surf, bg_col, (0, 0, rect.width, rect.height), border_radius=8)
        pygame.draw.rect(surf, border_col, (0, 0, rect.width, rect.height), 2 if is_hovered else 1, border_radius=8)
        self.screen.blit(surf, (rect.x, rect.y))

        text_col = (255, 255, 255) if is_hovered else COLOR_TEXT
        txt_surf = self.font_mid.render(text, True, text_col)
        
        if subtext:
            self.screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width()) // 2, rect.y + 8))
            sub_surf = self.font_tiny.render(subtext, True, COLOR_TEXT_MUTED)
            self.screen.blit(sub_surf, (rect.x + (rect.width - sub_surf.get_width()) // 2, rect.y + 28))
        else:
            self.screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width()) // 2, rect.y + (rect.height - txt_surf.get_height()) // 2))

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = []
        for word in words:
            if not word:
                continue
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def draw_wrapped_text(self, text, font, color, x, y, max_width, line_spacing=4, max_lines=None):
        lines = self.wrap_text(text, font, max_width)
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            if lines:
                while lines[-1] and font.size(lines[-1] + "...")[0] > max_width:
                    lines[-1] = lines[-1][:-1]
                lines[-1] += "..."
        cur_y = y
        line_height = font.get_height()
        for line in lines:
            surf = font.render(line, True, color)
            self.screen.blit(surf, (x, cur_y))
            cur_y += line_height + line_spacing
        return cur_y

    def draw_gothic_moon_window(self, cx, cy, difficulty=DIFFICULTY_NORMAL):
        t = self.time_elapsed
        win_w = 260
        win_h = 190
        win_rect = pygame.Rect(cx - win_w // 2, cy - win_h // 2, win_w, win_h)

        if difficulty == DIFFICULTY_EASY:
            sky_bg = (6, 16, 32)
            moon_body = (185, 228, 255)
            moon_crater = (135, 190, 235)
            moon_glow_rgb = (100, 190, 255)
            star_rgb = (190, 230, 255)
            beam_rgb = (100, 195, 255)
            cloud_color = (12, 28, 50, 130)
            cloud_inner = (10, 24, 44, 100)
            frame_col = (25, 45, 70)
        elif difficulty == DIFFICULTY_HARD:
            sky_bg = (24, 8, 12)
            moon_body = (245, 68, 68)
            moon_crater = (165, 25, 25)
            moon_glow_rgb = (235, 45, 45)
            star_rgb = (255, 175, 175)
            beam_rgb = (240, 45, 45)
            cloud_color = (40, 10, 15, 140)
            cloud_inner = (32, 8, 12, 110)
            frame_col = (55, 25, 30)
        else:
            sky_bg = (8, 14, 28)
            moon_body = (235, 242, 255)
            moon_crater = (195, 208, 230)
            moon_glow_rgb = (190, 220, 255)
            star_rgb = (210, 230, 255)
            beam_rgb = (180, 215, 255)
            cloud_color = (15, 24, 42, 130)
            cloud_inner = (15, 24, 42, 100)
            frame_col = (30, 42, 60)

        win_surf = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        pygame.draw.rect(win_surf, sky_bg, (0, int(win_w // 2), win_w, int(win_h - win_w // 2)), border_bottom_left_radius=4, border_bottom_right_radius=4)
        pygame.draw.circle(win_surf, sky_bg, (win_w // 2, int(win_w // 2)), win_w // 2)

        stars = [
            (35, 60, 0.4), (70, 35, 0.8), (110, 25, 0.5), (150, 40, 0.9), (210, 65, 0.3),
            (50, 110, 0.6), (90, 85, 0.7), (180, 100, 0.5), (225, 125, 0.8), (130, 140, 0.4)
        ]
        for sx, sy, spd in stars:
            s_alpha = int(120 + math.sin(t * 3.0 + sx * spd) * 90)
            pygame.draw.circle(win_surf, (star_rgb[0], star_rgb[1], star_rgb[2], s_alpha), (sx, sy), 1)

        moon_cx, moon_cy = int(win_w * 0.66), int(win_h * 0.42)
        moon_pulse = math.sin(t * 1.5) * 4
        moon_rad = int(24 + moon_pulse * 0.5)

        for r in range(moon_rad + 25, moon_rad, -4):
            m_alpha = int((1.0 - ((r - moon_rad) / 25.0)) * 65)
            pygame.draw.circle(win_surf, (moon_glow_rgb[0], moon_glow_rgb[1], moon_glow_rgb[2], m_alpha), (moon_cx, moon_cy), r)

        pygame.draw.circle(win_surf, moon_body, (moon_cx, moon_cy), moon_rad)
        pygame.draw.circle(win_surf, moon_crater, (moon_cx - 5, moon_cy - 4), 6)
        pygame.draw.circle(win_surf, moon_crater, (moon_cx + 7, moon_cy + 5), 4)
        pygame.draw.circle(win_surf, moon_crater, (moon_cx + 3, moon_cy - 8), 5)

        cloud_x = int((t * 14.0) % (win_w + 140)) - 70
        cloud_surf = pygame.Surface((120, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surf, cloud_color, (0, 0, 120, 24))
        pygame.draw.ellipse(cloud_surf, cloud_inner, (20, -5, 80, 20))
        win_surf.blit(cloud_surf, (cloud_x, moon_cy - 8))

        pygame.draw.line(win_surf, frame_col, (win_w // 2, 0), (win_w // 2, win_h), 3)
        pygame.draw.line(win_surf, frame_col, (0, int(win_h * 0.55)), (win_w, int(win_h * 0.55)), 3)
        pygame.draw.circle(win_surf, frame_col, (win_w // 2, int(win_w // 2)), int(win_w // 2), 4)
        pygame.draw.rect(win_surf, frame_col, (0, int(win_w // 2), win_w, int(win_h - win_w // 2)), 4)

        moonbeam = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        beam_pts = [
            (cx - 30, cy + win_h // 2 - 20),
            (cx + 50, cy + win_h // 2 - 20),
            (cx + 260, WINDOW_HEIGHT - 60),
            (cx - 200, WINDOW_HEIGHT - 60)
        ]
        b_alpha = 22 if difficulty == DIFFICULTY_HARD else (18 if difficulty == DIFFICULTY_EASY else 14)
        pygame.draw.polygon(moonbeam, (beam_rgb[0], beam_rgb[1], beam_rgb[2], b_alpha), beam_pts)
        self.screen.blit(moonbeam, (0, 0))

        self.screen.blit(win_surf, (win_rect.x, win_rect.y))

    def draw_silver_cross(self, surface, cx, cy, scale=1.0, is_charged=True):
        t = self.time_elapsed
        h = int(38 * scale)
        arm_w = int(32 * scale)
        thick = int(8 * scale)

        if is_charged:
            glow_rad = int(30 * scale)
            glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
            pulse = math.sin(t * 3.5) * 40
            alpha = int(90 + pulse)
            pygame.draw.circle(glow_surf, (COLOR_SILVER_GLOW[0], COLOR_SILVER_GLOW[1], COLOR_SILVER_GLOW[2], alpha), (glow_rad, glow_rad), glow_rad)
            surface.blit(glow_surf, (cx - glow_rad, cy - glow_rad))

        main_col = COLOR_SILVER_LIGHT if is_charged else COLOR_SILVER_DARK
        mid_col = COLOR_SILVER_MID if is_charged else (70, 80, 95)
        border_col = (40, 50, 65)

        v_rect = pygame.Rect(cx - thick // 2, cy - h // 2, thick, h)
        h_rect = pygame.Rect(cx - arm_w // 2, cy - h // 6, arm_w, thick)

        pygame.draw.rect(surface, border_col, v_rect.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surface, border_col, h_rect.inflate(2, 2), border_radius=2)

        pygame.draw.rect(surface, mid_col, v_rect, border_radius=2)
        pygame.draw.rect(surface, mid_col, h_rect, border_radius=2)

        inner_thick = max(2, int(thick * 0.45))
        iv_rect = pygame.Rect(cx - inner_thick // 2, cy - h // 2 + 2, inner_thick, h - 4)
        ih_rect = pygame.Rect(cx - arm_w // 2 + 2, cy - h // 6 + 1, arm_w - 4, inner_thick)
        pygame.draw.rect(surface, main_col, iv_rect)
        pygame.draw.rect(surface, main_col, ih_rect)

        gem_rad = max(2, int(4 * scale))
        gem_col = (140, 210, 255) if is_charged else (60, 75, 90)
        pygame.draw.circle(surface, border_col, (cx, cy - h // 6 + thick // 2), gem_rad + 1)
        pygame.draw.circle(surface, gem_col, (cx, cy - h // 6 + thick // 2), gem_rad)

    def draw_spectral_lantern(self, surface, cx, cy, scale=1.0, is_active=True):
        t = self.time_elapsed
        w = int(28 * scale)
        h = int(38 * scale)

        if is_active:
            glow_rad = int(32 * scale)
            glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
            pulse = math.sin(t * 4.0) * 35
            alpha = int(100 + pulse)
            pygame.draw.circle(glow_surf, (COLOR_LANTERN_AURA[0], COLOR_LANTERN_AURA[1], COLOR_LANTERN_AURA[2], alpha), (glow_rad, glow_rad), glow_rad)
            surface.blit(glow_surf, (cx - glow_rad, cy - glow_rad))

        ring_rad = max(3, int(6 * scale))
        pygame.draw.circle(surface, COLOR_LANTERN_BRASS, (cx, cy - h // 2 - ring_rad // 2), ring_rad, 2)

        roof_pts = [
            (cx, cy - h // 2),
            (cx + w // 2, cy - h // 4),
            (cx - w // 2, cy - h // 4)
        ]
        pygame.draw.polygon(surface, COLOR_LANTERN_BRASS, roof_pts)

        body_rect = pygame.Rect(cx - w // 2 + 2, cy - h // 4, w - 4, int(h * 0.55))
        pygame.draw.rect(surface, (15, 30, 48), body_rect)
        pygame.draw.rect(surface, COLOR_LANTERN_BRASS, body_rect, 2)

        if is_active:
            flame_y = cy + int(2 * scale)
            pygame.draw.circle(surface, COLOR_LANTERN_AURA, (cx, flame_y), int(7 * scale))
            pygame.draw.circle(surface, COLOR_LANTERN_FLAME, (cx, flame_y - 2), int(5 * scale))
            pygame.draw.circle(surface, COLOR_LANTERN_CORE, (cx, flame_y - 3), int(2 * scale))

        base_rect = pygame.Rect(cx - w // 2, cy + int(h * 0.3), w, int(h * 0.18))
        pygame.draw.rect(surface, COLOR_LANTERN_BRASS, base_rect, border_radius=2)

    def draw_retro_camera(self, surface, cx, cy, scale=1.0, charges=6):
        w = int(36 * scale)
        h = int(26 * scale)

        body_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        pygame.draw.rect(surface, COLOR_CAMERA_BODY, body_rect, border_radius=3)
        pygame.draw.rect(surface, COLOR_CAMERA_CHROME, body_rect, 2, border_radius=3)

        top_plate = pygame.Rect(cx - w // 2, cy - h // 2 - int(4 * scale), w, int(5 * scale))
        pygame.draw.rect(surface, COLOR_CAMERA_CHROME, top_plate, border_radius=2)

        lens_rad = int(9 * scale)
        pygame.draw.circle(surface, COLOR_CAMERA_CHROME, (cx, cy + 2), lens_rad + 2)
        pygame.draw.circle(surface, COLOR_CAMERA_LENS, (cx, cy + 2), lens_rad)
        pygame.draw.circle(surface, (150, 200, 255), (cx - 2, cy), int(3 * scale))

        flash_bulb = pygame.Rect(cx + w // 2 - int(10 * scale), cy - h // 2 - int(6 * scale), int(8 * scale), int(6 * scale))
        pygame.draw.rect(surface, COLOR_CAMERA_FLASH if charges > 0 else (60, 60, 70), flash_bulb, border_radius=1)

    def draw_moss_bag(self, surface, cx, cy, scale=1.0):
        t = self.time_elapsed
        w = int(32 * scale)
        h = int(34 * scale)

        pouch_pts = [
            (cx - w // 2, cy - h // 4),
            (cx + w // 2, cy - h // 4),
            (cx + w // 2 + int(3 * scale), cy + h // 3),
            (cx, cy + h // 2),
            (cx - w // 2 - int(3 * scale), cy + h // 3)
        ]
        pygame.draw.polygon(surface, COLOR_MOSS_DARK, pouch_pts)
        pygame.draw.polygon(surface, COLOR_MOSS_MID, [(p[0], p[1] - 2) for p in pouch_pts])
        pygame.draw.polygon(surface, (15, 45, 25), pouch_pts, 2)

        drawstring = pygame.Rect(cx - w // 3, cy - h // 3, int(w * 0.66), int(5 * scale))
        pygame.draw.rect(surface, (190, 160, 90), drawstring, border_radius=2)

        rune_pulse = math.sin(t * 3.0) * 35
        rune_alpha = max(100, min(255, int(180 + rune_pulse)))
        rune_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(rune_surf, (COLOR_MOSS_RUNE[0], COLOR_MOSS_RUNE[1], COLOR_MOSS_RUNE[2], rune_alpha), (10, 10), int(5 * scale), 1)
        pygame.draw.line(rune_surf, (COLOR_MOSS_RUNE[0], COLOR_MOSS_RUNE[1], COLOR_MOSS_RUNE[2], rune_alpha), (10, 5), (10, 15), 1)
        surface.blit(rune_surf, (cx - 10, cy - 6))

    def draw_modern_flashlight(self, surface, cx, cy, scale=1.0, charges=9):
        w = int(36 * scale)
        h = int(18 * scale)

        head_rect = pygame.Rect(cx + w // 4, cy - h // 2 - int(2 * scale), int(w * 0.35), h + int(4 * scale))
        pygame.draw.rect(surface, COLOR_MODERN_BODY, head_rect, border_radius=2)
        pygame.draw.rect(surface, COLOR_MODERN_BEZEL, head_rect, 2, border_radius=2)

        body_rect = pygame.Rect(cx - w // 2, cy - h // 2, int(w * 0.75), h)
        pygame.draw.rect(surface, (35, 42, 55), body_rect, border_radius=3)
        pygame.draw.rect(surface, (60, 75, 95), body_rect, 1, border_radius=3)

        if charges > 0:
            lens_x = cx + w // 2 + int(2 * scale)
            pygame.draw.line(surface, (120, 210, 255), (lens_x, cy - h // 2), (lens_x, cy + h // 2), 2)
            pygame.draw.circle(surface, (200, 240, 255), (lens_x, cy), int(3 * scale))

    def draw_persona_selection(self, selected_persona, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("ESCOLHA SEU ARQUÉTIPO DE PERSONA", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        sub = self.font_small.render("Cada arquétipo concede habilidades passivas e um poder ativo [Q] exclusivo.", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 54))

        personas = [
            (PERSONA_CARETAKER, "O Zelador", "GUARDIÃO DAS BRASAS", COLOR_ACCENT_AMBER),
            (PERSONA_OCCULTIST, "O Ocultista", "MESTRE DOS RITUAIS", COLOR_ACCENT_PURPLE),
            (PERSONA_WANDERER, "O Andarilho", "PASSOS NAS TREVAS", COLOR_ACCENT_BLUE),
            (PERSONA_PALADIN, "Aprendiz de Paladino", "ESPADA DA LUZ", COLOR_PALADIN_GOLD),
            (PERSONA_MOONBORN, "Nascido da Lua", "FILHO DO CREPÚSCULO", COLOR_MOONBORN_SILVER)
        ]

        card_w, card_h = 175, 135
        start_x_top = 180
        top_y = 85

        for idx, (p_id, p_name, p_tag, p_col) in enumerate(personas[:3]):
            cx = start_x_top + idx * (card_w + 30)
            c_rect = pygame.Rect(cx, top_y, card_w, card_h)
            self.draw_persona_card_preview(c_rect, p_id, p_name, p_tag, p_col, selected_persona == p_id, c_rect.collidepoint(mouse_pos))

        start_x_bot = 285
        bot_y = 235
        for idx, (p_id, p_name, p_tag, p_col) in enumerate(personas[3:]):
            cx = start_x_bot + idx * (card_w + 50)
            c_rect = pygame.Rect(cx, bot_y, card_w, card_h)
            self.draw_persona_card_preview(c_rect, p_id, p_name, p_tag, p_col, selected_persona == p_id, c_rect.collidepoint(mouse_pos))

        detail_rect = pygame.Rect(80, 390, WINDOW_WIDTH - 160, 185)
        d_surf = pygame.Surface((detail_rect.width, detail_rect.height), pygame.SRCALPHA)
        d_surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(d_surf, COLOR_UI_BORDER, (0, 0, detail_rect.width, detail_rect.height), 1, border_radius=10)
        self.screen.blit(d_surf, (detail_rect.x, detail_rect.y))

        p_name, p_title, p_pass, p_act, p_lore, p_col = self.get_persona_full_info(selected_persona)

        t_surf = self.font_mid.render(p_name, True, (255, 255, 255))
        tag_surf = self.font_tiny.render(f"[{p_title}]", True, p_col)
        self.screen.blit(t_surf, (detail_rect.x + 25, detail_rect.y + 12))
        self.screen.blit(tag_surf, (detail_rect.x + 35 + t_surf.get_width(), detail_rect.y + 14))

        self.draw_wrapped_text(p_lore, self.font_small, COLOR_TEXT_MUTED, detail_rect.x + 25, detail_rect.y + 36, max_width=detail_rect.width - 50, max_lines=1)

        pygame.draw.line(self.screen, COLOR_UI_BORDER, (detail_rect.x + 25, detail_rect.y + 56), (detail_rect.right - 25, detail_rect.y + 56), 1)

        pass_lbl = self.font_small.render("✦ HABILIDADE PASSIVA:", True, COLOR_ACCENT_GREEN)
        self.screen.blit(pass_lbl, (detail_rect.x + 25, detail_rect.y + 64))
        self.draw_wrapped_text(p_pass, self.font_small, COLOR_TEXT, detail_rect.x + 25, detail_rect.y + 82, max_width=detail_rect.width - 50, max_lines=2, line_spacing=2)

        act_lbl = self.font_small.render("✦ HABILIDADE ATIVA [Q]:", True, p_col)
        self.screen.blit(act_lbl, (detail_rect.x + 25, detail_rect.y + 122))
        self.draw_wrapped_text(p_act, self.font_small, COLOR_TEXT, detail_rect.x + 25, detail_rect.y + 140, max_width=detail_rect.width - 50, max_lines=2, line_spacing=2)

        fwd_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

        self.draw_button(fwd_btn, "AVANÇAR PARA ARTEFATOS", fwd_btn.collidepoint(mouse_pos), primary=True)
        self.draw_button(back_btn, "VOLTAR AO MENU", back_btn.collidepoint(mouse_pos))

    def draw_persona_card_preview(self, rect, p_id, p_name, p_tag, p_col, is_sel, is_hov):
        t = self.time_elapsed

        if is_sel:
            glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            glow_alpha = int(70 + 40 * math.sin(t * 5.0))
            pygame.draw.rect(glow_surf, (*p_col[:3], glow_alpha), (0, 0, rect.width + 10, rect.height + 10), 2, border_radius=12)
            self.screen.blit(glow_surf, (rect.x - 5, rect.y - 5))

        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_col = (30, 45, 70, 240) if is_sel else (COLOR_UI_PANEL_HOVER if is_hov else COLOR_UI_PANEL)
        border_col = p_col if is_sel else (COLOR_UI_BORDER if not is_hov else (90, 115, 150))
        border_thick = 3 if is_sel else (2 if is_hov else 1)

        pygame.draw.rect(surf, bg_col, (0, 0, rect.width, rect.height), border_radius=10)
        pygame.draw.rect(surf, border_col, (0, 0, rect.width, rect.height), border_thick, border_radius=10)
        self.screen.blit(surf, (rect.x, rect.y))

        cx = rect.x + rect.width // 2
        cy = rect.y + 38

        if p_id == PERSONA_CARETAKER:
            pulse = math.sin(t * 3.5) * 2.5
            pygame.draw.circle(self.screen, (245, 158, 11, int(35 + 15 * math.sin(t * 4.0))), (cx, cy), int(22 + pulse))
            swing = math.sin(t * 3.0) * 2.0
            bx = cx + swing
            pygame.draw.line(self.screen, (254, 240, 138), (cx, cy - 18), (int(bx), cy - 12), 2)
            pygame.draw.circle(self.screen, (254, 240, 138), (cx, cy - 18), 2)
            pygame.draw.rect(self.screen, COLOR_ACCENT_AMBER, (int(bx - 9), cy - 12, 18, 22), 2, border_radius=3)
            flame_h = 9 + math.sin(t * 12.0) * 2.0
            flame_pts = [(int(bx + math.sin(t * 10.0) * 1.5), cy - 1 + int(flame_h * 0.2) - flame_h), (int(bx + 4), cy + 4), (int(bx - 4), cy + 4)]
            pygame.draw.polygon(self.screen, COLOR_FLAME_OUTER, flame_pts)
            pygame.draw.polygon(self.screen, (255, 255, 200), [(int(p[0] * 0.6 + bx * 0.4), int(p[1] * 0.6 + (cy + 2) * 0.4)) for p in flame_pts])
            e1_x = int(cx + math.sin(t * 3.0) * 8)
            e1_y = int(cy + 6 - ((t * 16.0) % 24))
            e2_x = int(cx - 7 + math.cos(t * 4.0) * 6)
            e2_y = int(cy + 8 - ((t * 16.0 + 8) % 24))
            e3_x = int(cx + 7 + math.sin(t * 5.0) * 6)
            e3_y = int(cy + 10 - ((t * 16.0 + 16) % 24))
            pygame.draw.circle(self.screen, (255, 220, 100), (e1_x, e1_y), 2)
            pygame.draw.circle(self.screen, (255, 200, 80), (e2_x, e2_y), 2)
            pygame.draw.circle(self.screen, (255, 240, 140), (e3_x, e3_y), 2)

        elif p_id == PERSONA_OCCULTIST:
            ang_rot = t * 1.5
            r_ring = 18 + math.sin(t * 3.5) * 1.5
            pygame.draw.circle(self.screen, (168, 85, 247, int(35 + 15 * math.sin(t * 3.0))), (cx, cy), int(r_ring + 4))
            pygame.draw.circle(self.screen, COLOR_ACCENT_PURPLE, (cx, cy), int(r_ring), 1)
            for i in range(4):
                rn_ang = ang_rot + i * (math.pi / 2)
                rx = cx + math.cos(rn_ang) * r_ring
                ry = cy + math.sin(rn_ang) * r_ring
                pygame.draw.circle(self.screen, (216, 180, 254), (int(rx), int(ry)), 2)
            tri_ang = -t * 2.0
            tri_pts = []
            for i in range(3):
                cur_a = tri_ang + i * (math.pi * 2 / 3)
                tri_pts.append((int(cx + math.cos(cur_a) * 10), int(cy + math.sin(cur_a) * 10)))
            pygame.draw.polygon(self.screen, (192, 132, 252), tri_pts, 1)
            c_rad = 5 + math.sin(t * 6.0) * 1.5
            pygame.draw.circle(self.screen, (147, 51, 234), (cx, cy), int(c_rad + 2))
            pygame.draw.circle(self.screen, (243, 232, 255), (cx, cy), int(max(2, c_rad - 1)))
            o1_x = int(cx + math.cos(t * 3.2) * 13)
            o1_y = int(cy + math.sin(t * 3.2) * 6)
            o2_x = int(cx + math.cos(t * 3.2 + math.pi) * 13)
            o2_y = int(cy + math.sin(t * 3.2 + math.pi) * 6)
            pygame.draw.circle(self.screen, (232, 121, 249), (o1_x, o1_y), 3)
            pygame.draw.circle(self.screen, (232, 121, 249), (o2_x, o2_y), 3)

        elif p_id == PERSONA_WANDERER:
            pygame.draw.circle(self.screen, (59, 130, 246, int(35 + 15 * math.sin(t * 3.0))), (cx, cy), 22)
            echo_phase = (t * 2.0) % 1.0
            echo_dist = 4 + 8 * echo_phase
            echo_alpha = int(90 * (1.0 - echo_phase))
            echo_s = pygame.Surface((44, 44), pygame.SRCALPHA)
            e_pts = [(22 - 10, 22 + 4 + echo_dist), (22, 22 - 10 + echo_dist), (22 + 10, 22 + 4 + echo_dist)]
            pygame.draw.lines(echo_s, (59, 130, 246, echo_alpha), False, e_pts, 2)
            self.screen.blit(echo_s, (cx - 22, cy - 22))
            w_ang = t * 1.2
            for i in range(4):
                cur_a = w_ang + i * (math.pi / 2)
                p_len = 13 if i % 2 == 0 else 7
                px = cx + math.cos(cur_a) * p_len
                py = cy + math.sin(cur_a) * p_len
                pygame.draw.line(self.screen, (96, 165, 250), (cx, cy), (int(px), int(py)), 2)
            for i in range(3):
                p_ang = t * 4.0 + i * 2.1
                dist = 11 + math.sin(t * 2.0 + i) * 3.0
                wx = int(cx + math.cos(p_ang) * dist)
                wy = int(cy + math.sin(p_ang) * dist)
                pygame.draw.circle(self.screen, (191, 219, 254), (wx, wy), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 3)

        elif p_id == PERSONA_PALADIN:
            ray_ang = t * 0.7
            pygame.draw.circle(self.screen, (234, 179, 8, int(35 + 20 * math.sin(t * 4.0))), (cx, cy), 22)
            for i in range(4):
                cur_a = ray_ang + i * (math.pi / 2)
                r_len = 16 + math.sin(t * 6.0 + i * 1.5) * 4.0
                rx = cx + math.cos(cur_a) * r_len
                ry = cy + math.sin(cur_a) * r_len
                pygame.draw.line(self.screen, (254, 240, 138), (cx, cy), (int(rx), int(ry)), 2)
            halo_y = int(cy - 16 + math.sin(t * 3.0) * 2.0)
            halo_rect = pygame.Rect(cx - 9, halo_y - 3, 18, 6)
            pygame.draw.ellipse(self.screen, (253, 224, 71), halo_rect, 2)
            pygame.draw.line(self.screen, COLOR_PALADIN_GOLD, (cx, cy - 13), (cx, cy + 13), 3)
            pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - 12), (cx, cy + 8), 1)
            pygame.draw.line(self.screen, COLOR_PALADIN_GOLD, (cx - 7, cy - 3), (cx + 7, cy - 3), 3)
            pygame.draw.circle(self.screen, (254, 240, 138), (cx, cy + 14), 2)
            gleam_phase = (t * 1.4) % 1.0
            gleam_y = int(cy + 10 - 22 * gleam_phase)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, gleam_y), 3)

        elif p_id == PERSONA_MOONBORN:
            cor_r = 15 + math.sin(t * 4.0) * 2.0
            pygame.draw.circle(self.screen, (186, 230, 253, int(40 + 20 * math.sin(t * 3.0))), (cx, cy), int(cor_r + 4))
            pygame.draw.circle(self.screen, COLOR_MOONBORN_SILVER, (cx, cy), 12)
            shad_x = int(cx + 4 + math.sin(t * 2.5) * 1.5)
            shad_y = int(cy - 4 + math.cos(t * 2.5) * 1.5)
            pygame.draw.circle(self.screen, (15, 23, 42), (shad_x, shad_y), 10)
            for i in range(3):
                m_ang = t * 1.5 + i * (math.pi * 2 / 3)
                mx = int(cx + math.cos(m_ang) * 17)
                my = int(cy + math.sin(m_ang) * 8)
                if i == 0:
                    pygame.draw.circle(self.screen, (224, 242, 254), (mx, my), 3)
                elif i == 1:
                    pygame.draw.circle(self.screen, (186, 230, 253), (mx, my), 3)
                    pygame.draw.circle(self.screen, (15, 23, 42), (mx + 1, my - 1), 2)
                else:
                    pygame.draw.circle(self.screen, (125, 211, 252), (mx, my), 2)
            pygame.draw.circle(self.screen, (224, 242, 254), (cx - 15, cy - 14), 1)
            pygame.draw.circle(self.screen, (224, 242, 254), (cx + 15, cy + 14), 1)

        t_surf = self.font_small.render(p_name, True, (255, 255, 255) if is_sel else COLOR_TEXT)
        self.screen.blit(t_surf, (rect.x + (rect.width - t_surf.get_width()) // 2, rect.y + 76))

        tag_text = f"[{p_tag}]"
        if self.font_tiny.size(tag_text)[0] > rect.width - 10:
            tag_text = f"[{p_tag[:16]}...]"
        tag_surf = self.font_tiny.render(tag_text, True, p_col)
        self.screen.blit(tag_surf, (rect.x + (rect.width - tag_surf.get_width()) // 2, rect.y + 95))

        st_txt = "✓ ESCOLHIDO" if is_sel else "CLIQUE"
        st_surf = self.font_tiny.render(st_txt, True, p_col if is_sel else COLOR_TEXT_DIM)
        self.screen.blit(st_surf, (rect.x + (rect.width - st_surf.get_width()) // 2, rect.y + 114))

    def get_persona_full_info(self, p_id):
        if p_id == PERSONA_CARETAKER:
            return (
                "O Zelador",
                "Guardião das Brasas",
                "Pavio Consagrado: Ao reacender pilastra apagada, concede +2t extras de queima inicial.",
                "Reserva de Emergência: Reabastece 1 vela no inventário de imediato sem ir ao altar (Recarga: 25t).",
                "Especialista em manutenção equilibrada, conservação e resistência a colapsos repentinos.",
                COLOR_ACCENT_AMBER
            )
        elif p_id == PERSONA_OCCULTIST:
            return (
                "O Ocultista",
                "Mestre dos Rituais",
                "Ressonância Astral: Cruz recarrega com 2 velas, Lanterna 1t parado, Câmera +1 carga, Bolsa 65% encantamento.",
                "Prece da Luz: Consome 1 vela do inventário para afastar as sombras e repelir a criatura por 3t (Recarga: 20t).",
                "Canalizador de energias sagradas com alta afinidade a artefatos e controle da ameaça sombria.",
                COLOR_ACCENT_PURPLE
            )
        elif p_id == PERSONA_WANDERER:
            return (
                "O Andarilho",
                "Passos nas Trevas",
                "Passo Leve: 40% de probabilidade de mover entre pilastras vizinhas da mesma coluna sem gastar turnos.",
                "Sprint de Fuga: Teletransporta-se instantaneamente para o Altar Central com custo 0 de turnos (Recarga: 25t).",
                "Agilidade sobrenatural e travessia rápida do salão em momentos de perigo iminente.",
                COLOR_ACCENT_BLUE
            )
        elif p_id == PERSONA_PALADIN:
            return (
                "Aprendiz de Paladino",
                "Espada da Luz",
                "Vontade Inabalável: Cada criatura expurgada eleva permanentemente o piso de turnos mínimos das velas (+1t por expurgo).",
                "Julgamento Sagrado: Expurga permanentemente 1 criatura das sombras, reduzindo a ameaça e subindo o piso mínimo (Recarga: 30t).",
                "Guerreiro sagrado que purga as sombras do salão e fortalece a queima mínima das chamas.",
                COLOR_PALADIN_GOLD
            )
        else:
            return (
                "Nascido da Lua",
                "Filho do Crepúsculo",
                "Afinidade Lunar: Sob penumbra (<= 3 velas acesas), ganha +2t de queima bônus em trocas e 50% de movimento livre.",
                "Eclipse Prateado: Sob penumbra (<= 3 velas acesas), congela o tempo de queima de todas as velas por 2 rodadas (Recarga: 25t).",
                "Devoto das sombras lunares que extrai poder quando o salão está à beira da escuridão total.",
                COLOR_MOONBORN_SILVER
            )

    def draw_blessing_selection(self, selected_blessing, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("ESCOLHA SUA BÊNÇÃO DIVINA", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        sub = self.font_small.render("Selecione a graça mística que guiará sua estratégia e sobrevivência no ritual.", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 54))

        blessings = [
            (BLESSING_FIRE, "Fogo Perpétuo", "SOBREVIDA EM BRASAS", COLOR_FLAME_INNER),
            (BLESSING_STEALTH, "Passos Silenciosos", "CONTROLE DE AMEAÇA", COLOR_ACCENT_BLUE),
            (BLESSING_ABUNDANCE, "Abundância Ancestral", "VELAS DOURADAS", COLOR_ENCHANT_GOLD),
            (BLESSING_SYNCHRONY, "Sincronia Cósmica", "RESSONÂNCIA ESPELHO", COLOR_ACCENT_PURPLE),
            (BLESSING_ADRENALINE, "Sobrecarga de Adrenalina", "SURTO DE VELOCIDADE", COLOR_ACCENT_AMBER),
            (BLESSING_VIGOROUS_BREATH, "Fôlego Vigoroso", "PULSO DO ALTAR", COLOR_ACCENT_GREEN),
            (BLESSING_THERMAL_BOND, "Vínculo Térmico", "CALOR COMPARTILHADO", (255, 140, 100)),
            (BLESSING_WILL_O_WISP, "Fogo Fátuo", "CINZAS ESPIRITUAIS", (140, 220, 255))
        ]

        card_w, card_h = 175, 135
        start_x = 112
        top_y = 85
        bot_y = 235

        for idx, (b_id, b_name, b_tag, b_col) in enumerate(blessings[:4]):
            cx = start_x + idx * 200
            c_rect = pygame.Rect(cx, top_y, card_w, card_h)
            self.draw_blessing_card_preview(c_rect, b_id, b_name, b_tag, b_col, selected_blessing == b_id, c_rect.collidepoint(mouse_pos))

        for idx, (b_id, b_name, b_tag, b_col) in enumerate(blessings[4:]):
            cx = start_x + idx * 200
            c_rect = pygame.Rect(cx, bot_y, card_w, card_h)
            self.draw_blessing_card_preview(c_rect, b_id, b_name, b_tag, b_col, selected_blessing == b_id, c_rect.collidepoint(mouse_pos))

        detail_rect = pygame.Rect(80, 390, WINDOW_WIDTH - 160, 185)
        d_surf = pygame.Surface((detail_rect.width, detail_rect.height), pygame.SRCALPHA)
        d_surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(d_surf, COLOR_UI_BORDER, (0, 0, detail_rect.width, detail_rect.height), 1, border_radius=10)
        self.screen.blit(d_surf, (detail_rect.x, detail_rect.y))

        b_name, b_title, b_lines, b_col = self.get_blessing_full_info(selected_blessing)

        t_surf = self.font_mid.render(b_name, True, (255, 255, 255))
        tag_surf = self.font_tiny.render(f"[{b_title}]", True, b_col)
        self.screen.blit(t_surf, (detail_rect.x + 25, detail_rect.y + 14))
        self.screen.blit(tag_surf, (detail_rect.x + 35 + t_surf.get_width(), detail_rect.y + 16))

        pygame.draw.line(self.screen, COLOR_UI_BORDER, (detail_rect.x + 25, detail_rect.y + 44), (detail_rect.right - 25, detail_rect.y + 44), 1)

        dy = detail_rect.y + 54
        for line in b_lines:
            col = COLOR_TEXT if ("•" in line or "Efeito:" in line) else COLOR_TEXT_MUTED
            if "Penalidade:" in line or "Exausto:" in line or "Restrição" in line:
                col = COLOR_ACCENT_RED
            elif "Bônus:" in line or "Recarga:" in line or "Limite" in line:
                col = COLOR_ACCENT_GREEN
            dy = self.draw_wrapped_text(line, self.font_small, col, detail_rect.x + 25, dy, max_width=detail_rect.width - 50, line_spacing=2) + 3

        start_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

        self.draw_button(start_btn, "RESUMO DO RITUAL", start_btn.collidepoint(mouse_pos), primary=True)
        self.draw_button(back_btn, "VOLTAR AOS ARTEFATOS", back_btn.collidepoint(mouse_pos))

    def draw_ritual_summary(self, persona_id, artifact_type, blessing_type, difficulty, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("CONFIRMAÇÃO DO RITUAL SAGRADO", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 18))

        sub = self.font_small.render("Verifique a sua composição e o objetivo de sobrevivência antes de adentrar o salão", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 52))

        panel_rect = pygame.Rect(40, 80, 920, 525)
        surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(surf, COLOR_UI_BORDER, (0, 0, panel_rect.width, panel_rect.height), 1, border_radius=12)
        self.screen.blit(surf, (panel_rect.x, panel_rect.y))

        col_w = 280
        col_gap = 20
        col_y = panel_rect.y + 16

        # --- COLUNA 1: ARQUÉTIPO SELECIONADO ---
        c1_x = panel_rect.x + 20
        c1_box = pygame.Rect(c1_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c1_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c1_box, 1, border_radius=8)

        p_name, p_title, p_pass, p_act, p_lore, p_col = self.get_persona_full_info(persona_id)

        t1 = self.font_mid.render("1. ARQUÉTIPO", True, COLOR_TEXT)
        b1 = self.font_tiny.render(f"[{p_title}]", True, p_col)
        self.screen.blit(t1, (c1_x + 14, col_y + 12))
        self.screen.blit(b1, (c1_x + c1_box.width - b1.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c1_x + 14, col_y + 38), (c1_x + c1_box.width - 14, col_y + 38), 1)

        c_preview_rect = pygame.Rect(c1_x + (col_w - 170) // 2, col_y + 46, 170, 130)
        self.draw_persona_card_preview(c_preview_rect, persona_id, p_name, p_title, p_col, is_sel=True, is_hov=False)

        py = col_y + 186
        pass_lbl = self.font_tiny.render("✦ HABILIDADE PASSIVA:", True, COLOR_ACCENT_GREEN)
        self.screen.blit(pass_lbl, (c1_x + 14, py))
        py = self.draw_wrapped_text(p_pass, self.font_tiny, COLOR_TEXT, c1_x + 14, py + 16, max_width=col_w - 28, line_spacing=2) + 8

        act_lbl = self.font_tiny.render("✦ HABILIDADE ATIVA [Q]:", True, p_col)
        self.screen.blit(act_lbl, (c1_x + 14, py))
        py = self.draw_wrapped_text(p_act, self.font_tiny, COLOR_TEXT, c1_x + 14, py + 16, max_width=col_w - 28, line_spacing=2) + 8

        lore_lbl = self.font_tiny.render("✦ PERFIL DO INICIADO:", True, COLOR_TEXT_MUTED)
        self.screen.blit(lore_lbl, (c1_x + 14, py))
        self.draw_wrapped_text(p_lore, self.font_tiny, COLOR_TEXT_DIM, c1_x + 14, py + 16, max_width=col_w - 28, line_spacing=2)

        # --- COLUNA 2: EQUIPAMENTO & DÁDIVA ---
        c2_x = c1_x + col_w + col_gap
        c2_box = pygame.Rect(c2_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c2_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c2_box, 1, border_radius=8)

        t2 = self.font_mid.render("2. BUILD RITUAL", True, COLOR_TEXT)
        b2 = self.font_tiny.render("[RELÍQUIA & BÊNÇÃO]", True, COLOR_ACCENT_BLUE)
        self.screen.blit(t2, (c2_x + 14, col_y + 12))
        self.screen.blit(b2, (c2_x + c2_box.width - b2.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c2_x + 14, col_y + 38), (c2_x + c2_box.width - 14, col_y + 38), 1)

        a_name, a_tag, a_bullets, _ = self.get_artifact_full_info(artifact_type)
        art_box = pygame.Rect(c2_x + 12, col_y + 48, col_w - 24, 185)
        pygame.draw.rect(self.screen, (15, 22, 35), art_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, art_box, 1, border_radius=6)

        an_s = self.font_small.render(f"❖ {a_name}", True, (255, 255, 255))
        at_s = self.font_tiny.render(f"[{a_tag}]", True, COLOR_ACCENT_BLUE)
        self.screen.blit(an_s, (art_box.x + 10, art_box.y + 8))
        self.screen.blit(at_s, (art_box.x + 10, art_box.y + 26))

        ay = art_box.y + 44
        for b_line in a_bullets:
            ay = self.draw_wrapped_text(b_line, self.font_tiny, COLOR_TEXT_MUTED, art_box.x + 10, ay, max_width=art_box.width - 20, line_spacing=2) + 4

        b_name, b_tag, b_rules, b_col = self.get_blessing_full_info(blessing_type)
        bless_box = pygame.Rect(c2_x + 12, col_y + 245, col_w - 24, 195)
        pygame.draw.rect(self.screen, (15, 22, 35), bless_box, border_radius=6)
        pygame.draw.rect(self.screen, b_col, bless_box, 1, border_radius=6)

        bn_s = self.font_small.render(f"✧ {b_name}", True, (255, 255, 255))
        bt_s = self.font_tiny.render(f"[{b_tag}]", True, b_col)
        self.screen.blit(bn_s, (bless_box.x + 10, bless_box.y + 8))
        self.screen.blit(bt_s, (bless_box.x + 10, bless_box.y + 26))

        by = bless_box.y + 44
        for b_rule in b_rules:
            by = self.draw_wrapped_text(b_rule, self.font_tiny, COLOR_TEXT, bless_box.x + 10, by, max_width=bless_box.width - 20, line_spacing=2) + 4

        # --- COLUNA 3: CONDIÇÕES DE VITÓRIA ---
        c3_x = c2_x + col_w + col_gap
        c3_box = pygame.Rect(c3_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c3_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c3_box, 1, border_radius=8)

        t3 = self.font_mid.render("3. VITÓRIA & DESAFIO", True, COLOR_TEXT)
        b3 = self.font_tiny.render("[OBJETIVO]", True, COLOR_ENCHANT_GOLD)
        self.screen.blit(t3, (c3_x + 14, col_y + 12))
        self.screen.blit(b3, (c3_x + c3_box.width - b3.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c3_x + 14, col_y + 38), (c3_x + c3_box.width - 14, col_y + 38), 1)

        diff_names = {
            DIFFICULTY_EASY: ("SUAVE (Lua Azul)", COLOR_ACCENT_GREEN, "-10 rodadas de sobrevivência"),
            DIFFICULTY_NORMAL: ("PADRÃO (Lua Prateada)", COLOR_ACCENT_BLUE, "Duração de ritual padrão"),
            DIFFICULTY_HARD: ("NOITE DE HORROR (Lua Sangue)", COLOR_ACCENT_RED, "+15 rodadas de sobrevivência"),
            DIFFICULTY_ENDLESS: ("NOITE SEM FIM (Sobrevivência)", COLOR_ACCENT_PURPLE, "Sem limite de turnos • Modo Infinito")
        }
        d_title, d_col, d_mod = diff_names.get(difficulty, ("PADRÃO", COLOR_ACCENT_BLUE, "Padrão"))

        diff_box = pygame.Rect(c3_x + 12, col_y + 48, col_w - 24, 60)
        pygame.draw.rect(self.screen, (15, 22, 35), diff_box, border_radius=6)
        pygame.draw.rect(self.screen, d_col, diff_box, 1, border_radius=6)

        df_lbl = self.font_tiny.render("DIFICULDADE SELECIONADA:", True, COLOR_TEXT_MUTED)
        df_val = self.font_small.render(d_title, True, d_col)
        df_mod_s = self.font_tiny.render(f"• {d_mod}", True, COLOR_TEXT_MUTED)
        self.screen.blit(df_lbl, (diff_box.x + 10, diff_box.y + 6))
        self.screen.blit(df_val, (diff_box.x + 10, diff_box.y + 22))
        self.screen.blit(df_mod_s, (diff_box.x + 10, diff_box.y + 40))

        target_turns = get_target_victory_turns(persona_id, difficulty)
        goal_box = pygame.Rect(c3_x + 12, col_y + 118, col_w - 24, 115)
        pygame.draw.rect(self.screen, (32, 28, 18), goal_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_ENCHANT_GOLD if target_turns is not None else COLOR_ACCENT_PURPLE, goal_box, 2, border_radius=6)

        if target_turns is not None:
            g_title = self.font_tiny.render("✦ META PRINCIPAL DE VITÓRIA:", True, COLOR_ENCHANT_GOLD)
            g_val = self.font_large.render(f"{target_turns} RODADAS", True, (255, 255, 255))
            self.screen.blit(g_title, (goal_box.x + 10, goal_box.y + 8))
            self.screen.blit(g_val, (goal_box.x + 10, goal_box.y + 26))

            g_desc = f"Mantenha as chamas do salão acesas por {target_turns} turnos até a aurora nascer para selar a escuridão e vencer."
            self.draw_wrapped_text(g_desc, self.font_tiny, (254, 240, 138), goal_box.x + 10, goal_box.y + 62, max_width=goal_box.width - 20, line_spacing=2)
        else:
            g_title = self.font_tiny.render("✦ MODO DE SOBREVIVÊNCIA PURA:", True, COLOR_ACCENT_PURPLE)
            g_val = self.font_large.render("NOITE SEM FIM", True, (255, 255, 255))
            self.screen.blit(g_title, (goal_box.x + 10, goal_box.y + 8))
            self.screen.blit(g_val, (goal_box.x + 10, goal_box.y + 26))

            g_desc = "Não há limite de turnos e a aurora nunca chegará. Sobreviva o máximo de rodadas possível contra as criaturas da penumbra."
            self.draw_wrapped_text(g_desc, self.font_tiny, (216, 180, 254), goal_box.x + 10, goal_box.y + 62, max_width=goal_box.width - 20, line_spacing=2)

        gy = col_y + 245
        if persona_id == PERSONA_PALADIN:
            alt_box = pygame.Rect(c3_x + 12, gy, col_w - 24, 90)
            pygame.draw.rect(self.screen, (25, 30, 20), alt_box, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_PALADIN_GOLD, alt_box, 1, border_radius=6)
            a_lbl = self.font_tiny.render("✦ VITÓRIA SAGRADA ALTERNATIVA:", True, COLOR_PALADIN_GOLD)
            self.screen.blit(a_lbl, (alt_box.x + 10, alt_box.y + 6))
            a_desc = "Expurgue todas as 5 criaturas com o Julgamento Sagrado [Q] para banir as trevas e vencer instantaneamente a qualquer momento!"
            self.draw_wrapped_text(a_desc, self.font_tiny, COLOR_TEXT, alt_box.x + 10, alt_box.y + 24, max_width=alt_box.width - 20, line_spacing=2)
            gy += 100

        defeat_box = pygame.Rect(c3_x + 12, gy, col_w - 24, col_y + 445 - gy)
        pygame.draw.rect(self.screen, (20, 15, 20), defeat_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, defeat_box, 1, border_radius=6)
        def_lbl = self.font_tiny.render("✦ CONDIÇÃO DE DERROTA:", True, COLOR_ACCENT_RED)
        self.screen.blit(def_lbl, (defeat_box.x + 10, defeat_box.y + 6))
        def_desc = "Se as 6 velas apagarem ao mesmo tempo (sem Cruz ativa ou Flash da Câmera), o salão cairá no colapso e o ritual será perdido."
        self.draw_wrapped_text(def_desc, self.font_tiny, COLOR_TEXT_MUTED, defeat_box.x + 10, defeat_box.y + 24, max_width=defeat_box.width - 20, line_spacing=2)

        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 310, WINDOW_HEIGHT - 68, 290, 44)
        start_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT - 68, 290, 44)

        self.draw_button(back_btn, "REVISAR ESCOLHAS", back_btn.collidepoint(mouse_pos))
        self.draw_button(start_btn, "INICIAR RITUAL", start_btn.collidepoint(mouse_pos), primary=True)

    def draw_blessing_card_preview(self, rect, b_id, b_name, b_tag, b_col, is_sel, is_hov):
        t = self.time_elapsed

        if is_sel:
            glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            glow_alpha = int(70 + 40 * math.sin(t * 5.0))
            pygame.draw.rect(glow_surf, (*b_col[:3], glow_alpha), (0, 0, rect.width + 10, rect.height + 10), 2, border_radius=12)
            self.screen.blit(glow_surf, (rect.x - 5, rect.y - 5))

        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_col = (30, 45, 70, 240) if is_sel else (COLOR_UI_PANEL_HOVER if is_hov else COLOR_UI_PANEL)
        border_col = b_col if is_sel else (COLOR_UI_BORDER if not is_hov else (90, 115, 150))
        border_thick = 3 if is_sel else (2 if is_hov else 1)

        pygame.draw.rect(surf, bg_col, (0, 0, rect.width, rect.height), border_radius=10)
        pygame.draw.rect(surf, border_col, (0, 0, rect.width, rect.height), border_thick, border_radius=10)
        self.screen.blit(surf, (rect.x, rect.y))

        cx = rect.x + rect.width // 2
        cy = rect.y + 38

        if b_id == BLESSING_FIRE:
            flick = math.sin(t * 12.0) * 2.0
            pulse = math.sin(t * 6.0) * 2.0
            pygame.draw.circle(self.screen, (255, 120, 30, int(40 + 15 * math.sin(t * 4.0))), (cx, cy), int(20 + pulse))
            flame_h = 15 + flick
            flame_w = 7.5 + flick * 0.3
            flame_pts = [(cx + math.sin(t * 10.0) * 1.5, cy - flame_h), (cx + flame_w, cy + 4), (cx - flame_w, cy + 4)]
            pygame.draw.polygon(self.screen, COLOR_FLAME_OUTER, flame_pts)
            inner_pts = [(cx + math.sin(t * 10.0 + 1) * 1.0, cy - flame_h * 0.65), (cx + flame_w * 0.6, cy + 3), (cx - flame_w * 0.6, cy + 3)]
            pygame.draw.polygon(self.screen, COLOR_FLAME_INNER, inner_pts)
            pygame.draw.circle(self.screen, COLOR_FLAME_CORE, (cx, cy + 2), 3)
            emb_x = int(cx + math.cos(t * 4.0) * 13)
            emb_y = int(cy - 6 + math.sin(t * 4.0) * 6)
            pygame.draw.circle(self.screen, (255, 200, 80), (emb_x, emb_y), 2)
        elif b_id == BLESSING_STEALTH:
            r_pulse = 14 + math.sin(t * 3.5) * 2.0
            pygame.draw.circle(self.screen, (59, 130, 246, int(40 + 15 * math.sin(t * 3.0))), (cx, cy), int(20 + math.sin(t * 3.5) * 2))
            pygame.draw.circle(self.screen, COLOR_ACCENT_BLUE, (cx, cy), int(r_pulse), 2)
            orb1_x = int(cx + math.cos(t * 2.8) * 15)
            orb1_y = int(cy + math.sin(t * 2.8) * 8)
            orb2_x = int(cx + math.cos(t * 2.8 + math.pi) * 15)
            orb2_y = int(cy + math.sin(t * 2.8 + math.pi) * 8)
            pygame.draw.circle(self.screen, (147, 197, 253), (orb1_x, orb1_y), 3)
            pygame.draw.circle(self.screen, (147, 197, 253), (orb2_x, orb2_y), 3)
            pygame.draw.circle(self.screen, (191, 219, 254), (cx, cy), int(4 + math.sin(t * 4.0)))
        elif b_id == BLESSING_ABUNDANCE:
            gold_glow = 20 + math.sin(t * 5.0) * 2.5
            pygame.draw.circle(self.screen, (250, 204, 21, int(40 + 20 * math.sin(t * 4.0))), (cx, cy), int(gold_glow))
            pygame.draw.circle(self.screen, COLOR_ENCHANT_GOLD, (cx, cy), 13)
            pygame.draw.circle(self.screen, (255, 250, 210), (cx, cy), 6)
            ang = t * 1.8
            ray_len = 8 + math.sin(t * 6.0) * 2.0
            for i in range(4):
                cur_ang = ang + i * (math.pi / 2)
                rx = cx + math.cos(cur_ang) * ray_len
                ry = cy + math.sin(cur_ang) * ray_len
                pygame.draw.line(self.screen, (255, 255, 240), (cx, cy), (int(rx), int(ry)), 2)
        elif b_id == BLESSING_SYNCHRONY:
            offset = 6.5 + math.sin(t * 4.0) * 2.5
            pygame.draw.circle(self.screen, (168, 85, 247, int(40 + 15 * math.sin(t * 3.5))), (cx, cy), 20)
            pygame.draw.line(self.screen, (216, 180, 254), (int(cx - offset), cy), (int(cx + offset), cy), 2)
            pygame.draw.circle(self.screen, COLOR_ACCENT_PURPLE, (int(cx - offset), cy), 7, 2)
            pygame.draw.circle(self.screen, COLOR_ACCENT_PURPLE, (int(cx + offset), cy), 7, 2)
            pygame.draw.circle(self.screen, (243, 232, 255), (int(cx - offset), cy), 2)
            pygame.draw.circle(self.screen, (243, 232, 255), (int(cx + offset), cy), 2)
        elif b_id in (BLESSING_ADRENALINE, BLESSING_SECOND_BREATH):
            ad_wave = 12 + 10 * ((t * 1.8) % 1.0)
            ad_alpha = int(80 * (1.0 - ((t * 1.8) % 1.0)))
            wave_s = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(wave_s, (245, 158, 11, ad_alpha), (22, 22), int(ad_wave), 2)
            self.screen.blit(wave_s, (cx - 22, cy - 22))
            
            pygame.draw.circle(self.screen, (245, 158, 11, 45), (cx, cy), 18)
            vib = math.sin(t * 18.0) * 1.2
            pts = [
                (cx - 3 + vib, cy - 14),
                (cx + 8 + vib, cy - 2),
                (cx + 1 + vib, cy - 2),
                (cx + 5 + vib, cy + 14),
                (cx - 7 + vib, cy + 2),
                (cx - 1 + vib, cy + 2)
            ]
            pygame.draw.polygon(self.screen, COLOR_ACCENT_AMBER, pts)
            pygame.draw.polygon(self.screen, (254, 240, 138), [(int(p[0] * 0.7 + cx * 0.3), int(p[1] * 0.7 + cy * 0.3)) for p in pts])
        elif b_id == BLESSING_VIGOROUS_BREATH:
            w1 = 7 + 13 * ((t * 1.4) % 1.0)
            a1 = int(75 * (1.0 - ((t * 1.4) % 1.0)))
            ws1 = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(ws1, (34, 197, 94, a1), (22, 22), int(w1), 2)
            self.screen.blit(ws1, (cx - 22, cy - 22))
            
            w2 = 7 + 13 * ((t * 1.4 + 0.5) % 1.0)
            a2 = int(75 * (1.0 - ((t * 1.4 + 0.5) % 1.0)))
            ws2 = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(ws2, (34, 197, 94, a2), (22, 22), int(w2), 2)
            self.screen.blit(ws2, (cx - 22, cy - 22))
            
            core_r = 12 + math.sin(t * 4.0) * 1.5
            pygame.draw.circle(self.screen, (34, 197, 94, 50), (cx, cy), int(core_r + 4))
            pygame.draw.circle(self.screen, COLOR_ACCENT_GREEN, (cx, cy), int(core_r), 2)
            pygame.draw.circle(self.screen, (187, 247, 208), (cx, cy), 5)
        elif b_id == BLESSING_THERMAL_BOND:
            pygame.draw.circle(self.screen, (255, 140, 100, int(40 + 15 * math.sin(t * 4.0))), (cx, cy), 20)
            pygame.draw.line(self.screen, (255, 210, 140), (cx - 9, cy), (cx + 9, cy), 2)
            spark_phase = (t * 1.6) % 1.0
            spark_x = int(cx - 9 + 18 * spark_phase)
            spark_y = int(cy + math.sin(spark_phase * math.pi * 2) * 2.0)
            pygame.draw.circle(self.screen, (255, 255, 220), (spark_x, spark_y), 3)
            n1_r = 7 + math.sin(t * 5.0) * 1.0
            n2_r = 7 - math.sin(t * 5.0) * 1.0
            pygame.draw.circle(self.screen, (255, 90, 40), (cx - 9, cy), int(n1_r))
            pygame.draw.circle(self.screen, (255, 180, 80), (cx + 9, cy), int(n2_r))
            pygame.draw.circle(self.screen, (255, 240, 200), (cx - 9, cy), 2)
            pygame.draw.circle(self.screen, (255, 240, 200), (cx + 9, cy), 2)
        elif b_id == BLESSING_WILL_O_WISP:
            wisp_y = cy + math.sin(t * 3.5) * 3.0
            wisp_x = cx + math.cos(t * 2.5) * 2.0
            pygame.draw.circle(self.screen, (140, 220, 255, int(45 + 20 * math.sin(t * 3.0))), (int(wisp_x), int(wisp_y)), 18)
            pygame.draw.circle(self.screen, (100, 210, 255), (int(wisp_x), int(wisp_y)), 10)
            pygame.draw.circle(self.screen, (230, 250, 255), (int(wisp_x), int(wisp_y - 2)), 4)
            orb_ang = t * 3.8
            s1_x = int(wisp_x + math.cos(orb_ang) * 12)
            s1_y = int(wisp_y + math.sin(orb_ang) * 7)
            s2_x = int(wisp_x + math.cos(orb_ang + math.pi) * 12)
            s2_y = int(wisp_y + math.sin(orb_ang + math.pi) * 7)
            pygame.draw.circle(self.screen, (186, 230, 253), (s1_x, s1_y), 2)
            pygame.draw.circle(self.screen, (186, 230, 253), (s2_x, s2_y), 2)

        t_surf = self.font_small.render(b_name, True, (255, 255, 255) if is_sel else COLOR_TEXT)
        self.screen.blit(t_surf, (rect.x + (rect.width - t_surf.get_width()) // 2, rect.y + 76))

        tag_text = f"[{b_tag}]"
        if self.font_tiny.size(tag_text)[0] > rect.width - 10:
            tag_text = f"[{b_tag[:16]}...]"
        tag_surf = self.font_tiny.render(tag_text, True, b_col)
        self.screen.blit(tag_surf, (rect.x + (rect.width - tag_surf.get_width()) // 2, rect.y + 95))

        st_txt = "✓ ESCOLHIDO" if is_sel else "CLIQUE"
        st_surf = self.font_tiny.render(st_txt, True, b_col if is_sel else COLOR_TEXT_DIM)
        self.screen.blit(st_surf, (rect.x + (rect.width - st_surf.get_width()) // 2, rect.y + 114))

    def get_blessing_full_info(self, b_id):
        if b_id == BLESSING_FIRE:
            return (
                "Bênção do Fogo Perpétuo",
                "SOBREVIDA EM BRASAS",
                [
                    "• Brasa Latente: Velas que chegam a 0 turnos NÃO apagam de imediato.",
                    "• Efeito: Entram em estado de brasa por +1 rodada extra de sobrevida antes de extinguir.",
                    "• Ideal para: Sobreviventes de alta precisão que calculam rotas no limite do tempo."
                ],
                COLOR_FLAME_INNER
            )
        elif b_id == BLESSING_STEALTH:
            return (
                "Bênção dos Passos Silenciosos",
                "CONTROLE DE AMEAÇA",
                [
                    "• Furtividade Sagrada: Reduz a velocidade de avanço da criatura em 35%.",
                    "• Efeito: A escuridão e o cerco das sombras demoram mais para avançar nas rodadas críticas.",
                    "• Ideal para: Dificuldades elevadas (Padrão e Noite de Horror)."
                ],
                COLOR_ACCENT_BLUE
            )
        elif b_id == BLESSING_ABUNDANCE:
            return (
                "Bênção da Abundância Ancestral",
                "DÁDIVA DE VELAS DOURADAS",
                [
                    "• Velas Douradas: 40% de chance no Altar Central de forjar Velas Douradas Consagradas.",
                    "• Efeito: A Vela Dourada queima pelo DOBRO da duração normal da pilastra.",
                    "• Ideal para: Sinergia com O Zelador e Bolsa Verde Musgo."
                ],
                COLOR_ENCHANT_GOLD
            )
        elif b_id == BLESSING_SYNCHRONY:
            return (
                "Bênção da Sincronia Cósmica",
                "RESSONÂNCIA ESPELHADA",
                [
                    "• Ressonância de Lados: Ao renovar uma vela, verifica a pilastra oposta espelhada.",
                    "• Efeito: Se a pilastra oposta estiver acesa, AMBAS ganham +2 turnos de queima sincronizada.",
                    "• Ideal para: Rotas em zigue-zague cruzando o salão leste e oeste."
                ],
                COLOR_ACCENT_PURPLE
            )
        elif b_id in (BLESSING_ADRENALINE, "SECOND_BREATH"):
            return (
                "Sobrecarga de Adrenalina",
                "SURTO DE VELOCIDADE",
                [
                    "• Reflexo de Sobrevivência: Sob perigo crítico (2 ou menos velas acesas), ativa a Adrenalina.",
                    "• Efeito: Concede 2 movimentos imediatos sem custo de turnos para reposicionar ou trocar velas.",
                    "• Recarga: Reativa automaticamente assim que o salão for estabilizado com 4 ou mais velas."
                ],
                COLOR_ACCENT_AMBER
            )
        elif b_id == BLESSING_VIGOROUS_BREATH:
            return (
                "Fôlego Vigoroso",
                "PULSO DO ALTAR",
                [
                    "• Vigor Alquímico: Recompensa o ciclo completo de esgotamento e reposição.",
                    "• Efeito: Ao voltar ao Altar Central com 0 velas no inventário, concede +1t a TODAS as velas acesas.",
                    "• Ideal para: Gerenciamento ativo de inventário e rotas que esgotam as velas antes do retorno."
                ],
                COLOR_ACCENT_GREEN
            )
        elif b_id == BLESSING_THERMAL_BOND:
            return (
                "Vínculo Térmico",
                "CALOR COMPARTILHADO",
                [
                    "• Fluxo Vital: Conecta as chamas do salão para impedir que pilastras fracas se apaguem sozinhas.",
                    "• Efeito: Se uma vela atingir 1t, absorve 1t de uma vela com >5t e ganha +2t de sobrevida.",
                    "• Restrição Tática: Pode ser acionado no máximo 1 vez a cada 4 turnos."
                ],
                (255, 140, 100)
            )
        else:
            return (
                "Fogo Fátuo",
                "CINZAS ESPIRITUAIS",
                [
                    "• Cinzas Sagradas: Cada vela que se apagar no salão concede 1 carga de Fogo Fátuo espiritual.",
                    "• Limite de Carga: Limitado pela capacidade de velas do jogador (máx. 3 velas, ou 4 com Bolsa).",
                    "• Efeito: Ao trocar uma vela, consome tudo: +2t de queima e -3t de recarga no [Q] por carga!"
                ],
                (140, 220, 255)
            )

    def draw_menu(self, mouse_pos, difficulty=DIFFICULTY_NORMAL):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        t = self.time_elapsed
        self.draw_gothic_moon_window(WINDOW_WIDTH // 2, 115, difficulty=difficulty)

        title_y = 110 + math.sin(t * 1.8) * 3
        title_surf = self.font_title.render("O RITUAL DAS 6 VELAS", True, COLOR_TEXT)
        self.screen.blit(title_surf, (WINDOW_WIDTH // 2 - title_surf.get_width() // 2, int(title_y)))

        sub_surf = self.font_small.render("Sobreviva nas profundezas da escuridão", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (WINDOW_WIDTH // 2 - sub_surf.get_width() // 2, int(title_y) + 52))

        lx, rx = WINDOW_WIDTH // 2 - 360, WINDOW_WIDTH // 2 + 360
        flame_flick = math.sin(t * 10.0) * 3
        pygame.draw.rect(self.screen, COLOR_PILLAR, (lx - 12, int(title_y) + 12, 24, 55), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_PILLAR, (rx - 12, int(title_y) + 12, 24, 55), border_radius=4)
        pygame.draw.circle(self.screen, COLOR_FLAME_INNER, (lx, int(title_y) + 4), int(7 + flame_flick))
        pygame.draw.circle(self.screen, COLOR_FLAME_INNER, (rx, int(title_y) + 4), int(7 - flame_flick))

        btn_w, btn_h = 320, 50
        btn_x = WINDOW_WIDTH // 2 - btn_w // 2
        
        buttons = [
            ("start", pygame.Rect(btn_x, 242, btn_w, btn_h), "INICIAR JOGO", True),
            ("upgrades", pygame.Rect(btn_x, 310, btn_w, btn_h), "MELHORIAS", False),
            ("settings", pygame.Rect(btn_x, 378, btn_w, btn_h), "CONFIGURAÇÕES", False),
            ("exit", pygame.Rect(btn_x, 446, btn_w, btn_h), "SAIR", False)
        ]

        for b_id, b_rect, label, is_prim in buttons:
            is_hov = b_rect.collidepoint(mouse_pos)
            self.draw_button(b_rect, label, is_hov, primary=is_prim)

        diff_names = {
            DIFFICULTY_EASY: ("Dificuldade Atual: Suave (Lua Azul)", COLOR_ACCENT_BLUE),
            DIFFICULTY_NORMAL: ("Dificuldade Atual: Padrão (Lua Prateada)", (215, 225, 245)),
            DIFFICULTY_HARD: ("Dificuldade Atual: Noite de Horror (Lua de Sangue)", COLOR_ACCENT_RED)
        }
        d_text, d_col = diff_names.get(difficulty, ("Dificuldade: Padrão", COLOR_TEXT_MUTED))
        cred_surf = self.font_tiny.render(d_text, True, d_col)
        self.screen.blit(cred_surf, (WINDOW_WIDTH // 2 - cred_surf.get_width() // 2, WINDOW_HEIGHT - 45))

    def draw_artifact_selection(self, selected_type, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("ESCOLHA SEU ARTEFATO SAGRADO", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        subtitle = self.font_small.render("Selecione um artefato para apoiar sua sobrevivência durante o ritual.", True, COLOR_TEXT_MUTED)
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 54))

        artifacts = [
            ("CROSS", "Cruz de Prata", "DEFESA & RESSURREIÇÃO"),
            ("LANTERN", "Lampião Espectral", "SUSTENTAÇÃO TÁTICA"),
            ("CAMERA", "Câmera Retrô", "FLASH DE SOBREVIVÊNCIA"),
            ("BAG", "Bolsa Verde Musgo", "ALQUIMIA & ESPAÇO"),
            ("FLASHLIGHT", "Lanterna Moderna", "LONGO ALCANCE")
        ]

        card_w, card_h = 175, 135
        start_x_top = 180
        top_y = 85

        top_cards = artifacts[:3]
        for idx, (a_type, a_name, a_tag) in enumerate(top_cards):
            cx = start_x_top + idx * (card_w + 30)
            c_rect = pygame.Rect(cx, top_y, card_w, card_h)
            self.draw_artifact_card_preview(c_rect, a_type, a_name, a_tag, selected_type == a_type, c_rect.collidepoint(mouse_pos))

        bot_cards = artifacts[3:]
        start_x_bot = 285
        bot_y = 235
        for idx, (a_type, a_name, a_tag) in enumerate(bot_cards):
            cx = start_x_bot + idx * (card_w + 50)
            c_rect = pygame.Rect(cx, bot_y, card_w, card_h)
            self.draw_artifact_card_preview(c_rect, a_type, a_name, a_tag, selected_type == a_type, c_rect.collidepoint(mouse_pos))

        detail_rect = pygame.Rect(80, 390, WINDOW_WIDTH - 160, 185)
        d_surf = pygame.Surface((detail_rect.width, detail_rect.height), pygame.SRCALPHA)
        d_surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(d_surf, COLOR_UI_BORDER, (0, 0, detail_rect.width, detail_rect.height), 1, border_radius=10)
        self.screen.blit(d_surf, (detail_rect.x, detail_rect.y))

        sel_name, sel_tag, sel_desc, sel_stats = self.get_artifact_full_info(selected_type)
        
        t_surf = self.font_mid.render(sel_name, True, (255, 255, 255))
        tag_surf = self.font_tiny.render(f"[{sel_tag}]", True, COLOR_ACCENT_BLUE)
        self.screen.blit(t_surf, (detail_rect.x + 25, detail_rect.y + 14))
        self.screen.blit(tag_surf, (detail_rect.x + 35 + t_surf.get_width(), detail_rect.y + 16))

        pygame.draw.line(self.screen, COLOR_UI_BORDER, (detail_rect.x + 25, detail_rect.y + 40), (detail_rect.right - 25, detail_rect.y + 40), 1)

        dy = detail_rect.y + 48
        for line in sel_desc:
            col = COLOR_TEXT_MUTED
            if "Bênção:" in line or "Efeito:" in line or "Recarga:" in line or "Potência:" in line or "Capacidade:" in line or "Super Queima:" in line or "Recarga por Repouso:" in line:
                col = COLOR_TEXT
            elif "Verde" in line:
                col = COLOR_ENCHANT_FLAME
            elif "Ciano" in line:
                col = COLOR_ENCHANT_FREE
            elif "Púrpura" in line:
                col = COLOR_ENCHANT_ADJACENT

            dy = self.draw_wrapped_text(line, self.font_small, col, detail_rect.x + 25, dy, max_width=detail_rect.width - 50, line_spacing=2) + 2

        fwd_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 105, 320, 44)
        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT - 55, 320, 36)

        self.draw_button(fwd_btn, "AVANÇAR PARA BÊNÇÃOS", fwd_btn.collidepoint(mouse_pos), primary=True)
        self.draw_button(back_btn, "VOLTAR À PERSONA", back_btn.collidepoint(mouse_pos))

    def draw_artifact_card_preview(self, rect, a_type, a_name, a_tag, is_sel, is_hov):
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_col = (30, 45, 70, 240) if is_sel else (COLOR_UI_PANEL_HOVER if is_hov else COLOR_UI_PANEL)
        border_col = COLOR_ACCENT_BLUE if is_sel else (COLOR_UI_BORDER if not is_hov else (90, 115, 150))
        border_thick = 3 if is_sel else (2 if is_hov else 1)

        pygame.draw.rect(surf, bg_col, (0, 0, rect.width, rect.height), border_radius=10)
        pygame.draw.rect(surf, border_col, (0, 0, rect.width, rect.height), border_thick, border_radius=10)
        self.screen.blit(surf, (rect.x, rect.y))

        cx = rect.x + rect.width // 2
        cy = rect.y + 42

        if a_type == "CROSS":
            self.draw_silver_cross(self.screen, cx, cy, scale=0.95, is_charged=True)
        elif a_type == "LANTERN":
            self.draw_spectral_lantern(self.screen, cx, cy, scale=0.95, is_active=True)
        elif a_type == "CAMERA":
            self.draw_retro_camera(self.screen, cx, cy, scale=0.95, charges=6)
        elif a_type == "BAG":
            self.draw_moss_bag(self.screen, cx, cy, scale=0.95)
        elif a_type == "FLASHLIGHT":
            self.draw_modern_flashlight(self.screen, cx, cy, scale=0.95, charges=9)

        t_surf = self.font_small.render(a_name, True, (255, 255, 255) if is_sel else COLOR_TEXT)
        self.screen.blit(t_surf, (rect.x + (rect.width - t_surf.get_width()) // 2, rect.y + 76))

        tag_text = f"[{a_tag}]"
        if self.font_tiny.size(tag_text)[0] > rect.width - 10:
            tag_text = f"[{a_tag[:16]}...]"
        tag_surf = self.font_tiny.render(tag_text, True, COLOR_ACCENT_BLUE if is_sel else COLOR_TEXT_MUTED)
        self.screen.blit(tag_surf, (rect.x + (rect.width - tag_surf.get_width()) // 2, rect.y + 95))

        st_txt = "✓ ESCOLHIDO" if is_sel else "CLIQUE"
        st_surf = self.font_tiny.render(st_txt, True, COLOR_ACCENT_BLUE if is_sel else COLOR_TEXT_DIM)
        self.screen.blit(st_surf, (rect.x + (rect.width - st_surf.get_width()) // 2, rect.y + 114))

    def get_artifact_full_info(self, a_type):
        if a_type == "CROSS":
            return (
                "Cruz de Prata",
                "DEFESA & RESSURREIÇÃO",
                [
                    "• Bênção Radiante: Concede +1 turno bônus a todas as velas trocadas.",
                    "• Ressurreição Sagrada: Ao apagar as 6 velas, afasta sombras e reacende 2 pilastras (+4t).",
                    "• Recarga Sagrada: Recarrega automaticamente ao atingir 3 ou mais velas acesas."
                ],
                "Defesa Divina"
            )
        elif a_type == "LANTERN":
            return (
                "Lampião Espectral",
                "SUSTENTAÇÃO TÁTICA",
                [
                    "• Preservação da Chama: A pilastra onde o jogador estiver NÃO consome turnos de queima.",
                    "• Visão Expandida: Emite aura própria azul-celeste que ilumina o ambiente.",
                    "• Efeito Passivo: Ativo durante toda a partida sem gastar cargas."
                ],
                "Controle de Tempo"
            )
        elif a_type == "CAMERA":
            return (
                "Câmera Fotográfica Retrô",
                "FLASH DE SOBREVIVÊNCIA",
                [
                    "• 6 Cargas de Flash: Permite mover-se e agir quando todas as velas estão apagadas.",
                    "• Clarão Ofuscante: O flash cega as criaturas nas sombras ao realizar ações no escuro.",
                    "• Limite de Sobrevivência: A derrota só ocorre se agir no escuro após as 6 cargas acabarem."
                ],
                "Ação nas Trevas"
            )
        elif a_type == "BAG":
            return (
                "Bolsa Verde Musgo",
                "ALQUIMIA & ESPAÇO",
                [
                    "• Capacidade: 4 velas no inventário. Chance no altar de encantar velas por cor:",
                    "  [ Verde ] Chama Maior (+4t de queima bônus).",
                    "  [ Ciano ] Ação Livre (troca de vela com custo 0 de turnos).",
                    "  [ Púrpura ] Altar Adjacente (o fogo salta e estende a pilastra vizinha +3t)."
                ],
                "Recursos Expandidos"
            )
        else:
            return (
                "Lanterna Moderna",
                "FEIXE DE LONGO ALCANCE & RECARGA",
                [
                    "• 9 Cargas de Bateria: Dispara à distância sem gastar turnos (soma turnos à vela).",
                    "• Recarga por Repouso: Ficar parado por 2 turnos recupera +3 cargas de bateria (máx. 9).",
                    "• Super Queima: Velas com 10 ou mais turnos travam o decaimento por 3 rodadas completas."
                ],
                "Interação Remota"
            )

    def draw_upgrades_screen(self, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("COMPÊNDIO DE MELHORIAS & RITUAIS", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        sub = self.font_small.render("Guia completo de Arquétipos, Relíquias, Bênçãos e Mecânicas de Sobrevivência", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, 54))

        panel_rect = pygame.Rect(40, 85, 920, 525)
        surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(surf, COLOR_UI_BORDER, (0, 0, panel_rect.width, panel_rect.height), 1, border_radius=12)
        self.screen.blit(surf, (panel_rect.x, panel_rect.y))

        col_w = 280
        col_gap = 20
        col_y = panel_rect.y + 16

        # --- COLUNA 1: PERSONAS ---
        c1_x = panel_rect.x + 20
        c1_box = pygame.Rect(c1_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c1_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c1_box, 1, border_radius=8)

        t1 = self.font_mid.render("1. PERSONAS (5/5)", True, COLOR_TEXT)
        b1 = self.font_tiny.render("[ARQUÉTIPOS]", True, COLOR_ACCENT_GREEN)
        self.screen.blit(t1, (c1_x + 14, col_y + 12))
        self.screen.blit(b1, (c1_x + c1_box.width - b1.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c1_x + 14, col_y + 38), (c1_x + c1_box.width - 14, col_y + 38), 1)

        personas_info = [
            ("O Zelador", "+2t ao reacender; [Q] Pega vela do bolso sem ir ao altar."),
            ("O Ocultista", "Recarga de artefatos rápida; [Q] Prece da Luz repele sombras."),
            ("O Andarilho", "40% Passo Livre na coluna; [Q] Sprint instantâneo ao Altar."),
            ("O Paladino", "+1t de piso permanente por purga; [Q] Julgamento Sagrado."),
            ("Nascido da Lua", "Sob penumbra: +2t em trocas e 50% passo livre; [Q] Eclipse.")
        ]
        py = col_y + 48
        for p_name, p_desc in personas_info:
            pn_s = self.font_small.render(f"• {p_name}", True, (255, 255, 255))
            self.screen.blit(pn_s, (c1_x + 12, py))
            py = self.draw_wrapped_text(p_desc, self.font_tiny, COLOR_TEXT_MUTED, c1_x + 22, py + 18, max_width=col_w - 32, line_spacing=2) + 8

        # --- COLUNA 2: ARTEFATOS ---
        c2_x = c1_x + col_w + col_gap
        c2_box = pygame.Rect(c2_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c2_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c2_box, 1, border_radius=8)

        t2 = self.font_mid.render("2. ARTEFATOS (5/5)", True, COLOR_TEXT)
        b2 = self.font_tiny.render("[RELÍQUIAS]", True, COLOR_ACCENT_BLUE)
        self.screen.blit(t2, (c2_x + 14, col_y + 12))
        self.screen.blit(b2, (c2_x + c2_box.width - b2.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c2_x + 14, col_y + 38), (c2_x + c2_box.width - 14, col_y + 38), 1)

        artifacts_info = [
            ("Cruz de Prata", "+1t em trocas; se as 6 apagarem, ressuscita 2 velas (+4t)."),
            ("Lampião Espectral", "A pilastra onde o jogador estiver NÃO consome turnos de queima."),
            ("Câmera Retrô", "6 flashes para mover e agir nas trevas totais com segurança."),
            ("Bolsa Musgo", "4 slots; chance de velas Verde(+4t), Ciano(0t) e Púrpura(+3t)."),
            ("Lanterna Moderna", "Feixe remoto (0t); repouso por 2 turnos recupera +3 baterias.")
        ]
        ay = col_y + 48
        for a_name, a_desc in artifacts_info:
            an_s = self.font_small.render(f"• {a_name}", True, (255, 255, 255))
            self.screen.blit(an_s, (c2_x + 12, ay))
            ay = self.draw_wrapped_text(a_desc, self.font_tiny, COLOR_TEXT_MUTED, c2_x + 22, ay + 18, max_width=col_w - 32, line_spacing=2) + 8

        # --- COLUNA 3: BÊNÇÃOS & MECÂNICAS ---
        c3_x = c2_x + col_w + col_gap
        c3_box = pygame.Rect(c3_x, col_y, col_w, 455)
        pygame.draw.rect(self.screen, (20, 28, 42), c3_box, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, c3_box, 1, border_radius=8)

        t3 = self.font_mid.render("3. BÊNÇÃOS (8/8)", True, COLOR_TEXT)
        b3 = self.font_tiny.render("[DÁDIVAS]", True, COLOR_ENCHANT_GOLD)
        self.screen.blit(t3, (c3_x + 14, col_y + 12))
        self.screen.blit(b3, (c3_x + c3_box.width - b3.get_width() - 14, col_y + 15))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (c3_x + 14, col_y + 38), (c3_x + c3_box.width - 14, col_y + 38), 1)

        mechanics_info = [
            ("8 Bênçãos Sagradas", "Fogo Perpétuo, Passos Silenciosos, Abundância, Sincronia, Sobrecarga Adrenal, Fôlego Vigoroso, Vínculo Térmico e Fogo Fátuo."),
            ("Trava de Sobrecarga", "Velas atingindo >= 10 turnos ganham aura dourada e sustentam a queima travada por 3 rodadas completas!"),
            ("Velas Douradas", "40% de chance no Altar com Abundância para velas que queimam pelo dobro da duração.")
        ]
        my = col_y + 48
        for m_name, m_desc in mechanics_info:
            mn_s = self.font_small.render(f"• {m_name}", True, (255, 255, 255))
            self.screen.blit(mn_s, (c3_x + 12, my))
            my = self.draw_wrapped_text(m_desc, self.font_tiny, COLOR_TEXT_MUTED, c3_x + 22, my + 18, max_width=col_w - 32, line_spacing=2) + 12

        badge = self.font_tiny.render("[Todos os 5 Arquétipos, 5 Relíquias e 8 Bênçãos estão 100% integrados]", True, COLOR_ACCENT_GREEN)
        self.screen.blit(badge, (panel_rect.x + (panel_rect.width - badge.get_width()) // 2, panel_rect.bottom - 22))

        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 68, 280, 42)
        self.draw_button(back_btn, "VOLTAR AO MENU", back_btn.collidepoint(mouse_pos))

    def draw_settings_screen(self, mouse_pos, is_fullscreen, sound_enabled, sound_volume, current_difficulty):
        self.screen.fill(COLOR_BG)
        self.draw_floor()

        title = self.font_large.render("CONFIGURAÇÕES DO JOGO", True, COLOR_TEXT)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 22))

        panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 360, 68, 720, 545)
        surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(surf, COLOR_UI_BORDER, (0, 0, panel_rect.width, panel_rect.height), 1, border_radius=12)
        self.screen.blit(surf, (panel_rect.x, panel_rect.y))

        sec1_title = self.font_mid.render("1. Vídeo e Exibição", True, COLOR_TEXT)
        self.screen.blit(sec1_title, (panel_rect.x + 35, panel_rect.y + 18))

        screen_btn_rect = pygame.Rect(panel_rect.x + 35, panel_rect.y + 44, 280, 42)
        mode_str = "TELA CHEIA" if is_fullscreen else "MODO JANELA"
        self.draw_button(screen_btn_rect, mode_str, screen_btn_rect.collidepoint(mouse_pos), subtext="[F11 para alternar]")

        sec2_title = self.font_mid.render("2. Controle de Áudio & Volume", True, COLOR_TEXT)
        self.screen.blit(sec2_title, (panel_rect.x + 35, panel_rect.y + 105))

        mute_btn_rect = pygame.Rect(panel_rect.x + 35, panel_rect.y + 132, 230, 42)
        mute_str = "ÁUDIO: ATIVO" if sound_enabled else "ÁUDIO: SILENCIADO"
        self.draw_button(mute_btn_rect, mute_str, mute_btn_rect.collidepoint(mouse_pos), subtext="[Clique para silenciar]")

        vol_box_rect = pygame.Rect(panel_rect.x + 285, panel_rect.y + 132, 395, 42)
        pygame.draw.rect(self.screen, (22, 30, 46), vol_box_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, vol_box_rect, 1, border_radius=8)

        v_minus_rect = pygame.Rect(vol_box_rect.x + 10, vol_box_rect.y + 7, 32, 28)
        v_plus_rect = pygame.Rect(vol_box_rect.right - 42, vol_box_rect.y + 7, 32, 28)
        self.draw_button(v_minus_rect, "-", v_minus_rect.collidepoint(mouse_pos))
        self.draw_button(v_plus_rect, "+", v_plus_rect.collidepoint(mouse_pos))

        bar_x = v_minus_rect.right + 12
        bar_w = v_plus_rect.x - bar_x - 12
        bar_y = vol_box_rect.y + 16
        pygame.draw.rect(self.screen, (35, 45, 65), (bar_x, bar_y, bar_w, 10), border_radius=5)
        
        cur_vol = sound_volume if sound_enabled else 0.0
        fill_w = int(bar_w * cur_vol)
        if fill_w > 0:
            pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, (bar_x, bar_y, fill_w, 10), border_radius=5)

        vol_pct = int(sound_volume * 100) if sound_enabled else 0
        v_txt = self.font_tiny.render(f"Volume: {vol_pct}%", True, COLOR_TEXT_MUTED)
        self.screen.blit(v_txt, (bar_x + (bar_w - v_txt.get_width()) // 2, vol_box_rect.y - 14))

        sec3_title = self.font_mid.render("3. Nível de Dificuldade / Modo de Jogo", True, COLOR_TEXT)
        self.screen.blit(sec3_title, (panel_rect.x + 35, panel_rect.y + 195))

        diff_w = 152
        diff_h = 44
        diff_gap = 14
        d_start_x = panel_rect.x + 35

        diff_buttons = [
            (DIFFICULTY_EASY, "SUAVE", pygame.Rect(d_start_x, panel_rect.y + 225, diff_w, diff_h), COLOR_ACCENT_GREEN),
            (DIFFICULTY_NORMAL, "PADRÃO", pygame.Rect(d_start_x + (diff_w + diff_gap), panel_rect.y + 225, diff_w, diff_h), COLOR_ACCENT_BLUE),
            (DIFFICULTY_HARD, "HORROR", pygame.Rect(d_start_x + (diff_w + diff_gap) * 2, panel_rect.y + 225, diff_w, diff_h), COLOR_ACCENT_RED),
            (DIFFICULTY_ENDLESS, "NOITE SEM FIM", pygame.Rect(d_start_x + (diff_w + diff_gap) * 3, panel_rect.y + 225, diff_w, diff_h), COLOR_ACCENT_PURPLE)
        ]

        for d_key, d_label, d_rect, d_col in diff_buttons:
            is_cur = (current_difficulty == d_key)
            is_hov = d_rect.collidepoint(mouse_pos)
            
            d_surf = pygame.Surface((d_rect.width, d_rect.height), pygame.SRCALPHA)
            bg_c = (30, 48, 75) if is_cur else (COLOR_UI_PANEL_HOVER if is_hov else COLOR_UI_PANEL)
            b_c = d_col if is_cur else (COLOR_UI_BORDER if not is_hov else (90, 115, 150))
            
            pygame.draw.rect(d_surf, bg_c, (0, 0, d_rect.width, d_rect.height), border_radius=8)
            pygame.draw.rect(d_surf, b_c, (0, 0, d_rect.width, d_rect.height), 2 if is_cur or is_hov else 1, border_radius=8)
            self.screen.blit(d_surf, (d_rect.x, d_rect.y))

            t_col = (255, 255, 255) if is_cur else (COLOR_TEXT if is_hov else COLOR_TEXT_MUTED)
            txt_s = self.font_small.render(d_label, True, t_col)
            self.screen.blit(txt_s, (d_rect.x + (d_rect.width - txt_s.get_width()) // 2, d_rect.y + 14))

        diff_desc_box = pygame.Rect(panel_rect.x + 35, panel_rect.y + 280, 650, 64)
        pygame.draw.rect(self.screen, (15, 22, 35), diff_desc_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, diff_desc_box, 1, border_radius=6)

        if current_difficulty == DIFFICULTY_EASY:
            d_lines = [
                "• SUAVE: As velas iniciam e renovam com +1 turno mínimo base (Lua Azul).",
                "  Meta de rodadas reduzida (-10t). Ideal para um ritual mais paciente e estratégico."
            ]
        elif current_difficulty == DIFFICULTY_NORMAL:
            d_lines = [
                "• PADRÃO: Queima dinâmica padrão (mínimo de 5 turnos no início - Lua Prateada).",
                "  A cada vela apagada, a duração mínima é reduzida. Meta padrão do Arquétipo."
            ]
        elif current_difficulty == DIFFICULTY_HARD:
            d_lines = [
                "• NOITE DE HORROR: Sem valor mínimo fixo! (Lua de Sangue Vermelha).",
                "  Queima imprevisível, rápida e impiedosa (+15t de meta). Máximo desafio."
            ]
        else:
            d_lines = [
                "• NOITE SEM FIM: Modo de Sobrevivência Pura sem meta de rodadas (Lua Noturna Violeta).",
                "  A escuridão é infinita e a aurora nunca chega. Sobreviva o máximo de turnos possível!"
            ]

        d_y = diff_desc_box.y + 8
        for idx, line in enumerate(d_lines):
            if current_difficulty == DIFFICULTY_EASY:
                l_col = COLOR_ACCENT_GREEN
            elif current_difficulty == DIFFICULTY_NORMAL:
                l_col = COLOR_ACCENT_BLUE
            elif current_difficulty == DIFFICULTY_HARD:
                l_col = COLOR_ACCENT_RED
            else:
                l_col = COLOR_ACCENT_PURPLE
            d_y = self.draw_wrapped_text(line, self.font_small, l_col if idx == 0 else COLOR_TEXT_MUTED, diff_desc_box.x + 15, d_y, max_width=diff_desc_box.width - 30, line_spacing=2)

        guide_title = self.font_mid.render("4. Guia de Teclas Rápidas", True, COLOR_TEXT)
        self.screen.blit(guide_title, (panel_rect.x + 35, panel_rect.y + 360))

        controls = [
            ("1 a 6 / Clique Esq.", "Mover até a Pilastra"),
            ("Q / Botão HUD", "Usar Habilidade Ativa do Arquétipo"),
            ("Clique Dir. / Shift+1-6", "Disparar Feixe da Lanterna à distância"),
            ("W (2x sem mover)", "Aguardar / Recarregar Baterias da Lanterna")
        ]

        cy = panel_rect.y + 390
        for k, d in controls:
            k_surf = self.font_small.render(k, True, COLOR_ACCENT_BLUE)
            d_surf = self.font_tiny.render(d, True, COLOR_TEXT_MUTED)
            self.screen.blit(k_surf, (panel_rect.x + 35, cy))
            self.screen.blit(d_surf, (panel_rect.x + 235, cy + 2))
            cy += 20

        back_btn = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 65, 280, 42)
        self.draw_button(back_btn, "VOLTAR AO MENU", back_btn.collidepoint(mouse_pos))

    def render_gameplay(self, engine, mouse_pos):
        self.screen.fill(COLOR_BG)
        self.draw_floor()
        self.draw_gothic_window(engine)
        self.draw_corridors()
        self.draw_altar(engine)
        self.draw_pillars(engine)
        self.draw_particles()
        self.draw_player(engine)
        self.draw_lighting_and_creature(engine)
        self.draw_window_sunbeams(engine)
        self.draw_beam_effect(engine)
        self.draw_silver_burst(engine)
        self.draw_camera_flash(engine)
        self.draw_purge_burst(engine)
        self.draw_hud(engine, mouse_pos)

        if engine.game_over:
            self.draw_game_over(engine, mouse_pos)

    def draw_gothic_window(self, engine):
        win_w, win_h = 400, 130
        win_x = WINDOW_WIDTH // 2 - win_w // 2
        win_y = 86
        cx = win_w // 2
        t = self.time_elapsed

        ext_count = engine.extinguished_count
        light_ratio = max(0.10, 1.0 - (ext_count / 6.0) * 0.85)
        if engine.player.persona.light_prayer_turns > 0:
            light_ratio = min(1.0, light_ratio + 0.35)

        sky_surf = pygame.Surface((win_w, win_h), pygame.SRCALPHA)

        is_victory = engine.victory
        if engine.target_victory_turns is not None:
            prog = min(1.0, max(0.0, engine.turn / float(engine.target_victory_turns)))
        else:
            prog = ((t * 0.04 + engine.turn * 0.03) % 1.0)

        if is_victory:
            top_sky = (255, 175, 75)
            mid_sky = (255, 215, 130)
            bot_sky = (250, 160, 135)
        elif prog >= 0.75 and engine.target_victory_turns is not None:
            tw_f = (prog - 0.75) / 0.25
            top_sky = (int(12 + tw_f * 40), int(16 + tw_f * 35), int(35 + tw_f * 50))
            mid_sky = (int(20 + tw_f * 70), int(26 + tw_f * 60), int(55 + tw_f * 70))
            bot_sky = (int(30 + tw_f * 120), int(25 + tw_f * 75), int(45 + tw_f * 75))
        else:
            top_sky = (6, 10, 22)
            mid_sky = (12, 18, 36)
            bot_sky = (18, 26, 48)

        for y_step in range(win_h):
            ratio = y_step / float(win_h)
            if ratio < 0.5:
                r_half = ratio * 2.0
                r = int(top_sky[0] * (1.0 - r_half) + mid_sky[0] * r_half)
                g = int(top_sky[1] * (1.0 - r_half) + mid_sky[1] * r_half)
                b = int(top_sky[2] * (1.0 - r_half) + mid_sky[2] * r_half)
            else:
                r_half = (ratio - 0.5) * 2.0
                r = int(mid_sky[0] * (1.0 - r_half) + bot_sky[0] * r_half)
                g = int(mid_sky[1] * (1.0 - r_half) + bot_sky[1] * r_half)
                b = int(mid_sky[2] * (1.0 - r_half) + bot_sky[2] * r_half)
            pygame.draw.line(sky_surf, (r, g, b), (0, y_step), (win_w, y_step))

        if not is_victory and prog < 0.85:
            star_fade = (1.0 - (prog - 0.5) / 0.35 if prog > 0.5 and engine.target_victory_turns is not None else 1.0) * light_ratio
            for idx, (sx, sy, seed) in enumerate([
                (45, 35, 1.2), (85, 50, 2.5), (125, 25, 4.1), (165, 58, 0.8),
                (240, 28, 3.3), (280, 52, 5.0), (325, 24, 1.9), (365, 45, 2.8),
                (65, 72, 3.7), (105, 82, 1.1), (200, 22, 4.9), (300, 78, 2.3),
                (145, 42, 5.7), (255, 38, 1.6), (345, 65, 4.4), (180, 75, 3.1)
            ]):
                twinkle = 0.5 + 0.5 * math.sin(t * 3.5 + seed * 5.0)
                s_alpha = int(220 * twinkle * star_fade)
                if s_alpha > 10:
                    pygame.draw.circle(sky_surf, (230, 240, 255, s_alpha), (sx, sy), 1)

        if is_victory:
            sun_x = cx
            sun_y = 58
            
            for ray_i in range(12):
                ray_ang = ray_i * (math.pi / 6) + t * 0.8
                ray_len = 42 + 12 * math.sin(t * 4.0 + ray_i)
                rx = sun_x + math.cos(ray_ang) * ray_len
                ry = sun_y + math.sin(ray_ang) * (ray_len * 0.65)
                pygame.draw.line(sky_surf, (255, 235, 160, 140), (sun_x, sun_y), (int(rx), int(ry)), 2)

            pygame.draw.circle(sky_surf, (255, 215, 90, 80), (sun_x, sun_y), 40)
            pygame.draw.circle(sky_surf, (255, 230, 120, 140), (sun_x, sun_y), 26)
            pygame.draw.circle(sky_surf, (255, 250, 200, 220), (sun_x, sun_y), 18)
            pygame.draw.circle(sky_surf, (255, 255, 255), (sun_x, sun_y), 11)
        else:
            moon_x = int(50 + prog * (win_w - 100) + math.sin(t * 0.7) * 7)
            arc_rise = math.sin(prog * math.pi) * 44
            moon_y = int(92 - arc_rise + math.cos(t * 0.5) * 4)

            if engine.difficulty == DIFFICULTY_EASY:
                m_core = (125, 211, 252)
                m_glow = (56, 189, 248, int(60 * light_ratio))
                is_crescent = True
            elif engine.difficulty == DIFFICULTY_NORMAL:
                m_core = (226, 232, 240)
                m_glow = (200, 220, 255, int(55 * light_ratio))
                is_crescent = False
            elif engine.difficulty == DIFFICULTY_HARD:
                m_core = (239, 68, 68)
                m_glow = (255, 20, 45, int(70 * light_ratio))
                is_crescent = False
            else:
                m_core = (192, 132, 252)
                m_glow = (168, 85, 247, int(65 * light_ratio))
                is_crescent = True

            pygame.draw.circle(sky_surf, m_glow, (moon_x, moon_y), 28)
            pygame.draw.circle(sky_surf, (*m_core[:3], int(110 * light_ratio)), (moon_x, moon_y), 18)
            pygame.draw.circle(sky_surf, m_core, (moon_x, moon_y), 13)
            
            if is_crescent:
                c_off = int(6 * (1.0 - prog * 0.5))
                pygame.draw.circle(sky_surf, top_sky, (moon_x + c_off, moon_y - 3), 11)
            else:
                pygame.draw.circle(sky_surf, (int(m_core[0]*0.72), int(m_core[1]*0.72), int(m_core[2]*0.72)), (moon_x - 4, moon_y - 2), 3)
                pygame.draw.circle(sky_surf, (int(m_core[0]*0.72), int(m_core[1]*0.72), int(m_core[2]*0.72)), (moon_x + 4, moon_y + 3), 2)

        cloud_col_back = (255, 220, 180, 140) if is_victory else (20, 30, 50, int(110 * light_ratio))
        cloud_col_mid = (255, 240, 205, 170) if is_victory else (30, 42, 68, int(140 * light_ratio))
        cloud_col_fore = (255, 250, 230, 200) if is_victory else (45, 60, 92, int(120 * light_ratio))

        for c_i in range(4):
            c_offset = c_i * 130
            c_x = int((t * 14.0 + c_offset) % (win_w + 180)) - 90
            c_y = 40 + int(math.sin(t * 0.5 + c_i) * 5)
            pygame.draw.circle(sky_surf, cloud_col_back, (c_x, c_y), 32)
            pygame.draw.circle(sky_surf, cloud_col_back, (c_x + 25, c_y + 4), 25)
            pygame.draw.circle(sky_surf, cloud_col_back, (c_x - 22, c_y + 6), 22)

        for c_i in range(3):
            c_offset = c_i * 160 + 60
            c_x = int((t * 24.0 + c_offset) % (win_w + 200)) - 100
            c_y = 65 + int(math.cos(t * 0.7 + c_i) * 6)
            pygame.draw.circle(sky_surf, cloud_col_mid, (c_x, c_y), 36)
            pygame.draw.circle(sky_surf, cloud_col_mid, (c_x + 28, c_y + 5), 28)
            pygame.draw.circle(sky_surf, cloud_col_mid, (c_x - 26, c_y + 7), 26)

        for c_i in range(3):
            c_offset = c_i * 150 + 30
            c_x = int((t * 36.0 + c_offset) % (win_w + 180)) - 90
            c_y = 88 + int(math.sin(t * 1.1 + c_i) * 4)
            pygame.draw.circle(sky_surf, cloud_col_fore, (c_x, c_y), 26)
            pygame.draw.circle(sky_surf, cloud_col_fore, (c_x + 22, c_y + 3), 20)

        if not is_victory and light_ratio < 0.9:
            shadow_mask = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
            shadow_alpha = int((1.0 - light_ratio) * 160)
            shadow_mask.fill((3, 5, 10, shadow_alpha))
            sky_surf.blit(shadow_mask, (0, 0))

        mask_surf = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        arch_rect = pygame.Rect(12, 10, win_w - 24, (win_h - 10) * 2)
        pygame.draw.ellipse(mask_surf, (255, 255, 255, 255), arch_rect)
        rect_base = pygame.Rect(12, win_h // 2, win_w - 24, win_h // 2 - 4)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), rect_base)

        sky_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(sky_surf, (win_x, win_y))

        mullion_xs = [win_x + 14 + int((win_w - 28) * (i / 6.0)) for i in range(1, 6)]
        for mx in mullion_xs:
            rel_mx = mx - win_x
            norm_x = (rel_mx - cx) / (float(win_w - 28) / 2.0)
            norm_x = max(-1.0, min(1.0, norm_x))
            arch_top_y = win_y + 10 + int((1.0 - math.sqrt(max(0.0, 1.0 - norm_x ** 2))) * ((win_h - 10)))
            pygame.draw.line(self.screen, (30, 38, 52), (mx, arch_top_y), (mx, win_y + win_h - 4), 2)
            pygame.draw.line(self.screen, (55, 68, 90), (mx + 1, arch_top_y), (mx + 1, win_y + win_h - 4), 1)

        for hy_pct in [0.45, 0.72]:
            hy = win_y + int(win_h * hy_pct)
            norm_y = (hy - win_y - 10) / float(win_h - 10)
            w_span = int((win_w - 28) * math.sqrt(max(0.0, 1.0 - max(0.0, 1.0 - norm_y) ** 2)))
            pygame.draw.line(self.screen, (35, 45, 62), (cx - w_span // 2 + win_x, hy), (cx + w_span // 2 + win_x, hy), 2)

        pygame.draw.ellipse(self.screen, (10, 14, 22), (win_x + 8, win_y + 6, win_w - 16, (win_h - 6) * 2), 6)
        pygame.draw.rect(self.screen, (10, 14, 22), (win_x + 8, win_y + win_h // 2, win_w - 16, win_h // 2), 6)

        stone_col = (50, 65, 88)
        pygame.draw.ellipse(self.screen, stone_col, (win_x + 10, win_y + 8, win_w - 20, (win_h - 8) * 2), 3)
        pygame.draw.rect(self.screen, stone_col, (win_x + 10, win_y + win_h // 2, win_w - 20, win_h // 2 - 2), 3)

        pygame.draw.ellipse(self.screen, (80, 105, 138), (win_x + 12, win_y + 10, win_w - 24, (win_h - 10) * 2), 1)
        pygame.draw.rect(self.screen, (80, 105, 138), (win_x + 12, win_y + win_h // 2, win_w - 24, win_h // 2 - 4), 1)

        sill_rect = pygame.Rect(win_x + 6, win_y + win_h - 6, win_w - 12, 10)
        pygame.draw.rect(self.screen, (32, 42, 58), sill_rect, border_radius=3)
        pygame.draw.rect(self.screen, (70, 90, 120), sill_rect, 1, border_radius=3)

    def draw_window_sunbeams(self, engine):
        win_w, win_h = 400, 130
        win_x = WINDOW_WIDTH // 2 - win_w // 2
        win_y = 86
        cx = WINDOW_WIDTH // 2
        t = self.time_elapsed

        ext_count = engine.extinguished_count
        light_ratio = max(0.08, 1.0 - (ext_count / 6.0) * 0.85)
        if engine.player.persona.light_prayer_turns > 0:
            light_ratio = min(1.0, light_ratio + 0.35)

        beam_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        if engine.victory:
            alpha_pulse = int(55 + 20 * math.sin(t * 2.5))
            
            beams = [
                ((cx - 140, win_y + 80), (100, WINDOW_HEIGHT - 60), 85),
                ((cx - 70, win_y + 75), (260, WINDOW_HEIGHT - 50), 100),
                ((cx, win_y + 70), (cx, WINDOW_HEIGHT - 40), 120),
                ((cx + 70, win_y + 75), (740, WINDOW_HEIGHT - 50), 100),
                ((cx + 140, win_y + 80), (900, WINDOW_HEIGHT - 60), 85)
            ]
            for (p_top, p_bot, w_bot) in beams:
                poly = [
                    (p_top[0] - 18, p_top[1]),
                    (p_top[0] + 18, p_top[1]),
                    (p_bot[0] + w_bot // 2, p_bot[1]),
                    (p_bot[0] - w_bot // 2, p_bot[1])
                ]
                pygame.draw.polygon(beam_surf, (255, 220, 130, alpha_pulse), poly)
                poly_core = [
                    (p_top[0] - 6, p_top[1]),
                    (p_top[0] + 6, p_top[1]),
                    (p_bot[0] + w_bot // 4, p_bot[1]),
                    (p_bot[0] - w_bot // 4, p_bot[1])
                ]
                pygame.draw.polygon(beam_surf, (255, 245, 190, int(alpha_pulse * 0.7)), poly_core)

            for m_i in range(18):
                m_seed = m_i * 1.7
                mx = int(cx - 240 + ((t * 25.0 + m_seed * 80) % 480))
                my = int(160 + ((t * 18.0 + m_seed * 60) % (WINDOW_HEIGHT - 260)))
                m_alpha = int(140 + 80 * math.sin(t * 3.0 + m_seed))
                pygame.draw.circle(beam_surf, (255, 245, 180, m_alpha), (mx, my), 2)

        else:
            alpha_moon = int((24 + 10 * math.sin(t * 1.8)) * light_ratio)
            moon_col = (180, 220, 255, alpha_moon)
            if engine.difficulty == DIFFICULTY_HARD:
                moon_col = (255, 120, 130, alpha_moon)
            elif engine.difficulty == DIFFICULTY_ENDLESS:
                moon_col = (210, 160, 255, alpha_moon)

            for (p_top, p_bot, w_bot) in [
                ((cx - 90, win_y + 85), (250, 520), 85),
                ((cx, win_y + 80), (cx, 550), 105),
                ((cx + 90, win_y + 85), (750, 520), 85)
            ]:
                poly = [
                    (p_top[0] - 14, p_top[1]),
                    (p_top[0] + 14, p_top[1]),
                    (p_bot[0] + w_bot // 2, p_bot[1]),
                    (p_bot[0] - w_bot // 2, p_bot[1])
                ]
                pygame.draw.polygon(beam_surf, moon_col, poly)

        self.screen.blit(beam_surf, (0, 0))

    def draw_beam_effect(self, engine):
        if engine.beam_target is not None and engine.beam_timer > 0.0:
            target_pos = PILLAR_POSITIONS[engine.beam_target]
            px, py = int(self.player_visual_x), int(self.player_visual_y)
            alpha = int(engine.beam_timer * 255)

            beam_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(beam_surf, (100, 200, 255, alpha), (px, py), target_pos, 8)
            pygame.draw.line(beam_surf, (255, 255, 255, alpha), (px, py), target_pos, 3)
            pygame.draw.circle(beam_surf, (200, 240, 255, alpha), target_pos, int(25 * engine.beam_timer))
            self.screen.blit(beam_surf, (0, 0))

    def draw_silver_burst(self, engine):
        if engine.silver_burst <= 0.0:
            return

        burst_alpha = int(engine.silver_burst * 220)
        burst_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        burst_surf.fill((210, 230, 255, burst_alpha))

        cx, cy = int(self.player_visual_x), int(self.player_visual_y)
        ring_rad = int((1.0 - engine.silver_burst) * 500)
        pygame.draw.circle(burst_surf, (255, 255, 255, burst_alpha), (cx, cy), ring_rad, 8)

        self.screen.blit(burst_surf, (0, 0))

    def draw_camera_flash(self, engine):
        if engine.camera_flash <= 0.0:
            return

        flash_alpha = int(engine.camera_flash * 255)
        flash_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 240, flash_alpha))
        self.screen.blit(flash_surf, (0, 0))

    def draw_purge_burst(self, engine):
        if not hasattr(engine, 'purge_burst') or engine.purge_burst <= 0.0:
            return

        burst_alpha = int(engine.purge_burst * 230)
        burst_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        burst_surf.fill((254, 240, 138, int(burst_alpha * 0.35)))

        cx, cy = int(self.player_visual_x), int(self.player_visual_y)
        ring_rad = int((1.0 - engine.purge_burst) * 520 + 20)
        pygame.draw.circle(burst_surf, (253, 224, 71, burst_alpha), (cx, cy), ring_rad, 8)
        pygame.draw.circle(burst_surf, (255, 255, 255, burst_alpha), (cx, cy), int(ring_rad * 0.75), 4)

        for i in range(8):
            ang = i * (math.pi / 4) + self.time_elapsed * 2.0
            rx = cx + math.cos(ang) * ring_rad
            ry = cy + math.sin(ang) * ring_rad
            pygame.draw.line(burst_surf, (254, 240, 138, burst_alpha), (cx, cy), (int(rx), int(ry)), 3)

        self.screen.blit(burst_surf, (0, 0))

    def draw_floor(self):
        tile_size = 50
        for x in range(0, WINDOW_WIDTH, tile_size):
            for y in range(0, WINDOW_HEIGHT, tile_size):
                rect = pygame.Rect(x, y, tile_size, tile_size)
                pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                pygame.draw.rect(self.screen, COLOR_FLOOR_GRID, rect, 1)

        hall_center_rect = pygame.Rect(120, 100, WINDOW_WIDTH - 240, WINDOW_HEIGHT - 200)
        pygame.draw.rect(self.screen, (20, 29, 48), hall_center_rect, 2)

    def draw_corridors(self):
        cx, cy = CENTER_POSITION
        for pos in PILLAR_POSITIONS.values():
            pygame.draw.line(self.screen, (28, 38, 58), (cx, cy), pos, 3)

    def draw_altar(self, engine):
        cx, cy = CENTER_POSITION
        altar_rect = pygame.Rect(cx - 38, cy - 38, 76, 76)
        pygame.draw.rect(self.screen, COLOR_PILLAR_SHADOW, altar_rect.inflate(12, 12), border_radius=12)
        
        is_disabled = (engine.altar_disabled_turns > 0)
        bg_col = (45, 30, 35) if is_disabled else COLOR_ALTAR
        glow_col = COLOR_ACCENT_RED if is_disabled else COLOR_ALTAR_GLOW

        pygame.draw.rect(self.screen, bg_col, altar_rect, border_radius=8)
        pygame.draw.rect(self.screen, glow_col, altar_rect, 2, border_radius=8)

        pygame.draw.circle(self.screen, (55, 40, 45) if is_disabled else (45, 60, 85), (cx, cy), 20)
        pygame.draw.circle(self.screen, COLOR_ACCENT_RED if is_disabled else COLOR_ACCENT_BLUE, (cx, cy), 14, 2)

        pulse = math.sin(self.time_elapsed * 3.0) * 2.0
        p_col = (255, 100, 100) if is_disabled else (100, 160, 255)
        pygame.draw.circle(self.screen, p_col, (cx, cy), int(5 + pulse))

        lbl_txt = f"ALTAR EXAUSTO ({engine.altar_disabled_turns}t)" if is_disabled else "ALTAR [C]"
        lbl_col = COLOR_ACCENT_RED if is_disabled else COLOR_TEXT_MUTED
        lbl = self.font_tiny.render(lbl_txt, True, lbl_col)
        self.screen.blit(lbl, (cx - lbl.get_width() // 2, cy + 44))

    def draw_pillars(self, engine):
        is_lantern = (engine.player.artifact.type == "LANTERN")
        player_loc = engine.player.current_location

        for pillar in engine.pillars:
            px, py = pillar.position
            c_state = pillar.candle.state
            is_frozen = (is_lantern and player_loc == str(pillar.id) and pillar.candle.is_lit)
            has_lock = (pillar.candle.freeze_turns_left > 0)
            is_embers = (pillar.candle.latent_embers > 0)

            shadow_rect = pygame.Rect(px - 26, py - 16, 52, 48)
            pygame.draw.rect(self.screen, COLOR_PILLAR_SHADOW, shadow_rect, border_radius=8)

            pillar_rect = pygame.Rect(px - 22, py - 20, 44, 42)
            pygame.draw.rect(self.screen, COLOR_PILLAR, pillar_rect, border_radius=6)
            
            border_col = COLOR_PILLAR_BORDER
            if self.hovered_target == str(pillar.id):
                border_col = COLOR_ACCENT_BLUE
            if is_frozen:
                border_col = COLOR_LANTERN_FLAME
            elif has_lock:
                border_col = (250, 204, 21)
            elif is_embers:
                border_col = (239, 68, 68)

            pygame.draw.rect(self.screen, border_col, pillar_rect, 2, border_radius=6)

            candle_body = pygame.Rect(px - 5, py - 32, 10, 14)
            pygame.draw.rect(self.screen, (180, 190, 205), candle_body, border_radius=2)

            if pillar.candle.is_lit:
                flicker = math.sin(self.time_elapsed * 12.0 + pillar.id * 1.5) * 2.0
                if c_state == "FAILING" or is_embers:
                    flicker += random.uniform(-3, 3)

                flame_h = 14 + flicker
                flame_w = 7 + flicker * 0.4
                if is_embers:
                    flame_h *= 0.35
                    flame_w *= 0.4
                elif c_state == "DIM":
                    flame_h *= 0.7
                    flame_w *= 0.7
                elif c_state == "FAILING":
                    flame_h *= 0.5
                    flame_w *= 0.5

                if is_frozen:
                    flame_outer = COLOR_LANTERN_FLAME
                    flame_inner = COLOR_LANTERN_CORE
                elif has_lock:
                    flame_outer = (250, 204, 21)
                    flame_inner = (254, 240, 138)
                elif is_embers:
                    flame_outer = (180, 40, 15)
                    flame_inner = (255, 100, 30)
                else:
                    flame_outer = COLOR_FLAME_OUTER
                    flame_inner = COLOR_FLAME_INNER

                flame_pts = [
                    (px, py - 32 - flame_h),
                    (px + flame_w, py - 32),
                    (px - flame_w, py - 32)
                ]
                pygame.draw.polygon(self.screen, flame_outer, flame_pts)

                inner_pts = [
                    (px, py - 32 - flame_h * 0.7),
                    (px + flame_w * 0.6, py - 32),
                    (px - flame_w * 0.6, py - 32)
                ]
                pygame.draw.polygon(self.screen, flame_inner, inner_pts)
                pygame.draw.circle(self.screen, COLOR_FLAME_CORE, (px, int(py - 32)), int(3))
            else:
                pygame.draw.line(self.screen, (60, 60, 70), (px, py - 32), (px, py - 36), 2)

            label = engine.get_pillar_label(pillar.id)
            lbl_key = f"{label} [{pillar.id + 1}]"
            t_surf = self.font_tiny.render(lbl_key, True, COLOR_TEXT)
            self.screen.blit(t_surf, (px - t_surf.get_width() // 2, py + 26))

            if pillar.candle.is_lit:
                if is_frozen:
                    status_text = f"{pillar.candle.turns_left}t (FROZEN)"
                    st_col = COLOR_LANTERN_FLAME
                elif has_lock:
                    status_text = f"{pillar.candle.turns_left}t (TRAVA {pillar.candle.freeze_turns_left}r)"
                    st_col = (250, 204, 21)
                elif is_embers:
                    status_text = "BRASA LATENTE"
                    st_col = (239, 68, 68)
                else:
                    status_text = f"{pillar.candle.turns_left}t"
                    if c_state == "BRIGHT":
                        st_col = COLOR_ACCENT_GREEN
                    elif c_state == "DIM":
                        st_col = (234, 179, 8)
                    else:
                        st_col = COLOR_ACCENT_RED
            else:
                status_text = "APAGADA"
                st_col = COLOR_TEXT_DIM

            st_surf = self.font_tiny.render(status_text, True, st_col)
            self.screen.blit(st_surf, (px - st_surf.get_width() // 2, py + 42))

    def draw_particles(self):
        for p in self.particles:
            alpha_ratio = p["life"] / p["max_life"]
            size = max(1.0, p["size"] * alpha_ratio)
            col_val = int(255 * alpha_ratio)
            if p["type"] == "FIRE":
                col = (col_val, int(col_val * 0.6), int(col_val * 0.2))
            else:
                col = (int(col_val * 0.3), int(col_val * 0.8), col_val)
            pygame.draw.circle(self.screen, col, (int(p["x"]), int(p["y"])), int(size))

    def draw_player(self, engine):
        px = int(self.player_visual_x)
        py = int(self.player_visual_y)

        pygame.draw.circle(self.screen, COLOR_PILLAR_SHADOW, (px, py + 6), 18)
        pygame.draw.circle(self.screen, (50, 75, 110), (px, py), 15)
        pygame.draw.circle(self.screen, (90, 130, 190), (px, py), 15, 2)
        pygame.draw.circle(self.screen, COLOR_TEXT, (px, py - 4), 6)

        item_x = px + 16
        item_y = py + 2
        art = engine.player.artifact
        if art.type == "CROSS":
            self.draw_silver_cross(self.screen, item_x, item_y, scale=0.55, is_charged=art.is_charged)
        elif art.type == "LANTERN":
            self.draw_spectral_lantern(self.screen, item_x, item_y, scale=0.55, is_active=True)
        elif art.type == "CAMERA":
            self.draw_retro_camera(self.screen, item_x, item_y, scale=0.55, charges=art.charges)
        elif art.type == "BAG":
            self.draw_moss_bag(self.screen, item_x, item_y, scale=0.55)
        elif art.type == "FLASHLIGHT":
            self.draw_modern_flashlight(self.screen, item_x, item_y, scale=0.55, charges=art.charges)

    def draw_lighting_and_creature(self, engine):
        if engine.victory:
            dawn_wash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dawn_wash.fill((255, 230, 160, 25))
            self.screen.blit(dawn_wash, (0, 0))
            return

        dark_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        ext_count = engine.extinguished_count

        base_darkness = 160 + int(ext_count * 15)
        if engine.player.persona.light_prayer_turns > 0:
            base_darkness = max(60, base_darkness - 100)
        elif engine.player.blessing.type == "STEALTH":
            base_darkness = max(110, base_darkness - 30)

        base_darkness = min(250, base_darkness)
        dark_surf.fill((8, 12, 20, base_darkness))

        for pillar in engine.pillars:
            if pillar.candle.is_lit:
                px, py = pillar.position
                c_state = pillar.candle.state
                
                if c_state == "BRIGHT":
                    radius = 170
                    strength = 200
                elif c_state == "DIM":
                    radius = 120
                    strength = 150
                else:
                    radius = 75 + int(math.sin(self.time_elapsed * 15.0) * 15)
                    strength = 110

                light_circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                for r in range(radius, 0, -8):
                    alpha = int((1.0 - (r / radius)) * strength)
                    pygame.draw.circle(light_circle, (255, 180, 70, alpha), (radius, radius), r)
                
                dark_surf.blit(light_circle, (px - radius, py - 32 - radius), special_flags=pygame.BLEND_RGBA_SUB)

        altar_x, altar_y = CENTER_POSITION
        altar_light = pygame.Surface((220, 220), pygame.SRCALPHA)
        for r in range(110, 0, -6):
            alpha = int((1.0 - (r / 110)) * 140)
            pygame.draw.circle(altar_light, (100, 160, 255), (110, 110), r)
        dark_surf.blit(altar_light, (altar_x - 110, altar_y - 110), special_flags=pygame.BLEND_RGBA_SUB)

        if engine.player.artifact.type == "LANTERN":
            plx, ply = int(self.player_visual_x), int(self.player_visual_y)
            lantern_light = pygame.Surface((260, 260), pygame.SRCALPHA)
            for r in range(130, 0, -8):
                alpha = int((1.0 - (r / 130)) * 160)
                pygame.draw.circle(lantern_light, (80, 200, 255, alpha), (130, 130), r)
            dark_surf.blit(lantern_light, (plx - 130, ply - 130), special_flags=pygame.BLEND_RGBA_SUB)

        self.screen.blit(dark_surf, (0, 0))

        if engine.creature.visible or engine.extinguished_count > 0:
            self.draw_creature_entity(engine)

    def draw_creature_entity(self, engine):
        proximity = engine.creature.proximity
        if proximity <= 0.01:
            return

        cx, cy = CENTER_POSITION
        diff = engine.difficulty
        t = self.time_elapsed

        if diff == DIFFICULTY_EASY:
            eye_col = (56, 189, 248)
            pupil_col = (224, 242, 254)
        elif diff == DIFFICULTY_NORMAL:
            eye_col = (245, 158, 11)
            pupil_col = (254, 243, 199)
        elif diff == DIFFICULTY_HARD:
            eye_col = (255, 20, 45)
            pupil_col = (69, 10, 10)
        else: # ENDLESS
            eye_col = (192, 132, 252)
            pupil_col = (243, 232, 255)

        eye_rad = int(3 + proximity * 4)
        creature_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        base_eye_pairs = [
            (65, 75),
            (935, 75),
            (65, 625),
            (935, 625),
            (500, 50)
        ]

        purged = engine.player.persona.purged_creatures
        remaining_count = max(0, len(base_eye_pairs) - purged)
        active_base_pairs = base_eye_pairs[:remaining_count]

        # Shadow encroachment & creeping inward movement as candles extinguish
        for i, (bx, by) in enumerate(active_base_pairs):
            # Advance towards the center altar as candles extinguish / proximity rises
            creep_factor = proximity * 0.52
            sway_x = math.sin(t * 2.6 + i * 1.3) * (5 + proximity * 10)
            sway_y = math.cos(t * 2.6 + i * 1.3) * (4 + proximity * 8)
            ex = int(bx + (cx - bx) * creep_factor + sway_x)
            ey = int(by + (cy - by) * creep_factor + sway_y)

            # Dark shadow phantom shroud behind the creature eyes
            shroud_alpha = int(proximity * 210)
            pygame.draw.circle(creature_surf, (4, 6, 12, int(shroud_alpha * 0.7)), (ex, ey), int(18 + proximity * 36))
            pygame.draw.circle(creature_surf, (8, 12, 20, int(shroud_alpha * 0.4)), (ex, ey), int(28 + proximity * 52))

            eye_glow_alpha = int(min(255, proximity * 280))
            pygame.draw.circle(creature_surf, (*eye_col, int(eye_glow_alpha * 0.45)), (int(ex - 8), int(ey)), eye_rad + 4)
            pygame.draw.circle(creature_surf, (*eye_col, int(eye_glow_alpha * 0.45)), (int(ex + 8), int(ey)), eye_rad + 4)
            pygame.draw.circle(creature_surf, eye_col, (int(ex - 8), int(ey)), eye_rad)
            pygame.draw.circle(creature_surf, eye_col, (int(ex + 8), int(ey)), eye_rad)

            if diff == DIFFICULTY_HARD and proximity >= 0.2:
                pygame.draw.line(creature_surf, (15, 2, 5, eye_glow_alpha), (int(ex - 8), int(ey - eye_rad)), (int(ex - 8), int(ey + eye_rad)), 2)
                pygame.draw.line(creature_surf, (15, 2, 5, eye_glow_alpha), (int(ex + 8), int(ey - eye_rad)), (int(ex + 8), int(ey + eye_rad)), 2)
                pygame.draw.circle(creature_surf, (*pupil_col, eye_glow_alpha), (int(ex - 8), int(ey)), 1)
                pygame.draw.circle(creature_surf, (*pupil_col, eye_glow_alpha), (int(ex + 8), int(ey)), 1)
            else:
                pygame.draw.circle(creature_surf, (*pupil_col, eye_glow_alpha), (int(ex - 8), int(ey)), max(1, eye_rad - 2))
                pygame.draw.circle(creature_surf, (*pupil_col, eye_glow_alpha), (int(ex + 8), int(ey)), max(1, eye_rad - 2))

        vignette_alpha = int(proximity * 190)
        vignette = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (2, 4, 8, vignette_alpha), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.draw.circle(vignette, (0, 0, 0, 0), (cx, cy), int(350 * (1.1 - proximity * 0.55)))
        creature_surf.blit(vignette, (0, 0))

        self.screen.blit(creature_surf, (0, 0))

    def draw_hud(self, engine, mouse_pos):
        top_bar = pygame.Rect(20, 15, WINDOW_WIDTH - 40, 56)
        top_surf = pygame.Surface((top_bar.width, top_bar.height), pygame.SRCALPHA)
        top_surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(top_surf, COLOR_UI_BORDER, (0, 0, top_bar.width, top_bar.height), 1, border_radius=8)
        self.screen.blit(top_surf, (top_bar.x, top_bar.y))

        if engine.target_victory_turns is not None:
            turn_str = f"TURNO: {engine.turn}/{engine.target_victory_turns}"
        else:
            turn_str = f"TURNO: {engine.turn} [NOITE SEM FIM]"
        turn_lbl = self.font_mid.render(turn_str, True, COLOR_TEXT)
        self.screen.blit(turn_lbl, (35, 28))

        active_x = 35 + turn_lbl.get_width() + 18
        if engine.player.persona.archetype_id == "PALADIN":
            purge_str = f"PURGAS: {engine.player.persona.purged_creatures}/5"
            purge_lbl = self.font_small.render(purge_str, True, COLOR_PALADIN_GOLD)
            self.screen.blit(purge_lbl, (active_x, 32))
            active_x += purge_lbl.get_width() + 18

        active_str = f"VELAS: {engine.active_candles_count}/6"
        act_col = COLOR_ACCENT_GREEN if engine.active_candles_count >= 4 else (COLOR_ACCENT_RED if engine.active_candles_count <= 2 else (234, 179, 8))
        active_lbl = self.font_mid.render(active_str, True, act_col)
        self.screen.blit(active_lbl, (active_x, 28))

        persona_str = f"[{engine.player.persona.name}]"
        pers_lbl = self.font_small.render(persona_str, True, COLOR_ACCENT_BLUE)
        self.screen.blit(pers_lbl, (315 if active_x < 315 else active_x + active_lbl.get_width() + 15, 32))

        pers_right = (315 if active_x < 315 else active_x + active_lbl.get_width() + 15) + pers_lbl.get_width() + 15
        bless_str = f"[{engine.player.blessing.name}]"
        bless_lbl = self.font_small.render(bless_str, True, COLOR_ACCENT_PURPLE)
        self.screen.blit(bless_lbl, (pers_right, 32))

        diff_names = {
            DIFFICULTY_EASY: "Suave",
            DIFFICULTY_NORMAL: "Padrão",
            DIFFICULTY_HARD: "Horror",
            DIFFICULTY_ENDLESS: "Sem Fim"
        }
        diff_str = f"DIF: {diff_names.get(engine.difficulty, 'Padrão')}"
        if engine.difficulty == DIFFICULTY_EASY:
            d_col = COLOR_ACCENT_GREEN
        elif engine.difficulty == DIFFICULTY_NORMAL:
            d_col = COLOR_ACCENT_BLUE
        elif engine.difficulty == DIFFICULTY_HARD:
            d_col = COLOR_ACCENT_RED
        else:
            d_col = COLOR_ACCENT_PURPLE
        diff_lbl = self.font_small.render(diff_str, True, d_col)
        self.screen.blit(diff_lbl, (685, 32))

        threat_str = "AMEAÇA: ALTA" if engine.extinguished_count >= 4 else ("AMEAÇA: MÉDIA" if engine.extinguished_count >= 2 else "AMEAÇA: BAIXA")
        th_col = COLOR_ACCENT_RED if engine.extinguished_count >= 4 else ((234, 179, 8) if engine.extinguished_count >= 2 else COLOR_ACCENT_GREEN)
        th_lbl = self.font_mid.render(threat_str, True, th_col)
        self.screen.blit(th_lbl, (WINDOW_WIDTH - 180, 28))

        bottom_bar = pygame.Rect(20, WINDOW_HEIGHT - 95, WINDOW_WIDTH - 40, 80)
        bot_surf = pygame.Surface((bottom_bar.width, bottom_bar.height), pygame.SRCALPHA)
        bot_surf.fill(COLOR_UI_PANEL)
        pygame.draw.rect(bot_surf, COLOR_UI_BORDER, (0, 0, bottom_bar.width, bottom_bar.height), 1, border_radius=8)
        self.screen.blit(bot_surf, (bottom_bar.x, bottom_bar.y))

        inv_title = self.font_tiny.render("VELAS:", True, COLOR_TEXT_MUTED)
        self.screen.blit(inv_title, (30, WINDOW_HEIGHT - 85))

        for i in range(engine.player.max_inventory):
            slot_rect = pygame.Rect(30 + i * 32, WINDOW_HEIGHT - 65, 26, 32)
            pygame.draw.rect(self.screen, (25, 35, 50), slot_rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_UI_BORDER, slot_rect, 1, border_radius=4)
            
            if i < len(engine.player.inventory):
                c_item = engine.player.inventory[i]
                flame_c = COLOR_FLAME_INNER
                border_c = COLOR_UI_BORDER
                body_c = (200, 210, 225)

                if c_item.enchantment == "GOLDEN":
                    flame_c = COLOR_ENCHANT_GOLD
                    border_c = COLOR_ENCHANT_GOLD
                    body_c = (255, 235, 140)
                elif c_item.enchantment == "GREATER_FLAME":
                    flame_c = COLOR_ENCHANT_FLAME
                    border_c = COLOR_ENCHANT_FLAME
                elif c_item.enchantment == "FREE_ACTION":
                    flame_c = COLOR_ENCHANT_FREE
                    border_c = COLOR_ENCHANT_FREE
                elif c_item.enchantment == "ADJACENT":
                    flame_c = COLOR_ENCHANT_ADJACENT
                    border_c = COLOR_ENCHANT_ADJACENT

                if c_item.enchantment is not None:
                    pygame.draw.rect(self.screen, (30, 45, 60), slot_rect, border_radius=4)
                    pygame.draw.rect(self.screen, border_c, slot_rect, 1, border_radius=4)

                pygame.draw.rect(self.screen, body_c, (slot_rect.x + 9, slot_rect.y + 11, 8, 15), border_radius=2)
                pygame.draw.circle(self.screen, flame_c, (slot_rect.x + 13, slot_rect.y + 8), 4)

        art_title = self.font_tiny.render("ARTEFATO:", True, COLOR_TEXT_MUTED)
        art_x = 30 + engine.player.max_inventory * 32 + 12
        self.screen.blit(art_title, (art_x, WINDOW_HEIGHT - 85))

        art_slot_w = 155
        art_slot_rect = pygame.Rect(art_x, WINDOW_HEIGHT - 65, art_slot_w, 32)
        pygame.draw.rect(self.screen, (25, 35, 50), art_slot_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_ACCENT_BLUE, art_slot_rect, 1, border_radius=4)

        art = engine.player.artifact
        if art.type == "CROSS":
            self.draw_silver_cross(self.screen, art_slot_rect.x + 16, art_slot_rect.y + 16, scale=0.55, is_charged=art.is_charged)
            status_str = "PRONTA (+1t)" if art.is_charged else "DESCARREGADA"
            status_col = COLOR_ACCENT_GREEN if art.is_charged else COLOR_ACCENT_RED
            art_lbl = self.font_tiny.render(status_str, True, status_col)
            self.screen.blit(art_lbl, (art_slot_rect.x + 32, art_slot_rect.y + 10))
        elif art.type == "LANTERN":
            self.draw_spectral_lantern(self.screen, art_slot_rect.x + 16, art_slot_rect.y + 16, scale=0.55, is_active=True)
            art_lbl = self.font_tiny.render("CHAMA CONGELADA", True, COLOR_LANTERN_FLAME)
            self.screen.blit(art_lbl, (art_slot_rect.x + 32, art_slot_rect.y + 10))
        elif art.type == "CAMERA":
            self.draw_retro_camera(self.screen, art_slot_rect.x + 16, art_slot_rect.y + 16, scale=0.55, charges=art.charges)
            status_str = f"{art.charges} FLASHES"
            status_col = COLOR_ACCENT_GREEN if art.charges > 2 else (COLOR_ACCENT_RED if art.charges == 0 else (234, 179, 8))
            art_lbl = self.font_tiny.render(status_str, True, status_col)
            self.screen.blit(art_lbl, (art_slot_rect.x + 36, art_slot_rect.y + 10))
        elif art.type == "BAG":
            self.draw_moss_bag(self.screen, art_slot_rect.x + 16, art_slot_rect.y + 16, scale=0.55)
            art_lbl = self.font_tiny.render("4 SLOTS (ENCANTADA)", True, COLOR_MOSS_LIGHT)
            self.screen.blit(art_lbl, (art_slot_rect.x + 32, art_slot_rect.y + 10))
        elif art.type == "FLASHLIGHT":
            self.draw_modern_flashlight(self.screen, art_slot_rect.x + 14, art_slot_rect.y + 16, scale=0.55, charges=art.charges)
            
            p_minus_rect = pygame.Rect(art_slot_rect.x + 30, art_slot_rect.y + 6, 16, 20)
            p_plus_rect = pygame.Rect(art_slot_rect.x + 85, art_slot_rect.y + 6, 16, 20)
            
            pygame.draw.rect(self.screen, (40, 50, 70), p_minus_rect, border_radius=2)
            pygame.draw.rect(self.screen, (40, 50, 70), p_plus_rect, border_radius=2)
            
            m_txt = self.font_tiny.render("-", True, COLOR_TEXT)
            p_txt = self.font_tiny.render("+", True, COLOR_TEXT)
            self.screen.blit(m_txt, (p_minus_rect.x + 4, p_minus_rect.y + 3))
            self.screen.blit(p_txt, (p_plus_rect.x + 3, p_plus_rect.y + 3))

            pow_txt = self.font_tiny.render(f"{art.selected_power}t ({art.charges}b)", True, COLOR_BATTERY_BAR)
            self.screen.blit(pow_txt, (art_slot_rect.x + 48, art_slot_rect.y + 10))

        pers_x = art_x + art_slot_w + 12
        pers_title = self.font_tiny.render("HABILIDADE [Q]:", True, COLOR_TEXT_MUTED)
        self.screen.blit(pers_title, (pers_x, WINDOW_HEIGHT - 85))

        skill_w = 175
        skill_rect = pygame.Rect(pers_x, WINDOW_HEIGHT - 65, skill_w, 32)
        pygame.draw.rect(self.screen, (25, 35, 50), skill_rect, border_radius=4)
        
        p = engine.player.persona
        is_ready = (p.cooldown == 0)
        s_border = COLOR_ACCENT_GREEN if is_ready else COLOR_ACCENT_RED
        pygame.draw.rect(self.screen, s_border, skill_rect, 1, border_radius=4)

        act_text = f"[Q] {p.active_name[:12]} ({'PRONTA' if is_ready else f'{p.cooldown}t'})"
        act_col = COLOR_ACCENT_GREEN if is_ready else COLOR_TEXT_MUTED
        sk_lbl = self.font_tiny.render(act_text, True, act_col)
        self.screen.blit(sk_lbl, (skill_rect.x + 8, skill_rect.y + 10))

        msg_x = pers_x + skill_w + 15
        avail_w = WINDOW_WIDTH - msg_x - 30
        if engine.log_messages:
            last_msg = engine.log_messages[-1]
            self.draw_wrapped_text(last_msg, self.font_small, COLOR_TEXT, msg_x, WINDOW_HEIGHT - 82, max_width=avail_w, max_lines=2, line_spacing=2)

        if engine.player.artifact.type == "FLASHLIGHT":
            ctrl_guide = "[1-6/Esq.] Mover | [Dir.] Feixe | [Q] Ativa | [Parado 2x] +3 Bat"
            c_col = COLOR_ACCENT_BLUE
        elif engine.player.artifact.type == "BAG":
            ctrl_guide = "[1-6] Ir | [Espaço] Trocar | [Q] Ativa | Velas: [Verde/Ciano/Púrpura/Ouro]"
            c_col = COLOR_MOSS_LIGHT
        else:
            ctrl_guide = "[1-6] Pilastra | [C/Espaço] Centro/Trocar | [Q] Ativa | [W] Esperar"
            c_col = COLOR_TEXT_DIM
            
        guide_surf = self.font_tiny.render(ctrl_guide, True, c_col)
        if guide_surf.get_width() > avail_w:
            self.draw_wrapped_text(ctrl_guide, self.font_tiny, c_col, msg_x, WINDOW_HEIGHT - 46, max_width=avail_w, max_lines=1)
        else:
            self.screen.blit(guide_surf, (msg_x, WINDOW_HEIGHT - 46))

    def draw_game_over(self, engine, mouse_pos):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 6, 12, 235))
        self.screen.blit(overlay, (0, 0))

        if engine.victory:
            t = self.time_elapsed
            glow_rad = int(320 + math.sin(t * 4.0) * 15)
            glow_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (250, 204, 21, 35), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 130), glow_rad)
            self.screen.blit(glow_surf, (0, 0))

            title_text = "VITÓRIA: RITUAL CONCLUÍDO!"
            title = self.font_title.render(title_text, True, COLOR_ENCHANT_GOLD)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 190))

            if engine.player.persona.purged_creatures >= 5:
                sub_text = "✦ Julgamento Sagrado: Todas as 5 criaturas das trevas foram purificadas e banidas!"
                sub_col = COLOR_PALADIN_GOLD
            else:
                sub_text = f"✦ Sobrevivência Sagrada: Você manteve as chamas acesas por {engine.turn} rodadas e selou a escuridão!"
                sub_col = COLOR_ACCENT_GREEN
            
            sub = self.font_mid.render(sub_text, True, sub_col)
            self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, WINDOW_HEIGHT // 2 - 135))

            stat_rect = pygame.Rect(WINDOW_WIDTH // 2 - 280, WINDOW_HEIGHT // 2 - 95, 560, 115)
            pygame.draw.rect(self.screen, (18, 26, 40), stat_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_ENCHANT_GOLD, stat_rect, 1, border_radius=8)

            diff_names = {DIFFICULTY_EASY: "Suave", DIFFICULTY_NORMAL: "Padrão", DIFFICULTY_HARD: "Noite de Horror"}
            s1 = self.font_small.render(f"• Arquétipo: {engine.player.persona.name}", True, COLOR_TEXT)
            s2 = self.font_small.render(f"• Relíquia & Bênção: {engine.player.artifact.name} | {engine.player.blessing.name}", True, COLOR_TEXT)
            s3 = self.font_small.render(f"• Rodadas Concluídas: {engine.turn} / {engine.target_victory_turns} turnos", True, COLOR_ENCHANT_GOLD)
            s4 = self.font_small.render(f"• Dificuldade: {diff_names.get(engine.difficulty, 'Padrão')} | Purificações: {engine.player.persona.purged_creatures}/5", True, COLOR_ACCENT_BLUE)

            self.screen.blit(s1, (stat_rect.x + 25, stat_rect.y + 14))
            self.screen.blit(s2, (stat_rect.x + 25, stat_rect.y + 38))
            self.screen.blit(s3, (stat_rect.x + 25, stat_rect.y + 62))
            self.screen.blit(s4, (stat_rect.x + 25, stat_rect.y + 86))

            btn_w, btn_h = 280, 44
            restart_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 40, btn_w, btn_h)
            change_art_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 95, btn_w, btn_h)
            menu_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 150, btn_w, btn_h)

            self.draw_button(restart_btn, "JOGAR NOVAMENTE", restart_btn.collidepoint(mouse_pos), primary=True)
            self.draw_button(change_art_btn, "TROCAR COMPOSIÇÃO", change_art_btn.collidepoint(mouse_pos))
            self.draw_button(menu_btn, "MENU PRINCIPAL", menu_btn.collidepoint(mouse_pos))

        else:
            title = self.font_large.render("A ESCURIDÃO CONSUMIU O SALÃO", True, COLOR_ACCENT_RED)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 130))

            sub_text = f"Você sobreviveu por {engine.turn} de {engine.target_victory_turns} turnos com {engine.player.persona.name} e {engine.player.blessing.name}."
            sub = self.font_mid.render(sub_text, True, COLOR_TEXT)
            if sub.get_width() > WINDOW_WIDTH - 80:
                self.draw_wrapped_text(sub_text, self.font_mid, COLOR_TEXT, WINDOW_WIDTH // 2 - (WINDOW_WIDTH - 80) // 2, WINDOW_HEIGHT // 2 - 75, max_width=WINDOW_WIDTH - 80)
            else:
                self.screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, WINDOW_HEIGHT // 2 - 75))

            btn_w, btn_h = 280, 46
            restart_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 - 10, btn_w, btn_h)
            change_art_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 50, btn_w, btn_h)
            menu_btn = pygame.Rect(WINDOW_WIDTH // 2 - btn_w // 2, WINDOW_HEIGHT // 2 + 110, btn_w, btn_h)

            self.draw_button(restart_btn, "REINICIAR RITUAL", restart_btn.collidepoint(mouse_pos), primary=True)
            self.draw_button(change_art_btn, "TROCAR PERSONA & ITENS", change_art_btn.collidepoint(mouse_pos))
            self.draw_button(menu_btn, "MENU PRINCIPAL", menu_btn.collidepoint(mouse_pos))
