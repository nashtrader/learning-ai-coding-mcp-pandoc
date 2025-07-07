# Fast-MCP-Pandoc Dokumentation

## Überblick

Fast-MCP-Pandoc ist eine moderne API für die Dokumentenkonvertierung mit Pandoc, die Server-Sent Events (SSE) für Echtzeitaktualisierungen während des Konvertierungsprozesses unterstützt. Die API ermöglicht die Umwandlung zwischen verschiedenen Dokumentformaten wie Markdown, HTML, PDF, DOCX und mehr.

## Architektur

Die Anwendung verwendet folgende Schlüsseltechnologien:

- **FastAPI**: Für die API-Endpoints und HTTP-Handling
- **SSE (Server-Sent Events)**: Für Echtzeit-Fortschrittsupdates
- **Worker-Pool**: Für asynchrone Konvertierungsprozesse
- **Pypandoc**: Als Python-Wrapper für die Pandoc-Dokumentenkonvertierung

Die Hauptkomponenten der Anwendung sind:

1. **Server**: FastAPI-Anwendung mit Endpunkten
2. **Worker-Pool**: Thread-Pool für parallele Dokumentkonvertierung
3. **Models**: Pydantic-Modelle für Requests und SSE-Events
4. **SSE-Stream**: Mechanismus zur Echtzeit-Kommunikation mit Clients

## API-Endpunkte

### 1. Gesundheitsprüfung

```http
GET /health
```

Antwort:
```json
{
  "status": "healthy"
}
```

### 2. Synchrone Konvertierung

```http
POST /convert
```

Request-Body:
```json
{
  "contents": "# Überschrift\nInhalt mit **Formatierung**",
  "input_format": "markdown",
  "output_format": "html"
}
```

Antwort:
```json
{
  "status": "success",
  "result": "<h1>Überschrift</h1>\n<p>Inhalt mit <strong>Formatierung</strong></p>"
}
```

### 3. Streaming-Konvertierung mit SSE

```http
GET /convert/stream?contents=...&input_format=...&output_format=...
```

Antwort-Stream:

```
data: {"event":"progress","data":{"percentage":0,"message":"Starting conversion..."}}

data: {"event":"progress","data":{"percentage":25,"message":"Preparing document..."}}

data: {"event":"progress","data":{"percentage":50,"message":"Converting document..."}}

data: {"event":"progress","data":{"percentage":75,"message":"Finalizing..."}}

data: {"event":"complete","data":{"message":"Conversion complete","result":"<h1>Überschrift</h1>..."}}
```

### 4. Heartbeat

```http
GET /heartbeat
```

Antwort:
```json
{
  "alive": true
}
```

## Request-Parameter

| Parameter     | Typ   | Beschreibung                                   | Standard  | Erforderlich |
|---------------|-------|------------------------------------------------|-----------|-------------|
| contents      | string | Zu konvertierender Inhalt                     | -         | Ja (wenn input_file nicht angegeben) |
| input_file    | string | Pfad zur Eingabedatei                         | -         | Ja (wenn contents nicht angegeben) |
| input_format  | string | Quellformat (markdown, html, etc.)            | markdown  | Nein |
| output_format | string | Zielformat (markdown, html, pdf, etc.)        | markdown  | Nein |
| output_file   | string | Pfad für die Ausgabedatei                     | -         | Ja (für pdf, docx, etc.) |

## SSE-Events

Die `/convert/stream`-Route gibt folgende Event-Typen zurück:

1. **progress**: Fortschrittsupdates während der Konvertierung
   ```json
   {"event":"progress","data":{"percentage":25,"message":"Preparing document..."}}
   ```

2. **complete**: Erfolgreich abgeschlossene Konvertierung
   ```json
   {"event":"complete","data":{"message":"Conversion complete","result":"<html>...</html>"}}
   ```

3. **error**: Fehler während der Konvertierung
   ```json
   {"event":"error","data":{"message":"Error during conversion","error":"File not found"}}
   ```

4. **heartbeat**: Verbindung aufrechterhalten
   ```json
   {"event":"heartbeat","data":{"timestamp":"2025-07-02T12:52:31+02:00"}}
   ```

## Client-Integration

### JavaScript-Beispiel

```javascript
// SSE-Verbindung herstellen
const eventSource = new EventSource('/convert/stream?contents=# Überschrift&output_format=html');

// Fortschrittsupdates
eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Fortschritt: ${data.percentage}% - ${data.message}`);
  updateProgressBar(data.percentage);
});

