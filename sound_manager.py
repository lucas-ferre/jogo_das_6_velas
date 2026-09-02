import array
import math
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.generate_sounds()
            self.apply_volume()
        except Exception:
            self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def set_muted(self, is_muted):
        self.enabled = not is_muted

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        self.apply_volume()

    def change_volume(self, delta):
        self.set_volume(self.volume + delta)

    def apply_volume(self):
        for s in self.sounds.values():
            s.set_volume(self.volume)

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
