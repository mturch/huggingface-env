.PHONY: setup activate login test

setup:
	@echo "Creating Hugging Face environment with uv..."
	uv venv
	uv pip install -e .
	@echo "✅ Environment setup complete."

activate:
	@echo "Run: source .venv/bin/activate"

login:
	@echo "Logging into Hugging Face..."
	huggingface-cli login

test:
	@echo "Running test script..."
	uv run python src/test_hf.py
