# colonia
An Open Source Alternative to Spacelift



# Development Environment Setup

To set up the development environment, follow these steps:
1. **Clone the Repository**:
```bash
git clone https://github.com/manoelhc/colonia.git
cd colonia
```

2. Install `pyenv` and install the 3.14.0 version of Python using `pyenv`:
```bash
pyenv install 3.14.0
pyenv local 3.14.0
```

Follow the instructions to add the proper environment variables to your shell.

3. Install `uv`:
```bash
pip install uv
```

4. Run colonia:
```bash
uv run python -m main
```
