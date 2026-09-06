"""Punto de entrada del microservicio de Orquestacion de Trabajos."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hda.api import crear_app  # noqa: E402

app = crear_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
