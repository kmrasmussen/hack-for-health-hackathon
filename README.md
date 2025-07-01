# Hack for Health Hackathon

Speech analysis project using the Coral dataset.

## Dataset
- [Coral Dataset](https://huggingface.co/datasets/CoRal-project/coral-v2)

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd hack-for-health-hackathon
```

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install project
```bash
uv sync
```

### When you want to add new packages
```bash
uv add ***name of package***
```

### Run a script
```bash
uv run python script.py
```

## Project Structure
```
├── README.md
├── pyproject.toml
├── pyproject.toml
├── .gitignore
```

## Plan
- Coral dataset exploration
- Speech analysis implementation