// Abschluss der Konvertierung
eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Konvertierung abgeschlossen:', data.result);
  displayResult(data.result);
  eventSource.close();
});

// Fehlerbehandlung
eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  console.error('Konvertierungsfehler:', data.error);
  showErrorMessage(data.message);
  eventSource.close();
});

// Heartbeat-Behandlung
eventSource.addEventListener('heartbeat', (event) => {
  console.log('Verbindung aktiv');
});
```

### Python-Client-Beispiel

```python
import requests
import json
import sseclient

def sse_client():
    url = 'http://localhost:8000/convert/stream'
    params = {
        'contents': '# Überschrift\nText mit **Formatierung**',
        'input_format': 'markdown',
        'output_format': 'html'
    }
    
    # SSE-Verbindung herstellen
    response = requests.get(url, params=params, stream=True)
    client = sseclient.SSEClient(response)
    
    # Events verarbeiten
    for event in client.events():
        data = json.loads(event.data)
        event_type = data.get('event')
        
        if event_type == 'progress':
            print(f"Fortschritt: {data['data']['percentage']}% - {data['data']['message']}")
        elif event_type == 'complete':
            print(f"Konvertierung abgeschlossen: {data['data']['result'][:50]}...")
            break
        elif event_type == 'error':
            print(f"Fehler: {data['data']['message']}")
            break
```

## Erweiterte Konfiguration

### Umgebungsvariablen

Die Anwendung kann über folgende Umgebungsvariablen konfiguriert werden:

- `MAX_WORKERS`: Anzahl der Worker-Threads (Standard: 4)
- `PORT`: HTTP-Port (Standard: 8000)
- `HOST`: HTTP-Host (Standard: 0.0.0.0)
- `LOG_LEVEL`: Logging-Level (Standard: INFO)

### Pandoc-Konfiguration

Die Anwendung unterstützt erweiterte Pandoc-Optionen. PDF-Konvertierungen verwenden standardmäßig XeLaTeX mit folgenden Optionen:

```python
extra_args=[
    "--pdf-engine=xelatex",
    "-V", "geometry:margin=1in"
]
```

## Fehlerbehandlung

Die API gibt folgende HTTP-Statuscodes zurück:

- **200 OK**: Erfolgreiche Anfrage
- **400 Bad Request**: Ungültige Anfrageparameter
- **422 Unprocessable Entity**: Validierungsfehler (z.B. unbekanntes Format)
- **500 Internal Server Error**: Serverfehler während der Konvertierung

## Performance-Optimierung

Für optimale Performance sollten Sie:

1. Die Anzahl der Worker an Ihre CPU-Kerne anpassen
2. Bei großen Dokumenten die Timeouts erhöhen
3. Für hohe Last einen Load Balancer und mehrere Instanzen verwenden

## Bekannte Einschränkungen

1. PDF-Konvertierung erfordert eine funktionierende TeX-Installation
2. Große Dateien können zu längeren Konvertierungszeiten führen
3. Die maximale SSE-Verbindungszeit beträgt 5 Minuten ohne Aktivität

## Development-Workflow

### Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/yourusername/fast-mcp-pandoc.git
cd fast-mcp-pandoc

# Abhängigkeiten installieren
pip install -e ".[dev]"

# Entwicklungsserver starten
python -m fast_mcp_pandoc
```

### Tests ausführen

```bash
# Alle Tests
pytest

# Spezifische Tests
pytest tests/test_api_endpoints.py

# Mit Coverage-Bericht
pytest --cov=fast_mcp_pandoc
```

## Erweiterung

Die Anwendung kann durch Implementierung zusätzlicher Features erweitert werden:

1. Authentifizierung und Autorisierung
2. Rate Limiting
3. Unterstützung für zusätzliche Pandoc-Optionen
4. WebHooks für Ereignisbenachrichtigungen
5. Datei-Upload über Multipart-Formulare

## Troubleshooting

### Problem: SSE-Verbindungen werden unerwartet geschlossen

**Lösung**: Stellen Sie sicher, dass Proxy-Server für SSE konfiguriert sind und lange Verbindungen unterstützen.

### Problem: PDF-Konvertierung schlägt fehl

**Lösung**: Überprüfen Sie die TeX-Installation und stellen Sie sicher, dass alle erforderlichen Pakete installiert sind.

### Problem: Konvertierung dauert zu lange

**Lösung**: Erhöhen Sie die Anzahl der Worker-Threads oder verteilen Sie die Last auf mehrere Instanzen.
