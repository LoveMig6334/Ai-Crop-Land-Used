# Contributing to AI Crop Land-Use Analysis

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/Ai-Crop-Land-Used.git
   cd "AI Crop Land-Used"
   ```
3. **Set up** the environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # Linux/Mac
   pip install -r requirements.txt
   ```
4. **Create a branch**: `git checkout -b feature/your-feature`
5. **Make changes**, commit, push, and open a **Pull Request**

## 📐 Project Conventions

### File Paths

- **Always** use `src/util/data_path.py` for paths — never hardcode.
- All generated figures go under `fig/` (centralized).
- Model outputs go under `model/` (forecasts, errors, weights).

### Code Style

- **Python**: Follow [PEP 8](https://peps.python.org/pep-0008/). Use type hints where practical.
- **Notebooks**: Clear cell outputs before committing. Keep cells focused and well-commented.
- **Naming**: Use `snake_case` for files and variables, descriptive names for notebooks.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new crop support for rice
fix: Correct Thai date parsing for years before 2547
docs: Update README with new fig/ structure
refactor: Migrate image paths to centralized fig/ tree
```

### Configuration

- Model hyperparameters live in `config.yaml` — don't hardcode them in notebooks.
- Access via `from src.util.config import CFG`.

## 🔬 Areas for Contribution

| Area         | Examples                                                   |
| ------------ | ---------------------------------------------------------- |
| **Data**     | New crop datasets, weather correlation data                |
| **Models**   | New architectures, hyperparameter tuning, ensemble methods |
| **Analysis** | New visualization types, statistical analysis notebooks    |
| **Infra**    | CI/CD, automated testing, Docker support                   |
| **Docs**     | Translation, tutorials, API documentation                  |

## 🧪 Testing Your Changes

1. Ensure notebooks run end-to-end without errors
2. Verify generated figures save correctly to `fig/`
3. Check that `src/util/data_path.py` paths resolve for any new outputs
4. Run training scripts if modifying model code:
   ```bash
   python -m src.train.train_lstm --crop cassava
   ```

## 📝 Pull Request Guidelines

- **One concern per PR** — keep changes focused
- **Describe what and why** in the PR description
- **Link related issues** using `Closes #123`
- **Clear notebook outputs** before submitting
- **Update documentation** if you change paths, APIs, or project structure

## ❓ Questions?

Open a [Discussion](https://github.com/LoveMig6334/Ai-Crop-Land-Used/discussions) or [Issue](https://github.com/LoveMig6334/Ai-Crop-Land-Used/issues) — we're happy to help!
