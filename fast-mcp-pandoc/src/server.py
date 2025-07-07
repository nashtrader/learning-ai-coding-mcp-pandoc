"""
FastAPI server implementation for Fast MCP Pandoc with SSE support.

This module provides a FastAPI-based server with Server-Sent Events (SSE)
streaming capability for document conversion using Pandoc.
"""

import asyncio
import json
import os
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pypandoc
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sse_starlette.sse import EventSourceResponse

from .models import (ConversionComplete, ConversionError, ConversionProgress,
                    ConversionRequest, ConversionHeartbeat, MCPEvent, MCPErrorDetail,
                    MCPStatus, MCPTool, MCPToolParameter, MCPToolInvocation,
                    MCPToolsDiscovery)
from .worker import ConversionTask, worker_pool

app = FastAPI(
    title="Fast MCP Pandoc",
    description="Fast MCP server for Pandoc document conversion with SSE streaming",
    version="0.1.0",
)

# Dictionary to store active SSE connections and their progress updates
active_connections = {}

# Alle Modellklassen wurden in models.py verschoben und werden von dort importiert


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/convert")
async def convert_contents(request: ConversionRequest) -> JSONResponse:
    """
    Convert content between formats (synchronous version).
    
    This endpoint provides backward compatibility with the original MCP-Pandoc API.
    For streaming conversion progress, use the /convert/stream endpoint.
    """
    try:
        # Erstelle eine einzigartige Task-ID
        task_id = str(uuid.uuid4())
        
        # Führe die Konvertierung synchron durch
        result_future = asyncio.Future()
        
        # Definiere den Callback für Fortschrittsupdates
        def progress_callback(task_id: str, percentage: int, message: str):
            if percentage == 100:
                # Bei 100% setzen wir das Ergebnis der Future
                if not result_future.done():
                    result_future.set_result(message)
            elif percentage == -1:
                # Bei Fehler (-1) setzen wir die Exception
                if not result_future.done():
                    result_future.set_exception(ValueError(message))
        
        # Erstelle und starte die Konvertierungsaufgabe
        task = ConversionTask(
            request=request,
            task_id=task_id,
            progress_callback=progress_callback
        )
        
        await worker_pool.submit_task(task)
        
        # Warte auf das Ergebnis der Konvertierung
        result = await result_future
        
        return JSONResponse(content={"status": "success", "result": result})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@app.get("/convert/stream")
async def stream_conversion(
    request: Request,
    contents: Optional[str] = None,
    input_file: Optional[str] = None,
    input_format: str = "markdown",
    output_format: str = "markdown",
    output_file: Optional[str] = None,
) -> EventSourceResponse:
    """
    Stream the conversion progress using Server-Sent Events.
    
    This endpoint provides real-time updates on the conversion process.
    """
    # Create a ConversionRequest model from the parameters
    conversion_request = ConversionRequest(
        contents=contents,
        input_file=input_file,
        input_format=input_format,
        output_format=output_format,
        output_file=output_file,
    )
    
    # Erstelle eine einzigartige Task-ID
    task_id = str(uuid.uuid4())
    
    # Erstelle einen Event-Queue für diese Verbindung
    queue = asyncio.Queue()
    
    # Registriere die Verbindung im aktiven Verbindungspool
    active_connections[task_id] = queue
    
    async def event_generator():
        """Generate SSE events for the conversion process."""
        try:
            # Initial progress event
            yield json.dumps(
                ConversionProgress(
                    data={"percentage": 0, "message": "Starting conversion..."}
                ).dict()
            )
            
            # Definiere den Callback für Fortschrittsupdates
            def progress_callback(task_id: str, percentage: int, message: str):
                # Füge ein Fortschrittsevent zur Queue hinzu
                event_data = None
                
                if percentage == 100:
                    # Konvertierung abgeschlossen
                    event_data = ConversionComplete(
                        data={
                            "message": "Conversion complete",
                            "result": message,
                        }
                    ).dict()
                elif percentage == -1:
                    # Fehler bei der Konvertierung
                    event_data = ConversionError(
                        data={
                            "message": f"Error during conversion: {message}",
                            "error": message
                        }
                    ).dict()
                else:
                    # Fortschritts-Update
                    event_data = ConversionProgress(
                        data={"percentage": percentage, "message": message}
                    ).dict()
                
                # Füge das Event zur Queue hinzu, falls vorhanden
                if event_data and task_id in active_connections:
                    asyncio.run_coroutine_threadsafe(
                        active_connections[task_id].put(event_data),
                        asyncio.get_event_loop()
                    )
            
            # Erstelle und starte die Konvertierungsaufgabe
            task = ConversionTask(
                request=conversion_request,
                task_id=task_id,
                progress_callback=progress_callback
            )
            
            # Starte die Konvertierung asynchron
            await worker_pool.submit_task(task)
            
            # Warte auf Events vom Worker und sende sie an den Client
            heartbeat_timer = 0
            while True:
                # Entweder erhalte ein Event aus der Queue oder sende ein Heartbeat alle 15 Sekunden
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield json.dumps(event_data)
                    
                    # Prüfe, ob es ein CompleteEvent oder ErrorEvent war
                    if event_data.get("event") in ["complete", "error"]:
                        # Konvertierung abgeschlossen oder Fehler aufgetreten, beende den Stream
                        break
                except asyncio.TimeoutError:
                    # Sende ein Heartbeat-Event nach Timeout
                    heartbeat_data = ConversionHeartbeat(
                        data={"timestamp": datetime.now().isoformat()}
                    ).dict()
                    yield json.dumps(heartbeat_data)
                    heartbeat_timer += 15
                    
                    # Beende nach 5 Minuten ohne Aktivität
                    if heartbeat_timer >= 300:
                        yield json.dumps(
                            ConversionError(
                                data={
                                    "message": "Conversion timed out after 5 minutes of inactivity",
                                    "error": "timeout"
                                }
                            ).dict()
                        )
                        break
                    
        except Exception as e:
            # Send error event
            yield json.dumps(
                ConversionError(
                    data={
                        "message": f"Error during conversion: {str(e)}",
                        "error": str(e)
                    }
                ).dict()
            )
        finally:
            # Bereinige die Verbindung nach Abschluss
            if task_id in active_connections:
                del active_connections[task_id]
    
    return EventSourceResponse(event_generator())


