"""
Sound system for chess moves
"""
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput


class ChessSoundManager:
    """Manager for chess game sounds"""
    
    def __init__(self):
        self.sounds_enabled = True
        self.volume = 0.7
        
        # Create sounds directory
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Sound effects using QSoundEffect (better for short sounds)
        self.move_sound = QSoundEffect()
        self.capture_sound = QSoundEffect()
        self.check_sound = QSoundEffect()
        self.castle_sound = QSoundEffect()
        self.game_end_sound = QSoundEffect()
        
        # Initialize sounds
        self._init_sounds()
        
    def _init_sounds(self):
        """Initialize sound effects"""
        # Set volume for all sounds
        self.move_sound.setVolume(self.volume)
        self.capture_sound.setVolume(self.volume)
        self.check_sound.setVolume(self.volume)
        self.castle_sound.setVolume(self.volume)
        self.game_end_sound.setVolume(self.volume)
        
        # Try to load sound files if they exist
        # Otherwise we'll generate simple beeps or use system sounds
        move_file = self.sounds_dir / "move.wav"
        capture_file = self.sounds_dir / "capture.wav"
        check_file = self.sounds_dir / "check.wav"
        castle_file = self.sounds_dir / "castle.wav"
        end_file = self.sounds_dir / "game_end.wav"
        
        if move_file.exists():
            self.move_sound.setSource(QUrl.fromLocalFile(str(move_file.absolute())))
        if capture_file.exists():
            self.capture_sound.setSource(QUrl.fromLocalFile(str(capture_file.absolute())))
        if check_file.exists():
            self.check_sound.setSource(QUrl.fromLocalFile(str(check_file.absolute())))
        if castle_file.exists():
            self.castle_sound.setSource(QUrl.fromLocalFile(str(castle_file.absolute())))
        if end_file.exists():
            self.game_end_sound.setSource(QUrl.fromLocalFile(str(end_file.absolute())))
            
        # Generate default sounds if files don't exist
        if not move_file.exists():
            self._generate_default_sounds()
            
    def _generate_default_sounds(self):
        """Generate default sound files using simple tones"""
        try:
            import numpy as np
            import wave
            
            sample_rate = 44100
            
            def generate_tone(frequency, duration, filename):
                """Generate a simple tone and save as WAV"""
                t = np.linspace(0, duration, int(sample_rate * duration))
                # Generate sine wave
                audio = np.sin(2 * np.pi * frequency * t)
                # Add envelope to avoid clicks
                envelope = np.exp(-3 * t / duration)
                audio = audio * envelope
                # Convert to 16-bit PCM
                audio = (audio * 32767).astype(np.int16)
                
                # Save as WAV
                filepath = self.sounds_dir / filename
                with wave.open(str(filepath), 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio.tobytes())
                    
                return filepath
                
            # Generate different tones
            move_path = generate_tone(440, 0.1, "move.wav")  # A4 note, short
            capture_path = generate_tone(330, 0.15, "capture.wav")  # E4 note, longer
            check_path = generate_tone(880, 0.2, "check.wav")  # A5 note, alert
            castle_path = generate_tone(523, 0.15, "castle.wav")  # C5 note
            end_path = generate_tone(262, 0.3, "game_end.wav")  # C4 note, long
            
            # Load the generated sounds
            self.move_sound.setSource(QUrl.fromLocalFile(str(move_path.absolute())))
            self.capture_sound.setSource(QUrl.fromLocalFile(str(capture_path.absolute())))
            self.check_sound.setSource(QUrl.fromLocalFile(str(check_path.absolute())))
            self.castle_sound.setSource(QUrl.fromLocalFile(str(castle_path.absolute())))
            self.game_end_sound.setSource(QUrl.fromLocalFile(str(end_path.absolute())))
            
        except ImportError:
            # numpy not available, skip sound generation
            print("NumPy not available, sounds will be silent")
        except Exception as e:
            print(f"Error generating sounds: {e}")
            
    def play_move(self):
        """Play normal move sound"""
        if self.sounds_enabled and self.move_sound.source().isValid():
            self.move_sound.play()
            
    def play_capture(self):
        """Play capture sound"""
        if self.sounds_enabled and self.capture_sound.source().isValid():
            self.capture_sound.play()
            
    def play_check(self):
        """Play check sound"""
        if self.sounds_enabled and self.check_sound.source().isValid():
            self.check_sound.play()
            
    def play_castle(self):
        """Play castling sound"""
        if self.sounds_enabled and self.castle_sound.source().isValid():
            self.castle_sound.play()
            
    def play_game_end(self):
        """Play game end sound"""
        if self.sounds_enabled and self.game_end_sound.source().isValid():
            self.game_end_sound.play()
            
    def set_enabled(self, enabled: bool):
        """Enable or disable sounds"""
        self.sounds_enabled = enabled
        
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self.move_sound.setVolume(self.volume)
        self.capture_sound.setVolume(self.volume)
        self.check_sound.setVolume(self.volume)
        self.castle_sound.setVolume(self.volume)
        self.game_end_sound.setVolume(self.volume)
        
    def is_enabled(self) -> bool:
        """Check if sounds are enabled"""
        return self.sounds_enabled
        
    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume


# Singleton instance
_sound_manager: Optional[ChessSoundManager] = None


def get_sound_manager() -> ChessSoundManager:
    """Get the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = ChessSoundManager()
    return _sound_manager

