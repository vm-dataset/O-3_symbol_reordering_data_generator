"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SYMBOL REORDERING TASK GENERATOR                           ║
║                                                                               ║
║  Generates symbol reordering tasks where symbols must be rearranged          ║
║  from an initial sequence to a target sequence.                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import math

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Symbol Reordering Task Generator.

    Generates tasks where symbols need to be rearranged from an initial
    sequence to a target sequence. The task has a unique solution.
    """

    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)

        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")

        # Symbol definitions
        self._init_symbol_sets()

    def _init_symbol_sets(self):
        """Initialize different types of symbol sets."""
        self.symbol_sets = {
            "letters": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "numbers": list("0123456789"),
            "shapes": ["circle", "square", "triangle", "diamond", "star", "pentagon", "hexagon", "heart"],
            "colors": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"],
        }

        # Color definitions
        self.color_map = {
            "red": (220, 50, 50),
            "blue": (50, 120, 220),
            "green": (50, 180, 50),
            "yellow": (240, 200, 50),
            "purple": (160, 50, 200),
            "orange": (255, 140, 50),
            "pink": (255, 120, 180),
            "cyan": (50, 200, 200),
        }

    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one symbol reordering task pair."""

        # Generate task data
        task_data = self._generate_task_data()

        # Render images
        first_image = self._render_state(task_data["initial_sequence"], task_data)
        final_image = self._render_state(task_data["target_sequence"], task_data)

        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(task_data, task_id)

        # Select prompt based on whether labels are used in this specific task
        prompt_type = "with_labels" if task_data.get("use_labels", True) else "default"
        prompt = get_prompt(prompt_type)

        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  TASK GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_task_data(self) -> dict:
        """Generate symbol reordering task data."""
        # RANDOMIZE num_symbols for each task (3-8 symbols)
        # This dramatically increases combinatorial space for scaling to 10K+ samples
        num_symbols = random.randint(3, 8)

        # RANDOMIZE symbol_type for each task (not from config)
        # This increases variety from 6,664 to 309+ million unique combinations
        symbol_type = random.choice(["shapes", "letters", "numbers", "colors", "mixed"])

        # Generate symbols based on randomly selected type
        if symbol_type == "mixed":
            # Mix different types
            symbols = self._generate_mixed_symbols(num_symbols)
        else:
            # Use single type
            available_symbols = self.symbol_sets.get(symbol_type, self.symbol_sets["shapes"])
            symbols = random.sample(available_symbols, min(num_symbols, len(available_symbols)))

        # Create initial sequence (0, 1, 2, 3, ...)
        initial_sequence = list(range(num_symbols))

        # Create target sequence (shuffled, but different from initial)
        target_sequence = list(range(num_symbols))
        attempts = 0
        while target_sequence == initial_sequence and attempts < 100:
            random.shuffle(target_sequence)
            attempts += 1

        # Ensure they are different
        if target_sequence == initial_sequence:
            # Force a swap
            if num_symbols >= 2:
                target_sequence[0], target_sequence[1] = target_sequence[1], target_sequence[0]

        # RANDOMIZE whether to show position labels (adds more variety)
        use_labels = random.choice([True, False])

        return {
            "symbols": symbols,
            "symbol_type": symbol_type,
            "initial_sequence": initial_sequence,
            "target_sequence": target_sequence,
            "num_symbols": num_symbols,
            "use_labels": use_labels,
        }

    def _generate_mixed_symbols(self, num_symbols: int) -> List[str]:
        """Generate mixed symbol types."""
        all_symbols = []
        for symbol_set in ["letters", "numbers", "shapes"]:
            all_symbols.extend(self.symbol_sets[symbol_set][:3])

        return random.sample(all_symbols, min(num_symbols, len(all_symbols)))

    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING
    # ══════════════════════════════════════════════════════════════════════════

    def _render_state(self, sequence: List[int], task_data: dict) -> Image.Image:
        """Render a state with symbols in the given sequence."""
        width, height = self.config.image_size
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        symbols = task_data["symbols"]
        num_symbols = len(symbols)
        symbol_size = self.config.symbol_size
        spacing = self.config.symbol_spacing

        # Calculate starting x position to center the symbols
        total_width = (num_symbols - 1) * spacing + symbol_size
        start_x = (width - total_width) // 2
        center_y = height // 2

        # Draw each symbol in the sequence
        for position_idx, symbol_idx in enumerate(sequence):
            x = start_x + position_idx * spacing
            y = center_y - symbol_size // 2

            symbol = symbols[symbol_idx]
            self._draw_symbol(draw, symbol, x, y, symbol_size, task_data["symbol_type"])

            # Draw position label if enabled for this task
            if task_data.get("use_labels", True):
                label = str(position_idx)
                self._draw_label(draw, label, x + symbol_size // 2, y + symbol_size + 10)

        return img

    def _draw_symbol(self, draw: ImageDraw.Draw, symbol: str, x: int, y: int,
                     size: int, symbol_type: str):
        """Draw a single symbol."""
        center_x = x + size // 2
        center_y = y + size // 2

        if symbol_type == "letters" or (symbol_type == "mixed" and symbol.isalpha() and len(symbol) == 1):
            self._draw_letter(draw, symbol, center_x, center_y, size)

        elif symbol_type == "numbers" or (symbol_type == "mixed" and symbol.isdigit()):
            self._draw_number(draw, symbol, center_x, center_y, size)

        elif symbol_type == "colors":
            self._draw_color_square(draw, symbol, x, y, size)

        else:  # shapes or mixed shapes
            self._draw_shape(draw, symbol, center_x, center_y, size)

    def _draw_letter(self, draw: ImageDraw.Draw, letter: str, center_x: int,
                     center_y: int, size: int):
        """Draw a letter symbol."""
        # Draw circle background
        radius = size // 2
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=(100, 150, 250),
            outline=(50, 100, 200),
            width=3
        )

        # Draw letter
        font_size = int(size * 0.5)
        font = self._get_font(font_size)
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        draw.text((text_x, text_y), letter, fill=(255, 255, 255), font=font)

    def _draw_number(self, draw: ImageDraw.Draw, number: str, center_x: int,
                     center_y: int, size: int):
        """Draw a number symbol."""
        # Draw square background
        half_size = size // 2
        draw.rectangle(
            [center_x - half_size, center_y - half_size,
             center_x + half_size, center_y + half_size],
            fill=(250, 150, 100),
            outline=(200, 100, 50),
            width=3
        )

        # Draw number
        font_size = int(size * 0.5)
        font = self._get_font(font_size)
        bbox = draw.textbbox((0, 0), number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        draw.text((text_x, text_y), number, fill=(255, 255, 255), font=font)

    def _draw_color_square(self, draw: ImageDraw.Draw, color_name: str,
                          x: int, y: int, size: int):
        """Draw a colored square."""
        color = self.color_map.get(color_name, (128, 128, 128))
        draw.rectangle([x, y, x + size, y + size], fill=color, outline=(0, 0, 0), width=2)

    def _draw_shape(self, draw: ImageDraw.Draw, shape: str, center_x: int,
                    center_y: int, size: int):
        """Draw a geometric shape."""
        radius = size // 2

        if shape == "circle":
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                fill=(100, 200, 100),
                outline=(50, 150, 50),
                width=3
            )

        elif shape == "square":
            draw.rectangle(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                fill=(200, 100, 100),
                outline=(150, 50, 50),
                width=3
            )

        elif shape == "triangle":
            points = [
                (center_x, center_y - radius),
                (center_x - radius, center_y + radius),
                (center_x + radius, center_y + radius)
            ]
            draw.polygon(points, fill=(150, 100, 200), outline=(100, 50, 150), width=3)

        elif shape == "diamond":
            points = [
                (center_x, center_y - radius),
                (center_x + radius, center_y),
                (center_x, center_y + radius),
                (center_x - radius, center_y)
            ]
            draw.polygon(points, fill=(200, 200, 100), outline=(150, 150, 50), width=3)

        elif shape == "star":
            self._draw_star(draw, center_x, center_y, radius)

        elif shape == "pentagon":
            self._draw_regular_polygon(draw, center_x, center_y, radius, 5,
                                      fill=(100, 150, 200), outline=(50, 100, 150))

        elif shape == "hexagon":
            self._draw_regular_polygon(draw, center_x, center_y, radius, 6,
                                      fill=(200, 150, 100), outline=(150, 100, 50))

        elif shape == "heart":
            self._draw_heart(draw, center_x, center_y, radius)

    def _draw_star(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Draw a 5-pointed star."""
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            r = radius if i % 2 == 0 else radius * 0.4
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points.append((x, y))

        draw.polygon(points, fill=(255, 200, 50), outline=(200, 150, 0), width=3)

    def _draw_regular_polygon(self, draw: ImageDraw.Draw, center_x: int, center_y: int,
                             radius: int, num_sides: int, fill: Tuple, outline: Tuple):
        """Draw a regular polygon."""
        points = []
        for i in range(num_sides):
            angle = math.pi * 2 * i / num_sides - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        draw.polygon(points, fill=fill, outline=outline, width=3)

    def _draw_heart(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Draw a heart shape."""
        # Simplified heart using circles and triangle
        r = radius // 2
        # Two circles at top
        draw.ellipse([center_x - radius, center_y - r, center_x, center_y + r],
                    fill=(255, 100, 150), outline=(200, 50, 100), width=2)
        draw.ellipse([center_x, center_y - r, center_x + radius, center_y + r],
                    fill=(255, 100, 150), outline=(200, 50, 100), width=2)
        # Triangle at bottom
        points = [
            (center_x - radius, center_y),
            (center_x + radius, center_y),
            (center_x, center_y + radius)
        ]
        draw.polygon(points, fill=(255, 100, 150), outline=(200, 50, 100))

    def _draw_label(self, draw: ImageDraw.Draw, text: str, center_x: int, y: int):
        """Draw a position label."""
        font = self._get_font(20)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        text_x = center_x - text_width // 2
        draw.text((text_x, y), text, fill=(80, 80, 80), font=font)

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font for rendering text."""
        font_names = [
            "Arial.ttf",
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]

        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, size)
            except (OSError, IOError):
                continue

        return ImageFont.load_default()

    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_video(self, task_data: dict, task_id: str) -> str:
        """Generate animation video showing symbol reordering."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"

        # Create animation frames
        frames = self._create_reordering_animation(task_data)

        if frames:
            result = self.video_generator.create_video_from_frames(frames, video_path)
            return str(result) if result else None

        return None

    def _create_reordering_animation(
        self,
        task_data: dict,
        hold_frames: int = 10,
        transition_frames: int = 30
    ) -> List[Image.Image]:
        """
        Create animation frames showing symbols moving from initial to target positions.
        """
        frames = []

        initial_sequence = task_data["initial_sequence"]
        target_sequence = task_data["target_sequence"]
        symbols = task_data["symbols"]
        num_symbols = len(symbols)

        # Calculate positions
        width, height = self.config.image_size
        symbol_size = self.config.symbol_size
        spacing = self.config.symbol_spacing

        total_width = (num_symbols - 1) * spacing + symbol_size
        start_x = (width - total_width) // 2
        center_y = height // 2

        # Initial state - hold
        initial_img = self._render_state(initial_sequence, task_data)
        for _ in range(hold_frames):
            frames.append(initial_img.copy())

        # Create mapping from symbol to target position
        symbol_to_target_pos = {}
        for target_pos, symbol_idx in enumerate(target_sequence):
            symbol_to_target_pos[symbol_idx] = target_pos

        # Transition frames - animate each symbol moving
        for frame_idx in range(transition_frames):
            progress = frame_idx / (transition_frames - 1) if transition_frames > 1 else 1.0

            # Create frame
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Draw each symbol at interpolated position
            for initial_pos, symbol_idx in enumerate(initial_sequence):
                target_pos = symbol_to_target_pos[symbol_idx]

                # Calculate current position (interpolate between initial and target)
                initial_x = start_x + initial_pos * spacing
                target_x = start_x + target_pos * spacing
                current_x = int(initial_x + (target_x - initial_x) * progress)

                y = center_y - symbol_size // 2

                symbol = symbols[symbol_idx]
                self._draw_symbol(draw, symbol, current_x, y, symbol_size,
                                task_data["symbol_type"])

                # Draw position labels if enabled for this task
                if task_data.get("use_labels", True):
                    # Show target position label
                    label = str(target_pos)
                    self._draw_label(draw, label, current_x + symbol_size // 2,
                                   y + symbol_size + 10)

            frames.append(img)

        # Final state - hold
        final_img = self._render_state(target_sequence, task_data)
        for _ in range(hold_frames):
            frames.append(final_img.copy())

        return frames
