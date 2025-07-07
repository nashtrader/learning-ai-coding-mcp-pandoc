# Deployment-Anleitung für Fast-MCP-Pandoc

Diese Anleitung beschreibt verschiedene Methoden zum Bereitstellen der Fast-MCP-Pandoc-Anwendung.

## Voraussetzungen

- Python 3.11+
- Pandoc
- TeX Live (für PDF-Konvertierung)
- Docker (für Container-Deployment)

## 1. Direktes Deployment

### Installation

```bash
# Installieren der Anwendung
pip install -e .

# Oder für Produktionsumgebungen
pip install .
```

### Ausführen

```bash
# Direkt ausführen
python -m fast_mcp_pandoc

# Oder über den installierten Entry-Point
fast-mcp-pandoc
```

Die Anwendung ist dann unter `http://0.0.0.0:8000` erreichbar.

## 2. Docker-Deployment

### Container bauen

```bash
docker build -t fast-mcp-pandoc .
```

### Container ausführen

```bash
docker run -p 8000:8000 fast-mcp-pandoc
```

Die Anwendung ist dann unter `http://localhost:8000` erreichbar.

## 3. Docker Compose Deployment

Erstelle eine `docker-compose.yml` Datei:

```yaml
version: '3'

services:
  fast-mcp-pandoc:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      # Optional: Mount ein Verzeichnis für Input/Output-Dateien
      - ./data:/data
    environment:
      - MAX_WORKERS=4
```

Ausführen mit Docker Compose:

```bash
docker compose up -d
```

## 4. Produktions-Deployment

Für Produktionsumgebungen empfehlen wir:

1. Verwenden eines WSGI-Servers wie Gunicorn
2. Setzen eines Reverse-Proxys (Nginx, Caddy) vor den Server
3. TLS/SSL-Verschlüsselung aktivieren

### Beispiel mit Gunicorn

```bash
# Installieren von Gunicorn
pip install gunicorn

# Ausführen mit Gunicorn (4 Worker-Prozesse)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker fast_mcp_pandoc.server:app
```

### Beispiel Nginx-Konfiguration

```nginx
server {
    listen 80;
    server_name fast-mcp-pandoc.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE-spezifische Header
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

## Umgebungsvariablen

Die Anwendung unterstützt folgende Umgebungsvariablen:

- `MAX_WORKERS`: Maximale Anzahl von Worker-Threads (Standard: 4)
- `PORT`: Server-Port (Standard: 8000)
- `HOST`: Server-Host (Standard: 0.0.0.0)

## Gesundheitsüberwachung

Die Anwendung stellt folgende Endpunkte für Monitoring zur Verfügung:

- `/health`: Gesundheitsprüfung
- `/heartbeat`: Heartbeat für SSE-Verbindungen

## Sicherheitshinweise

1. In Produktionsumgebungen sollten Sie unbedingt TLS/SSL-Verschlüsselung aktivieren.
2. Beschränken Sie den Dateizugriff auf vertrauenswürdige Verzeichnisse, wenn Sie mit Dateien arbeiten.
3. Limitieren Sie die maximale Dateigröße und Konvertierungszeit nach Bedarf.

## Troubleshooting

### Häufige Probleme

- **PDF-Konvertierung schlägt fehl**: Stellen Sie sicher, dass TeX Live korrekt installiert ist
- **SSE-Verbindungen werden unterbrochen**: Prüfen Sie Proxy-Timeout-Einstellungen
- **Langsame Konvertierung**: Erhöhen Sie die Anzahl der Worker-Threads

## Bereitstellungsautomatisierung

Ein Beispiel für eine GitHub Actions Workflow-Datei:

```yaml
name: Deploy Fast-MCP-Pandoc

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t fast-mcp-pandoc .
        
      - name: Log in to registry
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        
      - name: Push image
        run: |
          docker tag fast-mcp-pandoc your-registry/fast-mcp-pandoc:latest
          docker push your-registry/fast-mcp-pandoc:latest
```
