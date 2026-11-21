import wave
import struct
import math
import random
from pathlib import Path

def generate_ambient_synth(output_path: Path, duration_s: float = 8.0, sample_rate: int = 44100):
    n_samples = int(duration_s * sample_rate)
    
    # Chord frequencies (e.g. D minor 9: D3, F3, A3, C4, E4)
    # D3=146.83, F3=174.61, A3=220.00, C4=261.63, E4=329.63, A4=440.00
    chords = [
        [146.83, 220.00, 261.63, 329.63], # Dm9
        [130.81, 196.00, 261.63, 329.63], # Cmaj7
        [116.54, 174.61, 220.00, 293.66], # Bbmaj7
        [110.00, 164.81, 220.00, 261.63], # Am7
    ]
    chord = random.choice(chords)
    
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        # Envelope: soft attack and long decay
        env = min(1.0, t / 1.5) * max(0.0, 1.0 - (t / duration_s))
        
        sample = 0.0
        # Multi-oscillator pad with gentle chorusing/detuning
        for idx, freq in enumerate(chord):
            detune = 1.0 + 0.002 * math.sin(t * 0.8 + idx)
            # Fundamental + soft harmonics
            w1 = math.sin(2 * math.pi * (freq * detune) * t)
            w2 = 0.4 * math.sin(2 * math.pi * (freq * 2.0 * detune) * t)
            # Kuramoto-style modulation
            mod = 0.2 * math.sin(2 * math.pi * 3.5 * t + idx)
            sample += (w1 + w2 + mod) * (0.25 / len(chord))
        
        # Sub-bass warmth
        sub = 0.15 * math.sin(2 * math.pi * (chord[0] / 2.0) * t)
        sample = (sample + sub) * env
        
        # Clip to -1.0 .. 1.0
        sample = max(-0.95, min(0.95, sample))
        int_sample = int(sample * 32767.0)
        samples.append(int_sample)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), 'wb') as wav_file:
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        packed = struct.pack(f'<{len(samples)}h', *samples)
        wav_file.writeframes(packed)
    
    print(f"Synthesized ambient audio: {output_path} ({len(samples)} samples, {duration_s}s)")

if __name__ == "__main__":
    out = Path("artifacts/art/test_synth.wav")
    generate_ambient_synth(out)
