"""
Instagram style voice processor
"""
import os
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import tempfile
from scipy import signal
from config import Config

class VoiceProcessor:
    def __init__(self):
        self.temp_dir = "temp_voices"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    async def download_voice_note(self, file_id, bot):
        """Download voice note from Telegram"""
        try:
            file = await bot.get_file(file_id)
            temp_path = os.path.join(self.temp_dir, f"voice_{file_id}.ogg")
            await file.download(destination_file=temp_path)
            return temp_path
        except Exception as e:
            print(f"Download error: {e}")
            return None
            
    async def convert_to_deep_voice(self, input_path: str, filter_type: str = "deep"):
        """Apply Instagram deep voice filter"""
        try:
            # Convert to WAV if needed
            if input_path.endswith('.ogg'):
                audio = AudioSegment.from_ogg(input_path)
                wav_path = input_path.replace('.ogg', '.wav')
                audio.export(wav_path, format='wav')
            else:
                wav_path = input_path
                
            # Load audio
            y, sr = librosa.load(wav_path, sr=44100)
            
            # Apply selected filter
            if filter_type == "deep":
                y = self._apply_instagram_filter(y, sr)
            elif filter_type == "robot":
                y = self._apply_robot_filter(y, sr)
            elif filter_type == "radio":
                y = self._apply_radio_filter(y, sr)
            elif filter_type == "echo":
                y = self._apply_echo_filter(y, sr)
            elif filter_type == "bass":
                y = self._apply_bass_boost(y, sr)
            else:
                y = self._apply_instagram_filter(y, sr)  # Default
                
            # Save processed audio
            output_wav = wav_path.replace('.wav', '_processed.wav')
            sf.write(output_wav, y, sr)
            
            # Convert to OGG for Telegram
            audio = AudioSegment.from_wav(output_wav)
            output_ogg = output_wav.replace('.wav', '.ogg')
            audio.export(output_ogg, format='ogg')
            
            # Cleanup
            self.cleanup_file(wav_path)
            self.cleanup_file(output_wav)
            
            return output_ogg
            
        except Exception as e:
            print(f"Voice processing error: {e}")
            return input_path  # Return original if fails
            
    def _apply_instagram_filter(self, y, sr):
        """Instagram trending deep voice"""
        # Pitch shift
        y = librosa.effects.pitch_shift(
            y, sr=sr, 
            n_steps=Config.VOICE_PITCH_SHIFT,
            bins_per_octave=24
        )
        
        # Time stretch
        y = librosa.effects.time_stretch(y, rate=Config.VOICE_SPEED)
        
        # Bass boost
        sos = signal.butter(4, 200, 'lowpass', fs=sr, output='sos')
        y_bass = signal.sosfilt(sos, y)
        y = y + (y_bass * (Config.VOICE_BASS_BOOST / 20))
        
        # Normalize
        y = librosa.util.normalize(y)
        
        return y
        
    def _apply_robot_filter(self, y, sr):
        """Robot voice effect"""
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=-3)
        
        # Ring modulation
        t = np.arange(len(y)) / sr
        modulator = np.sin(2 * np.pi * 50 * t)
        y = y * (1 + 0.3 * modulator)
        
        return librosa.util.normalize(y)
        
    def _apply_radio_filter(self, y, sr):
        """AM radio effect"""
        # Bandpass filter
        sos = signal.butter(4, [300, 3000], 'bandpass', fs=sr, output='sos')
        y = signal.sosfilt(sos, y)
        
        # Add noise
        noise = np.random.normal(0, 0.005, len(y))
        y = y * 0.9 + noise * 0.1
        
        return librosa.util.normalize(y)
        
    def _apply_echo_filter(self, y, sr):
        """Echo effect"""
        delay = int(0.3 * sr)  # 300ms delay
        delay_signal = np.zeros_like(y)
        delay_signal[delay:] = y[:-delay] * 0.5
        y = y + delay_signal
        
        return librosa.util.normalize(y)
        
    def _apply_bass_boost(self, y, sr):
        """Bass boost effect"""
        sos = signal.butter(4, 150, 'lowpass', fs=sr, output='sos')
        y_bass = signal.sosfilt(sos, y)
        y = y * 0.7 + y_bass * 0.3
        
        return librosa.util.normalize(y)
        
    def cleanup_file(self, file_path: str):
        """Delete temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
            
    def cleanup_all(self):
        """Cleanup all temp files"""
        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except:
                pass
