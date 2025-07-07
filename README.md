![PyPI Downloads](https://img.shields.io/pypi/dm/mcp-pandoc) <a href="https://smithery.ai/server/mcp-pandoc"><img alt="Smithery Badge" src="https://smithery.ai/badge/mcp-pandoc"></a> <a href="https://glama.ai/mcp/servers/xyzzgaj9bk"><img width="380" height="200" src="https://glama.ai/mcp/servers/xyzzgaj9bk/badge" /></a> [![MseeP.ai Security Assessment Badge](https://mseep.net/pr/vivekvells-mcp-pandoc-badge.png)](https://mseep.ai/app/vivekvells-mcp-pandoc)

# MCP-Pandoc Lernprojekt: Dokumentenkonvertierung mit Fast MCP und SSE

> Ein Lernrepo für AI Coding zur Demonstration von Fast MCP-Architektur, Worker-Pool-Implementation und SSE (Server-Sent Events) Streaming.
>
> Basierend auf [Model Context Protocol servers](https://github.com/modelcontextprotocol/servers/blob/main/README.md).

## Übersicht und Lernziele

Dieses Repository dient als Lernressource für KI-gestützte Codierungstechniken und demonstriert die Refaktorisierung eines Model Context Protocol (MCP) Servers für Dokumentenkonvertierung mit [Pandoc](https://pandoc.org/index.html).

### Lernziele

1. **Verständnis von MCP-Architektur**: Lernen Sie die Grundlagen der Model Context Protocol-Architektur kennen
2. **Asynchrone Verarbeitung**: Implementierung eines Worker-Pools für parallele Dokumentkonvertierung
3. **Echtzeit-Updates mit SSE**: Server-Sent Events für Streaming-Fortschrittsaktualisierungen
4. **Modernes API-Design**: Strukturierung einer FastAPI-Anwendung mit Pydantic-Modellen
5. **Testdriven Development**: Umfassende Testabdeckung mit Pytest

Dieses Projekt verwendet das [Pandoc Python-Paket](https://pypi.org/project/pandoc/) für die Dokumentenkonvertierung als Grundlage.

## Projektstruktur: Original und Erweiterungen

Dieses Repository ist in zwei Hauptteile gegliedert:

### 1. Original MCP-Pandoc (`/mcp-pandoc/`)

**Status**: Ursprüngliche Implementierung

Eine Basisimplementierung des Model Context Protocol Servers für Dokumentkonvertierung mit synchroner Verarbeitung.

### 2. Fast-MCP-Pandoc (`/fast-mcp-pandoc/`)

**Status**: Neue, refaktorisierte Implementierung mit erweiterten Funktionen

Eine moderne Neuimplementierung mit:

- **Worker-Pool**: Asynchrone parallele Verarbeitung
- **SSE-Streaming**: Echtzeit-Fortschrittsbenachrichtigungen
- **Verbesserte Modellierung**: Saubere Trennung von Datenmodellen und Logik
- **Umfassende Tests**: API-Endpunkt- und Komponententests

> 🎥 [Originale MCP-Pandoc-Demo auf YouTube](https://youtu.be/vN3VOb0rygM)

<details>
<summary>Screenshots</summary>

<img width="2407" alt="Screenshot 2024-12-26 at 3 33 54 PM" src="https://github.com/user-attachments/assets/ce3f5396-252a-4bba-84aa-65b2a06b859e" />
<img width="2052" alt="Screenshot 2024-12-26 at 3 38 24 PM" src="https://github.com/user-attachments/assets/8c525ad1-b184-41ca-b068-7dd34b60b85d" />
<img width="1498" alt="Screenshot 2024-12-26 at 3 40 51 PM" src="https://github.com/user-attachments/assets/a1e0682d-fe44-40b6-9988-bf805627beeb" />
<img width="760" alt="Screenshot 2024-12-26 at 3 41 20 PM" src="https://github.com/user-attachments/assets/1d7f5998-6d7f-48fa-adcf-fc37d0521213" />
<img width="1493" alt="Screenshot 2024-12-26 at 3 50 27 PM" src="https://github.com/user-attachments/assets/97992c5d-8efc-40af-a4c3-94c51c392534" />
</details>

More to come...

## Bereitgestellte Funktionen und APIs

### Original MCP-Pandoc

1. **`convert-contents` Tool**
   - Transformiert Inhalte zwischen unterstützten Formaten
   - Eingaben:
     - `contents` (string): Zu konvertierender Quellinhalt
     - `input_file` (string): Vollständiger Pfad zur Eingabedatei
     - `input_format` (string): Quellformat des Inhalts (Standard: markdown)
     - `output_format` (string): Zielformat (Standard: markdown)
     - `output_file` (string): Vollständiger Pfad für die Ausgabedatei

### Fast-MCP-Pandoc (Neue Implementierung)

1. **REST-API-Endpunkte**
   - `/health`: Gesundheitsstatus-Check (GET)
   - `/heartbeat`: Server-Heartbeat für SSE-Verbindungen (GET)
   - `/convert`: Synchrone Dokumentkonvertierung (POST)
   - `/convert/stream`: Streaming-Konvertierung mit SSE-Updates (GET)

2. **Worker-Pool-System**
   - Parallele Verarbeitung mehrerer Konvertierungsaufgaben
   - Fortschritts-Callbacks für Echtzeit-Updates
   - Automatische Ressourcenverwaltung

3. **SSE-Streaming-Events**
   - `progress`: Fortschrittsaktualisierungen (0-100%)
   - `complete`: Erfolgreiche Konvertierungen mit Ergebnis
   - `error`: Fehlerbenachrichtigungen
   - `heartbeat`: Verbindungs-Alive-Signale

### Supported Formats

Currently supported formats:

Basic formats (direct conversion):

- Plain text (.txt)
- Markdown (.md)
- HTML (.html)

Advanced formats (requires complete file paths):

- PDF (.pdf) - requires TeX Live installation
- DOCX (.docx)
- RST (.rst)
- LaTeX (.tex)
- EPUB (.epub)

Note: For advanced formats:

1. Complete file paths with filename and extension are required
2. **PDF conversion requires TeX Live installation** (see Critical Requirements section -> For macOS: `brew install texlive`)
3. When no output path is specified:
   - Basic formats: Displays converted content in the chat
   - Advanced formats: May save in system temp directory (/tmp/ on Unix systems)

## Usage & configuration

**NOTE: Ensure to complete installing required packages mentioned below under "Critical Requirements".**

To use the published one

```bash
{
  "mcpServers": {
    "mcp-pandoc": {
      "command": "uvx",
      "args": ["mcp-pandoc"]
    }
  }
}
```

### ⚠️ Important Notes

#### Critical Requirements

1. **Pandoc Installation**
  - **Required**: Install `pandoc` - the core document conversion engine
  - Installation:
    ```bash
    # macOS
    brew install pandoc
    
    # Ubuntu/Debian
    sudo apt-get install pandoc
    
    # Windows
    # Download installer from: https://pandoc.org/installing.html
    ```
  - **Verify**: `pandoc --version`

2. **UV package installation**
  - **Required**: Install `uv` package (includes `uvx` command)
  - Installation:
    ```bash
    # macOS
    brew install uv
    
    # Windows/Linux
    pip install uv
    ```
  - **Verify**: `uvx --version`

3. **PDF Conversion Prerequisites:** Only needed if you need to convert & save pdf
  - TeX Live must be installed before attempting PDF conversion
  - Installation commands:
    ```bash
    # Ubuntu/Debian
    sudo apt-get install texlive-xetex
    
    # macOS
    brew install texlive
    
    # Windows
    # Install MiKTeX or TeX Live from:
    # https://miktex.org/ or https://tug.org/texlive/
    ```

4. **File Path Requirements**
  - When saving or converting files, you MUST provide complete file paths including filename and extension
  - The tool does not automatically generate filenames or extensions

#### Examples

✅ Correct Usage:

```bash
# Converting content to PDF
"Convert this text to PDF and save as /path/to/document.pdf"

# Converting between file formats
"Convert /path/to/input.md to PDF and save as /path/to/output.pdf"
```

❌ Incorrect Usage:

```bash
# Missing filename and extension
"Save this as PDF in /documents/"

# Missing complete path
"Convert this to PDF"

# Missing extension
"Save as /documents/story"
```

#### Common Issues and Solutions

1. **PDF Conversion Fails**
   - Error: "xelatex not found"
   - Solution: Install TeX Live first (see installation commands above)

2. **File Conversion Fails**
   - Error: "Invalid file path"
   - Solution: Provide complete path including filename and extension
   - Example: `/path/to/document.pdf` instead of just `/path/to/`

3. **Format Conversion Fails**
   - Error: "Unsupported format"
   - Solution: Use only supported formats:
     - Basic: txt, html, markdown
     - Advanced: pdf, docx, rst, latex, epub

## Installation und Start

### 1. Original MCP-Pandoc Server

**WICHTIG: Der originale MCP-Pandoc Server kann mit Smithery oder uv/uvx installiert werden.**

#### Option 1: Manuelle Konfiguration in Claude Desktop

- MacOS: `open ~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
"mcpServers": {
  "mcp-pandoc": {
    "command": "uv",
    "args": [
      "--directory",
      "<VERZEICHNIS>/mcp-pandoc",
      "run",
      "mcp-pandoc"
    ]
  }
}
```

#### Option 2: Automatische Installation via Smithery

```bash
npx -y @smithery/cli install mcp-pandoc --client claude
```

### 2. Fast-MCP-Pandoc Server (Neue SSE-Version)

**WICHTIG: Der neue Fast-MCP-Pandoc Server kann NUR lokal oder via Docker gestartet werden, nicht via Smithery/uv.**

#### Option 1: Lokale Installation mit virtueller Umgebung

1. **Virtuelle Umgebung erstellen und aktivieren**

```bash
cd fast-mcp-pandoc
python3 -m venv venv
source venv/bin/activate
```

2. **Abhängigkeiten installieren**

```bash
pip install fastapi uvicorn pypandoc sse-starlette pydantic pytest pytest-asyncio
```

3. **Server starten**

```bash
python -m src.server
```

Der Server läuft dann auf `http://0.0.0.0:8000`.

#### Option 2: Docker-Container

1. **Docker-Image bauen**

```bash
cd fast-mcp-pandoc
docker build -t fast-mcp-pandoc .
```

2. **Container starten**

```bash
docker run -p 8000:8000 fast-mcp-pandoc
```

Der Server ist dann über `http://localhost:8000` erreichbar.

## Lernkomponenten und Programmierkonzepte

### 1. Worker-Pool-Implementierung

Der Worker-Pool in `fast-mcp-pandoc/src/worker.py` demonstriert:

- **ThreadPoolExecutor**: Asynchrone Task-Ausführung in separaten Threads
- **Callback-Mechanismen**: Fortschrittskommunikation zwischen Threads
- **Task-Kapselung**: Saubere Abstraktionen für Konvertierungsaufgaben

### 2. Server-Sent Events (SSE)

Die SSE-Implementierung in `fast-mcp-pandoc/src/server.py` zeigt:

- **Langlebige Verbindungen**: Aufrechterhaltung von Client-Verbindungen
- **Echtzeit-Updates**: Senden von Ereignissen ohne Client-Anfragen
- **Heartbeat-Mechanismus**: Verbindungserhaltung bei Inaktivität

### 3. API-Design mit FastAPI

- **Pydantic-Modelle**: Strenge Typisierung und automatische Validierung
- **Dependency Injection**: Saubere Komponentenintegration
- **Async/Await-Pattern**: Non-blocking I/O für hohe Skalierbarkeit

### 4. Testdriven Development

Die Tests in `fast-mcp-pandoc/tests/` demonstrieren:

- **Unit-Tests**: Isolierte Komponententests
- **Integrationstests**: API-Endpunkt-Validierung
- **Mock-Objekte**: Simulation von externen Abhängigkeiten
- **Edge Cases**: Robustheitstests für Fehlerszenarien

### Debugging der Original-MCP-Implementierung

Für die Fehlersuche im ursprünglichen MCP-Server empfehlen wir den [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector uv --directory <PFAD>/mcp-pandoc run mcp-pandoc
```

---

## Übungen für Kursteilnehmer

Dieses Repository bietet verschiedene Lernaufgaben, um Ihre KI-Coding-Fähigkeiten zu verbessern:

### Einstiegsaufgaben

1. **API-Endpunkt erweitern**: Fügen Sie einen neuen `/formats` Endpunkt hinzu, der alle unterstützten Formate auflistet
2. **Fortschrittsberichte verbessern**: Erweitern Sie die Fortschrittsberichte um detailliertere Informationen

### Mittelstufe

1. **Speicherüberwachung**: Implementieren Sie eine Speichernutzungsüberwachung für große Dokumente
2. **Parallelitätssteuerung**: Fügen Sie eine dynamische Anpassung der Worker-Pool-Größe basierend auf der Systemlast hinzu

### Fortgeschritten

1. **Formatunterstützung erweitern**: Integrieren Sie neue Dokumentformate und Konvertierungsoptionen
2. **Fehlertoleranz**: Implementieren Sie Wiederholungslogik für fehlgeschlagene Konvertierungen
3. **Leistungsoptimierung**: Identifizieren und optimieren Sie Leistungsengpässe

## Beitragen

Beiträge zur Verbesserung dieses Lernrepositories sind willkommen! So können Sie sich beteiligen:

1. **Fehler melden**: Haben Sie einen Bug gefunden oder haben einen Vorschlag? Öffnen Sie ein Issue.
2. **Pull-Requests einreichen**: Verbessern Sie den Code oder fügen Sie neue Features hinzu.

---