# Konvertierungsfunktion wurde in den worker.py-Modul verschoben
# und wird jetzt durch den Worker-Pool verarbeitet


@app.get("/heartbeat")
async def heartbeat() -> Dict[str, bool]:
    """Heartbeat endpoint for SSE reconnection."""
    return {"alive": True}


@app.get("/sse")
async def mcp_sse_endpoint(
    request: Request,
    tool: Optional[str] = None,
    contents: Optional[str] = None,
    input_format: Optional[str] = None,
    output_format: Optional[str] = None,
    output_file: Optional[str] = None
) -> EventSourceResponse:
    """
    MCP Protocol SSE endpoint for tool discovery and tool invocation.
    
    This endpoint implements the Model Context Protocol (MCP) over Server-Sent Events,
    providing tool discovery and document conversion functionality via a standard interface.
    """
    # Wenn kein Tool angegeben ist, machen wir Tool Discovery
    if not tool:
        return EventSourceResponse(mcp_tool_discovery_generator())
    
    # Wenn das Tool "convert-contents" ist, rufen wir die Konvertierung auf
    if tool == "convert-contents":
        # Erstellen einer Conversion-Request aus den Parametern
        conversion_request = ConversionRequest(
            contents=contents,
            input_file=None,  # Im MCP-Protokoll unterstützen wir zunächst nur Inhalte direkt
            input_format=input_format or "markdown",
            output_format=output_format or "html",
            output_file=output_file
        )
        
        return EventSourceResponse(mcp_convert_generator(request, conversion_request))
    else:
        # Unbekanntes Tool
        return EventSourceResponse(mcp_error_generator(f"Unknown tool: {tool}"))


async def mcp_tool_discovery_generator():
    """
    Generator für MCP Tool Discovery Events.
    
    Gibt die verfügbaren Tools im MCP-Format zurück.
    """
    # Definiere die Parameter für das convert-contents Tool
    convert_tool_params = [
        MCPToolParameter(
            name="contents",
            description="Der zu konvertierende Inhalt",
            type="string",
            required=True
        ),
        MCPToolParameter(
            name="input_format",
            description="Das Quellformat des Inhalts",
            type="string",
            required=False,
            default="markdown",
            enum=["markdown", "html", "txt", "rst"]
        ),
        MCPToolParameter(
            name="output_format",
            description="Das gewünschte Zielformat",
            type="string",
            required=False,
            default="html",
            enum=["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt"]
        ),
        MCPToolParameter(
            name="output_file",
            description="Pfad zur Ausgabedatei (erforderlich für pdf, docx, rst, latex, epub)",
            type="string",
            required=False
        )
    ]
    
    # Erstelle das convert-contents Tool
    convert_tool = MCPTool(
        name="convert-contents",
        description="Konvertiert Dokumentinhalte zwischen verschiedenen Formaten mit Pandoc",
        parameters=convert_tool_params
    )
    
    # Erstelle die Tool Discovery Response
    tools_discovery = MCPToolsDiscovery(tools=[convert_tool])
    
    # Sende die Tool Discovery als Event
    yield json.dumps({"type": "discovery", "data": tools_discovery.dict()})


