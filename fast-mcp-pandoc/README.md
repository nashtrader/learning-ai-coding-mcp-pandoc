# Fast MCP Pandoc

> FastAPI-basierte Implementierung des MCP-Pandoc-Servers mit SSE-Streaming-Unterstützung und vollständigem MCP-Protokoll

## Übersicht

Fast MCP Pandoc ist eine moderne, auf FastAPI basierende Implementierung des ursprünglichen MCP-Pandoc-Servers mit vollständiger Unterstützung für das Model Context Protocol (MCP) und Server-Sent Events (SSE). Der Server ermöglicht die Umwandlung von Dokumenten zwischen verschiedenen Formaten mit Echtzeitaktualisierungen über SSE während des Konvertierungsprozesses und bietet eine standardkonforme MCP-Schnittstelle zur nahtlosen Integration mit MCP-Clients wie dem n8n MCP Client Node.

## Funktionen

- **Model Context Protocol (MCP)**: Vollständige Implementierung des MCP-Protokolls mit Tool-Discovery
- **Server-Sent Events (SSE)**: Streaming von Echtzeit-Konvertierungsfortschritten
- **Formatunterstützung**: Konvertierung zwischen verschiedenen Dokumentformaten (markdown, html, pdf, docx, etc.)
- **REST API**: Einfache Integration mit Web-Frontends oder anderen Services
- **Kompatibilitätsmodus**: Unterstützt die ursprüngliche MCP-Pandoc API
- **n8n Integration**: Nahtlose Anbindung an n8n über den MCP Client Node

## Unterstützte Formate

- **Basisformate** (direkte Konvertierung):
  - Plain Text (.txt)
  - Markdown (.md)
  - HTML (.html)

- **Erweiterte Formate** (benötigt vollständige Dateipfade):
  - PDF (.pdf) - benötigt TeX Live Installation
  - DOCX (.docx)
  - RST (.rst)
  - LaTeX (.tex)
  - EPUB (.epub)

## Voraussetzungen

1. **Python 3.11+**
2. **Pandoc** (für Dokumentenkonvertierung)
3. **TeX Live** (nur für PDF-Konvertierung)

### Installation der Abhängigkeiten

```bash
# Pandoc installieren
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# TeX Live für PDF-Konvertierung installieren
# Ubuntu/Debian
sudo apt-get install texlive-xetex

# macOS
brew install texlive
```

## Installation

```bash
pip install fast-mcp-pandoc
```

## Manuelle Installation (Entwicklung)

```bash
git clone https://github.com/yourusername/fast-mcp-pandoc.git
cd fast-mcp-pandoc
pip install -e .
```

## Nutzung

### Server starten

```bash
fast-mcp-pandoc
```

Der Server startet standardmäßig auf `http://0.0.0.0:8000`.

### API-Endpunkte

#### Health Check

```http
GET /health
```

#### Synchrone Konvertierung (Kompatibilitätsmodus)

```http
POST /convert
```

Request-Body:

```json
{
  "contents": "# Beispiel\nDies ist ein **Beispieltext**.",
  "input_format": "markdown",
  "output_format": "html"
}
```

ODER:

```json
{
  "input_file": "/path/to/input.md",
  "output_format": "pdf",
  "output_file": "/path/to/output.pdf"
}
```

#### Streaming-Konvertierung mit SSE

```http
GET /convert/stream?contents=...&input_format=...&output_format=...
```

#### MCP-Protokoll Endpoint (n8n MCP Client Node kompatibel)

```http
GET /sse
```

Dieser Endpunkt implementiert das vollständige Model Context Protocol (MCP) und bietet Tool-Discovery sowie standardisierte Event-Formate für MCP-Clients wie den n8n MCP Client Node.

Parameter:

- `contents`: Zu konvertierender Inhalt (optional wenn input_file angegeben)
- `input_file`: Pfad zur Eingabedatei (optional wenn contents angegeben)
- `input_format`: Quellformat (Standard: markdown)
- `output_format`: Zielformat (Standard: markdown)
- `output_file`: Pfad zur Ausgabedatei (erforderlich für pdf, docx, rst, latex, epub)

### Beispiel: SSE-Streams im Frontend nutzen

```javascript
const eventSource = new EventSource('/convert/stream?contents=...');

eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.percentage}% - ${data.message}`);
  // Update UI with progress
});

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Conversion complete:', data.result);
  eventSource.close();
  // Update UI with result
});

eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  console.error('Conversion error:', data.error);
  eventSource.close();
  // Show error in UI
});
```

## Integration mit n8n

Fast MCP Pandoc lässt sich nahtlos mit n8n über den MCP Client Node integrieren.

### n8n MCP Client Node Konfiguration

1. **MCP Client Node hinzufügen**:
   - Suche in n8n nach "MCP Client" und füge den Node zu deinem Workflow hinzu

2. **Verbindungskonfiguration**:
   - **Server-URL**: `http://localhost:8000` (oder `http://host.docker.internal:8000` wenn in Docker)
   - **Verbindungstyp**: `HTTP`
   - **Transport**: `SSE` (Server Sent Events)

3. **Tools-Discovery**:
   Nach der Verbindung entdeckt der MCP Client automatisch das verfügbare `convert-contents` Tool.

4. **Tool Parameter konfigurieren**:
   - `contents`: Der zu konvertierende Inhalt
   - `input_format`: Das Quellformat (z.B. "markdown")
   - `output_format`: Das Zielformat (z.B. "html" oder "pdf")
   - `output_file`: Optional, für Formate die eine Datei benötigen

## Entwicklung

### Tests ausführen

```bash
pytest
```

### CI/CD-Pipeline

Die CI/CD-Pipeline umfasst:

- Code-Formatierung (Black, isort)
- Linting (Flake8)
- Typüberprüfung (mypy)
- Unit- und Integrationstests (pytest)
- Docker-Container-Build

## Lizenz

MIT-Lizenz
