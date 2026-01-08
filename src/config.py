"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Your task-specific configuration.
    
    CUSTOMIZE THIS CLASS to add your task's hyperparameters.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════

    domain: str = Field(default="symbol_reordering")
    image_size: tuple[int, int] = Field(default=(800, 200))

    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════

    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )

    video_fps: int = Field(
        default=15,
        description="Video frame rate"
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS - Symbol Reordering
    # ══════════════════════════════════════════════════════════════════════════

    # NOTE: For scaling to 10K+ samples, the generator now randomizes these
    # parameters per-task rather than using fixed config values:
    # - symbol_type: randomly chosen from ['shapes', 'letters', 'numbers', 'colors', 'mixed']
    # - num_symbols: randomly chosen from range 3-8
    # - use_labels: randomly chosen True/False
    # This increases unique combinations from 6,664 to 309+ million

    symbol_type: str = Field(
        default="shapes",
        description="[DEPRECATED - now randomized per task] Type of symbols to use"
    )

    num_symbols: int = Field(
        default=5,
        description="[DEPRECATED - now randomized per task] Number of symbols (3-8)"
    )

    symbol_size: int = Field(
        default=80,
        description="Size of each symbol in pixels"
    )

    symbol_spacing: int = Field(
        default=120,
        description="Horizontal spacing between symbols"
    )

    use_labels: bool = Field(
        default=True,
        description="[DEPRECATED - now randomized per task] Whether to show position labels"
    )
