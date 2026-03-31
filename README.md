# Canvas Organizer

A tool to organize **Canvas LMS** student submission files.

Useful for instructors and TAs working with bulk Canvas downloads.

It automatically:
- Creates one folder per student (e.g. `davola_joe`, `costanza_george`, `kramercosmo`)
- Cleans filenames by removing Canvas metadata and long numeric IDs
- Preserves the student's actual submitted filename as much as possible
- Moves files into organized folders (no copies created)
- Supports dry-run mode for safety

## Example Transformation

**Before:**
```text
davola_joe127509_question_4183284_7515253_final.m
costanza_george40227_question_4183284_7521448_Matrix analysis final; ckh209.pdf
kramercosmo_85905_14507942_Final_Problem_3.m
```

**After:**
```text
davola_joe/
    final.m

costanza_george/
    Matrix analysis final - ckh209.pdf

kramercosmo/
    Final_Problem_3.m
```

## Installation

### Using Conda (Recommended)
```bash
conda env create -f environment.yml
conda activate canvas-organizer
```

### Using pip
```bash
pip install -e .
```

## Usage

Run from the directory containing your downloaded Canvas files:

```bash
# 1. Always do a dry run first!
organize-canvas . --dry-run

# 2. When you're happy with the output, run for real:
organize-canvas .
```

Or specify a different folder:

```bash
organize-canvas ~/Downloads/Canvas_Submissions --dry-run
```

### Command Line Options

| Option             | Description                                 |
|--------------------|---------------------------------------------|
| `--dry-run`        | Show what would happen without moving files |
| `--ignore "*.zip"` | Ignore specific file patterns               |
| `-q`, `--quiet`    | Suppress non-error messages                 |

You can also run it directly:

```bash
python -m canvas_organizer.organizer /path/to/files --dry-run
```

## Project Structure

```text
canvas-organizer/
├── src/
│   └── canvas_organizer/
│       ├── __init__.py
│       └── organizer.py
├── tests/                  # optional
├── samples/
│   └── test_files/         # for testing
├── pyproject.toml
├── environment.yml
├── README.md
└── .gitignore
```

## License

MIT License
