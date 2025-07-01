
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

## How to run frontend1
```
cd dataexploration
uvicorn server:app --reload
```
så burde den køre på localhost:8000

eller
uv run uvicorn server:app --reload

### 1. Build the Docker image
From the project's root directory, run:
```bash
docker build -t hack-for-health .
```

### 2. Run the Docker container
```bash
docker run -p 8000:8000 -v "$(pwd)/dataexploration:/app/dataexploration" -it --rm --name health-hack-app hack-for-health
```

The application will now be running and accessible at [http://localhost:8000](http://localhost:8000).
