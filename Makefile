.PHONY: instalar pruebas demo servidor limpiar

instalar:
	pip install -r requirements.txt

pruebas:
	PYTHONPATH=src python -m pytest tests/ -v

demo:
	PYTHONPATH=src python demo.py

servidor:
	PYTHONPATH=src python main.py

limpiar:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f *.db
