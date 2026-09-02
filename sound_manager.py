import array
import math
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        self.sounds = {}
        self.ambient_channel = None
        self.current_ambient = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(12)
            self.ambient_channel = pygame.mixer.Channel(7)
            self.generate_sounds()
            self.apply_volume()
        except Exception:
            self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_weather_ambient()

    def set_muted(self, is_muted):
        self.enabled = not is_muted
        if not self.enabled:
            self.stop_weather_ambient()

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        self.apply_volume()

    def change_volume(self, delta):
        self.set_volume(self.volume + delta)

    def apply_volume(self):
        for s in self.sounds.values():
            s.set_volume(self.volume)
        if self.ambient_channel:
            self.ambient_channel.set_volume(self.volume * 0.45)

    def start_weather_ambient(self, weather_type):
        if not self.enabled or self.ambient_channel is None:
            return

        if weather_type == "THUNDERSTORM":
            snd_name = "heavy_rain_loop"
        elif weather_type == "BLOOD_RAIN":
            snd_name = "blood_rain_loop"
        else:
            self.stop_weather_ambient()
            return

        if self.current_ambient == snd_name and self.ambient_channel.get_busy():
            return

        snd = self.sounds.get(snd_name)
        if snd:
            self.current_ambient = snd_name
            self.ambient_channel.play(snd, loops=-1, fade_ms=700)
            self.ambient_channel.set_volume(self.volume * 0.45)

    def stop_weather_ambient(self):
        if self.ambient_channel and self.ambient_channel.get_busy():
            self.ambient_channel.fadeout(500)
        self.current_ambient = None

    def play(self, name):
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def create_sound(self, samples):
        buf = array.array('h', samples)
        snd = pygame.mixer.Sound(buffer=buf.tobytes())
        snd.set_volume(self.volume)
        return snd

    def generate_sounds(self):
        sr = 44100

        def square_wave(freq, duration, decay=True):
            samples = []
            num_samples = int(sr * duration)
            period = sr / max(1.0, freq)
            for i in range(num_samples):
                vol = 1.0 - (i / num_samples) if decay else 1.0
                val = 7000 if (i % period) < (period / 2) else -7000
                samples.append(int(val * vol))
            return samples

        def sawtooth_wave(freq_start, freq_end, duration):
            samples = []
            num_samples = int(sr * duration)
            phase = 0.0
            for i in range(num_samples):
                t = i / num_samples
                freq = freq_start + (freq_end - freq_start) * t
                phase += freq / sr
                if phase >= 1.0:
                    phase -= 1.0
                vol = (1.0 - t) * 0.8
                val = int((2.0 * phase - 1.0) * 8000 * vol)
                samples.append(val)
            return samples

        def noise_burst(duration):
            import random
            samples = []
            num_samples = int(sr * duration)
            for i in range(num_samples):
                vol = (1.0 - (i / num_samples)) ** 2
                val = int(random.uniform(-9000, 9000) * vol)
                samples.append(val)
            return samples

        def chord(freqs, duration):
            samples = []
            num_samples = int(sr * duration)
            for i in range(num_samples):
                vol = 1.0 - (i / num_samples)
                s_sum = 0
                for f in freqs:
                    period = sr / f
                    val = 3000 if (i % period) < (period / 2) else -3000
                    s_sum += val
                samples.append(int(s_sum * vol))
            return samples

        hover_samples = []
        h_dur = 0.025
        h_samples_count = int(sr * h_dur)
        for i in range(h_samples_count):
            t = i / h_samples_count
            freq = 950 + 150 * t
            period = sr / freq
            vol = math.sin(t * math.pi) * 0.45
            val = 4000 if (i % period) < (period / 2) else -4000
            hover_samples.append(int(val * vol))
        self.sounds["menu_hover"] = self.create_sound(hover_samples)

        s_move = square_wave(440, 0.04)
        self.sounds["menu_move"] = self.create_sound(s_move)

        s_sel = square_wave(587.33, 0.04) + square_wave(880, 0.08)
        self.sounds["menu_select"] = self.create_sound(s_sel)

        s_light = noise_burst(0.05) + square_wave(520, 0.08)
        self.sounds["candle_light"] = self.create_sound(s_light)

        s_out = sawtooth_wave(400, 110, 0.25)
        self.sounds["candle_out"] = self.create_sound(s_out)

        s_flash = noise_burst(0.18) + square_wave(1200, 0.05)
        self.sounds["flash"] = self.create_sound(s_flash)

        s_cross = chord([440, 554.37, 659.25], 0.35)
        self.sounds["divine_cross"] = self.create_sound(s_cross)

        s_beam = sawtooth_wave(200, 900, 0.12)
        self.sounds["beam"] = self.create_sound(s_beam)

        s_over = chord([300, 280], 0.15) + chord([250, 230], 0.15) + chord([200, 180], 0.35)
        self.sounds["game_over"] = self.create_sound(s_over)

        # Deep low-frequency tactile impact rumble
        s_impact = sawtooth_wave(85, 32, 0.22) + square_wave(45, 0.18)
        self.sounds["screen_impact"] = self.create_sound(s_impact)

        # Thunder strike: Crackle noise burst followed by deep booming rumble
        import random
        t_samples = []
        t_dur = 0.85
        t_num = int(sr * t_dur)
        for i in range(t_num):
            t = i / t_num
            crackle = random.uniform(-10000, 10000) * math.exp(-t * 22.0)
            rumble_freq = 55.0 - t * 25.0
            rumble = math.sin(2.0 * math.pi * rumble_freq * (i / sr)) * 9000.0 * ((1.0 - t) ** 1.8)
            roll = random.uniform(-4000, 4000) * math.sin(t * 15.0) * math.exp(-t * 3.0)
            val = int(max(-32767, min(32767, crackle + rumble + roll)))
            t_samples.append(val)
        self.sounds["thunder_strike"] = self.create_sound(t_samples)

        # Wind gust for gale storms
        w_samples = []
        w_dur = 0.45
        w_num = int(sr * w_dur)
        for i in range(w_num):
            t = i / w_num
            env = math.sin(t * math.pi)
            noise = random.uniform(-6000, 6000)
            val = int(noise * env * 0.75)
            w_samples.append(val)
        self.sounds["wind_gust"] = self.create_sound(w_samples)

        # Blood strike: Guttural creature roar & ominous blood surge
        b_samples = []
        b_dur = 0.70
        b_num = int(sr * b_dur)
        for i in range(b_num):
            t = i / b_num
            freq = 180.0 * (1.0 - t * 0.6) + math.sin(t * 40.0) * 25.0
            screech = (2.0 * ((i * freq / sr) % 1.0) - 1.0) * 11000.0 * math.exp(-t * 3.5)
            roar = math.sin(2.0 * math.pi * 50.0 * (i / sr)) * 12000.0 * ((1.0 - t) ** 1.5)
            val = int(max(-32767, min(32767, screech + roar)))
            b_samples.append(val)
        self.sounds["blood_strike"] = self.create_sound(b_samples)

        # Procedural Looping Rain Ambience Synthesizer (Tempestade de Trovões)
        rain_dur = 2.5
        rain_len = int(sr * rain_dur)
        rain_buffer = [0.0] * rain_len

        # Layer 1: Filtered continuous rushing rain wash
        prev_n = 0.0
        for i in range(rain_len):
            raw_n = random.uniform(-2500, 2500)
            prev_n = prev_n * 0.70 + raw_n * 0.30
            t_frac = i / rain_len
            mod_wind = 0.85 + 0.15 * math.sin(2.0 * math.pi * 0.4 * t_frac)
            rain_buffer[i] += prev_n * mod_wind

        # Layer 2: Individual raindrop impacts and glass/stone patters
        num_drops = 380
        for _ in range(num_drops):
            drop_start = random.randint(0, rain_len - 800)
            drop_freq = random.uniform(900.0, 2400.0)
            drop_amp = random.uniform(1800.0, 4800.0)
            decay_rate = random.uniform(180.0, 320.0)
            for di in range(min(700, rain_len - drop_start)):
                dt_sec = di / sr
                drop_val = math.sin(2.0 * math.pi * drop_freq * dt_sec) * drop_amp * math.exp(-dt_sec * decay_rate)
                rain_buffer[drop_start + di] += drop_val

        # Layer 3: Seamless boundary crossfade
        xfade_len = 2200
        for xi in range(xfade_len):
            xfade_ratio = xi / float(xfade_len)
            start_val = rain_buffer[xi]
            end_val = rain_buffer[rain_len - xfade_len + xi]
            blended = start_val * xfade_ratio + end_val * (1.0 - xfade_ratio)
            rain_buffer[xi] = blended
            rain_buffer[rain_len - xfade_len + xi] = blended

        rain_samples = [int(max(-32767, min(32767, v))) for v in rain_buffer]
        self.sounds["heavy_rain_loop"] = self.create_sound(rain_samples)

        # Procedural Blood Rain Loop (Chuva de Sangue)
        blood_buffer = [0.0] * rain_len
        prev_bn = 0.0
        for i in range(rain_len):
            raw_bn = random.uniform(-2200, 2200)
            prev_bn = prev_bn * 0.82 + raw_bn * 0.18
            drone = math.sin(2.0 * math.pi * 55.0 * (i / sr)) * 1400.0
            blood_buffer[i] += prev_bn + drone

        num_blood_drops = 220
        for _ in range(num_blood_drops):
            drop_start = random.randint(0, rain_len - 1200)
            drop_freq = random.uniform(320.0, 850.0)
            drop_amp = random.uniform(2200.0, 5200.0)
            decay_rate = random.uniform(90.0, 160.0)
            for di in range(min(1100, rain_len - drop_start)):
                dt_sec = di / sr
                drop_val = math.sin(2.0 * math.pi * drop_freq * dt_sec) * drop_amp * math.exp(-dt_sec * decay_rate)
                blood_buffer[drop_start + di] += drop_val

        for xi in range(xfade_len):
            xfade_ratio = xi / float(xfade_len)
            start_val = blood_buffer[xi]
            end_val = blood_buffer[rain_len - xfade_len + xi]
            blended = start_val * xfade_ratio + end_val * (1.0 - xfade_ratio)
            blood_buffer[xi] = blended
            blood_buffer[rain_len - xfade_len + xi] = blended

        blood_samples = [int(max(-32767, min(32767, v))) for v in blood_buffer]
        self.sounds["blood_rain_loop"] = self.create_sound(blood_samples)
