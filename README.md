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

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the data exploration
```bash
python dataexploration/load_coral.py
```

## Project Structure
```
├── README.md
├── requirements.txt
├── .gitignore
└── dataexploration/
    └── load_coral.py
```

## Plan
- Coral dataset exploration
- Speech analysis implementation
