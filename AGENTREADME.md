# MCP-Pandoc Project Agent Readme

## Project Overview

MCP-Pandoc is a Model Context Protocol (MCP) server for document format conversion using Pandoc. The server provides tools to transform content between different document formats while preserving formatting and structure.

### Key Project Information
- **Repository**: vivekVells/mcp-pandoc
- **Status**: Early development
- **Primary Function**: Document format conversion
- **Core Dependencies**: Pandoc, pypandoc, TeX Live (for PDF)

## Directory Structure

```
/mcp-pandoc
├── .git/                  # Git repository
├── .gitignore             # Git ignore patterns
├── .python-version        # Python version specification
├── .windsurf/             # Windsurf configuration
├── Dockerfile             # Container definition
├── LICENSE                # Project license
├── PLANNING.md            # Project planning document
├── README.md              # Project README
├── TASKS.md               # Task tracking
├── demo/                  # Demo resources
├── pyproject.toml         # Python project configuration
├── smithery.yaml          # Smithery configuration
├── src/                   # Source code
│   └── mcp_pandoc/        # Main package
│       ├── __init__.py    # Package initialization
│       └── server.py      # MCP server implementation
└── uv.lock                # UV package manager lock file
```

## Implementation Details

The project is implemented as a Python package with a core MCP server implementation in `server.py`. The server provides a single tool called `convert-contents` that handles document conversion between various formats.

### Key Components

- **Server Implementation**: The MCP server is implemented using the MCP framework with a stdio server.
- **Conversion Logic**: Document conversion is performed using pypandoc, which is a Python wrapper for Pandoc.
- **Supported Formats**:
  - Basic formats: txt, html, markdown
  - Advanced formats: pdf, docx, rst, latex, epub

## Available Tools

### 1. convert-contents

**Description**: Transforms content between supported formats

**Parameters**:
- `contents` (string): Source content to convert (required if input_file not provided)
- `input_file` (string): Complete path to input file (required if contents not provided)
- `input_format` (string): Source format of the content (defaults to markdown)
- `output_format` (string): Target format (defaults to markdown)
- `output_file` (string): Complete path for output file (required for pdf, docx, rst, latex, epub formats)

**Format Support**:
- Basic formats (direct conversion): Plain text (.txt), Markdown (.md), HTML (.html)
- Advanced formats (requires complete file paths): PDF (.pdf), DOCX (.docx), RST (.rst), LaTeX (.tex), EPUB (.epub)

## Critical Requirements

1. **Pandoc Installation**
   - Required for all document conversions
   - Install commands:
     ```bash
     # macOS
     brew install pandoc
     
     # Ubuntu/Debian
     sudo apt-get install pandoc
     
     # Windows
     # Download installer from: https://pandoc.org/installing.html
     ```

2. **UV Package Installation**
   - Required for running the server
   - Install commands:
     ```bash
     # macOS
     brew install uv
     
     # Windows/Linux
     pip install uv
     ```

3. **PDF Conversion Prerequisites**
   - TeX Live must be installed before attempting PDF conversion
   - Install commands:
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
   - When saving or converting files, complete file paths including filename and extension must be provided
   - The tool does not automatically generate filenames or extensions

## Usage Guidelines

### Correct Usage Examples

```
# Converting content to PDF
"Convert this text to PDF and save as /path/to/document.pdf"

# Converting between file formats
"Convert /path/to/input.md to PDF and save as /path/to/output.pdf"
```

### Incorrect Usage Examples

```
# Missing filename and extension
"Save this as PDF in /documents/"

# Missing complete path
"Convert this to PDF"

# Missing extension
"Save as /documents/story"
```

## Development and Working Environment

### WSL2 Environment Notes

- Working in WSL2 in a Remote-Repo on LinuxSubsystems
- Use `python3` command to execute Python scripts
- Docker Compose is executed with `docker compose <command>` (without hyphen)

### Installation and Configuration

For users:
```json
{
  "mcpServers": {
    "mcp-pandoc": {
      "command": "uvx",
      "args": ["mcp-pandoc"]
    }
  }
}
```

For developers:
```json
{
  "mcpServers": {
    "mcp-pandoc": {
      "command": "uv",
      "args": [
        "--directory",
        "<DIRECTORY>/mcp-pandoc",
        "run",
        "mcp-pandoc"
      ]
    }
  }
}
```

### Debugging
- Use the MCP Inspector for debugging:
  ```bash
  npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-pandoc run mcp-pandoc
  ```

## Git Repository Management

- Git operations should use the repo path: `/repo`
- Git MCP tool defaults configuration:
  ```json
  {
    "toolDefaults": {
      "git/*": {
        "repo_path": "/repo"
      }
    }
  }
  ```

## Development Workflow and Practices

### Code Structure
- Organize code into clearly separated modules
- Use clear, consistent imports (prefer relative imports within packages)
- Never create files longer than 500 lines of code

### Testing
- Create Pytest unit tests for new features
- Update existing tests when logic changes
- Tests should mirror the main app structure
- Include tests for expected use, edge cases, and failure cases

### Documentation
- Update README.md when features change
- Comment non-obvious code
- Use docstrings for every function (Google style)

### Task Management
- Always read PLANNING.md at the start of new conversations
- Check TASKS.md before starting new tasks
- Mark completed tasks in TASKS.md
- Add discovered sub-tasks to TASKS.md

## Project Resources

- Framework Documentation: Use MCP tools in crawl4ai-rag to get up-to-date sources
- Documentation Search: `get_available_sources`, `perform_rag_query`, `search_code_examples`
