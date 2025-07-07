FROM python:3.11-slim

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir ".[dev]"

# Anwendungsquellcode kopieren
COPY src/ /app/src/

# Port freigeben
EXPOSE 8000

# Anwendung starten
CMD ["python", "-m", "src.server"]
