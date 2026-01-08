# Symbol Reordering Data Generator 🔄

A synthetic data generator for symbol reordering tasks. Generates visual reasoning tasks where symbols must be rearranged from an initial sequence to a target sequence.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/symbol-reordering-generator.git
cd symbol-reordering-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
symbol-reordering-generator/
├── core/                    # Framework utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # Symbol reordering task logic
│   ├── generator.py        # Symbol reordering generator
│   ├── prompts.py          # Task prompt templates
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Each generated task includes:

```
data/questions/symbol_reordering_task/{task_id}/
├── first_frame.png          # Initial symbol arrangement
├── final_frame.png          # Target symbol arrangement
├── prompt.txt               # Task instructions
└── ground_truth.mp4         # Animation showing symbol movements
```

**Example:**
- Initial: ⭐ ▲ ◆ ⬡ ⬟ (positions 0-4)
- Target:  ◆ ⬟ ⭐ ⬡ ▲ (positions 0-4)
- Video: Smooth animation of symbols moving to target positions

---

## ⚙️ Configuration

Customize task generation in `src/config.py`:

```python
class TaskConfig(GenerationConfig):
    domain: str = "symbol_reordering"
    image_size: tuple[int, int] = (800, 200)

    # Symbol settings - NOTE: For scaling to 10K+ samples, the generator
    # automatically randomizes these per-task:
    # - symbol_type: randomly chosen from ['shapes', 'letters', 'numbers', 'colors', 'mixed']
    # - num_symbols: randomly chosen from range 3-8
    # - use_labels: randomly chosen True/False
    symbol_size: int = 80        # Symbol size in pixels
    symbol_spacing: int = 120    # Horizontal spacing

    # Video settings
    generate_videos: bool = True
    video_fps: int = 15
```

### 🔢 Scaling Capability

The generator can scale to **309+ million unique combinations** by randomizing:
- **Symbol type** (5 options: shapes, letters, numbers, colors, mixed)
- **Number of symbols** (6 options: 3-8 symbols)
- **Symbol selection** from pool (shapes: 8, letters: 26, numbers: 10, colors: 8)
- **Target permutation** (n! - 1 permutations for n symbols)
- **Position labels** (2 options: shown or hidden)

This ensures sufficient diversity for generating 10K+ unique samples without repetition.

## 🎨 Symbol Types

- **`shapes`**: circle, square, triangle, diamond, star, pentagon, hexagon, heart
- **`letters`**: A-Z (rendered in colored circles)
- **`numbers`**: 0-9 (rendered in colored squares)
- **`colors`**: red, blue, green, yellow, purple, orange, pink, cyan (colored squares)
- **`mixed`**: Random combination of different types

## 📊 Usage Examples

```bash
# Generate 100 shape-based tasks
python examples/generate.py --num-samples 100

# Generate with specific seed (reproducible)
python examples/generate.py --num-samples 50 --seed 42

# Generate without videos (faster)
python examples/generate.py --num-samples 50 --no-videos

# Custom output directory
python examples/generate.py --num-samples 50 --output data/my_tasks
```

## 🔧 Advanced Customization

Edit the configuration file to change symbol types:

```python
# In src/config.py, modify:
symbol_type: str = Field(default="letters")  # Use letters instead of shapes
num_symbols: int = Field(default=7)          # Use 7 symbols instead of 5
use_labels: bool = Field(default=False)      # Hide position labels
```