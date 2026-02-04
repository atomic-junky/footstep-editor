"""Data models for footstep sounds and projects."""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class SurfaceType(Enum):
    """Types of surfaces for footstep sounds."""
    CONCRETE = "concrete"
    GRASS = "grass"
    WOOD = "wood"
    METAL = "metal"
    CARPET = "carpet"
    GRAVEL = "gravel"
    SNOW = "snow"
    MUD = "mud"


class FootstepType(Enum):
    """Types of footsteps."""
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    LAND = "land"
    STEP = "step"


@dataclass
class FootstepSound:
    """Represents a single footstep sound configuration."""
    
    name: str
    surface: SurfaceType
    footstep_type: FootstepType
    
    # Parameters
    frequency: float = 440.0  # Hz
    duration: float = 0.5  # seconds
    intensity: float = 0.7  # 0-1
    pitch: float = 1.0  # pitch multiplier
    
    # Advanced parameters
    reverb_amount: float = 0.2  # 0-1
    compression: float = 0.5  # 0-1
    eq_bass: float = 0.0  # dB
    eq_mid: float = 0.0  # dB
    eq_treble: float = 0.0  # dB
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Ensure all parameters are within valid ranges."""
        self.intensity = max(0.0, min(1.0, self.intensity))
        self.pitch = max(0.1, self.pitch)
        self.duration = max(0.1, self.duration)
        self.reverb_amount = max(0.0, min(1.0, self.reverb_amount))
        self.compression = max(0.0, min(1.0, self.compression))


@dataclass
class FootstepProject:
    """Represents a complete footstep project."""
    
    name: str
    description: str = ""
    
    # List of sounds in the project
    sounds: List[FootstepSound] = field(default_factory=list)
    
    # Project settings
    sample_rate: int = 44100  # Hz
    bit_depth: int = 16  # bits
    channels: int = 2  # mono or stereo
    
    def add_sound(self, sound: FootstepSound) -> None:
        """Add a sound to the project."""
        self.sounds.append(sound)
    
    def remove_sound(self, sound: FootstepSound) -> None:
        """Remove a sound from the project."""
        if sound in self.sounds:
            self.sounds.remove(sound)
    
    def get_sound_by_name(self, name: str) -> FootstepSound | None:
        """Get a sound by its name."""
        for sound in self.sounds:
            if sound.name == name:
                return sound
        return None