async def mcp_convert_generator(request: Request, conversion_request: ConversionRequest):
    """
    Generator für MCP-konforme Konvertierungs-Events.
    
    Konvertiert Inhalte und sendet Fortschrittsupdates im MCP-Format.
    """
    # Erstelle eine einzigartige Event-ID
    event_id = str(uuid.uuid4())
    start_time = time.time()
    created_at = datetime.now().isoformat()
    
    try:
        # Erstelle eine Queue für Fortschrittsupdates
        queue = asyncio.Queue()
        
        # Registriere die Verbindung
        active_connections[event_id] = queue
        
        # Definiere den Callback für Fortschrittsupdates
        def progress_callback(task_id: str, percentage: int, message: str):
            # MCP-Event erstellen
            if percentage == 100:
                # Conversion complete
                event_data = MCPEvent(
                    id=event_id,
                    status=MCPStatus.COMPLETE,
                    tool="convert-contents",
                    created_at=created_at,
                    output=message,
                    runtime=time.time() - start_time
                ).dict()
                
            elif percentage == -1:
                # Conversion error
                error_detail = MCPErrorDetail(message=message)
                event_data = MCPEvent(
                    id=event_id,
                    status=MCPStatus.ERROR,
                    tool="convert-contents",
                    created_at=created_at,
                    error=error_detail,
                    runtime=time.time() - start_time
                ).dict()
                
            else:
                # Progress update
                event_data = MCPEvent(
                    id=event_id,
                    status=MCPStatus.RUNNING if percentage > 0 else MCPStatus.CREATED,
                    tool="convert-contents",
                    created_at=created_at,
                    output={"percentage": percentage, "message": message}
                ).dict()
            
            # Event zur Queue hinzufügen
            if event_data and event_id in active_connections:
                asyncio.run_coroutine_threadsafe(
                    active_connections[event_id].put(event_data),
                    asyncio.get_event_loop()
                )
        
        # Sende initial created event
        initial_event = MCPEvent(
            id=event_id,
            status=MCPStatus.CREATED,
            tool="convert-contents",
            created_at=created_at,
            output={"percentage": 0, "message": "Starting conversion"}
        )
        yield json.dumps(initial_event.dict())
        
        # Erstelle und starte die Konvertierungsaufgabe
        task = ConversionTask(
            request=conversion_request,
            task_id=event_id,
            progress_callback=progress_callback
        )
        
        await worker_pool.submit_task(task)
        
        # Warte auf Events vom Worker und sende sie an den Client
        try:
            while True:
                event_data = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield json.dumps(event_data)
                
                # Beende den Generator nach complete oder error event
                if event_data.get("status") in [MCPStatus.COMPLETE, MCPStatus.ERROR]:
                    break
                    
        except asyncio.TimeoutError:
            # Timeout - sende ein Error-Event
            error_detail = MCPErrorDetail(message="Conversion timed out after 60 seconds")
            timeout_event = MCPEvent(
                id=event_id,
                status=MCPStatus.ERROR,
                tool="convert-contents",
                created_at=created_at,
                error=error_detail,
                runtime=time.time() - start_time
            )
            yield json.dumps(timeout_event.dict())
    
    except Exception as e:
        # Bei Ausnahmen ein Error-Event senden
        error_detail = MCPErrorDetail(message=str(e))
        error_event = MCPEvent(
            id=event_id,
            status=MCPStatus.ERROR,
            tool="convert-contents",
            created_at=created_at,
            error=error_detail,
            runtime=time.time() - start_time
        )
        yield json.dumps(error_event.dict())
    
    finally:
        # Verbindung bereinigen
        if event_id in active_connections:
            del active_connections[event_id]


async def mcp_error_generator(error_message: str):
    """
    Generator für MCP-Fehler-Events.
    
    Args:
        error_message: Die Fehlermeldung
    """
    event_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    error_detail = MCPErrorDetail(message=error_message)
    error_event = MCPEvent(
        id=event_id,
        status=MCPStatus.ERROR,
        tool="",  # Leerer Tool-Name, da kein gültiges Tool
        created_at=created_at,
        error=error_detail
    )
    
    yield json.dumps(error_event.dict())


def main():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
