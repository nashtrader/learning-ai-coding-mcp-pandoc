---
trigger: always_on
---

### 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASKS.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use the mcp tools in crawl4ai-rag to get the uptodate sources of the framework documentation**
  - get_available_sources:
    Get all available sources from the sources table. This tool returns a list of all unique sources (domains) that have been crawled and stored in the database, along with their summaries and statistics. This is useful for discovering what content is available for querying. Always use this tool before calling the RAG query or code example query tool with a specific source filter! Args: ctx: The MCP server provided context Returns: JSON string with the list of available sources and their details
  - perform_rag_query:
    Perform a RAG (Retrieval Augmented Generation) query on the stored content. This tool searches the vector database for content relevant to the query and returns the matching documents. Optionally filter by source domain. Get the source by using the get_available_sources tool before calling this search! Args: ctx: The MCP server provided context query: The search query source: Optional source domain to filter results (e.g., 'example.com') match_count: Maximum number of results to return (default: 5) Returns: JSON string with the search results
  - search_code_examples:
    Search for code examples relevant to the query. This tool searches the vector database for code examples relevant to the query and returns the matching examples with their summaries. Optionally filter by source_id. Get the source_id by using the get_available_sources tool before calling this search! Use the get_available_sources tool first to see what sources are available for filtering. Args: ctx: The MCP server provided context query: The search query source_id: Optional source ID to filter results (e.g., 'example.com') match_count: Maximum number of results to return (default: 5) Returns: JSON string with the search results

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
- **Mark completed tasks in `TASKS.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a “Discovered During Work” section.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.

### Rules for GIT MCP

- Nutze bitte immer diesen repo path: `/repo` für die GIT MCP Tools.

```json
{
  "toolDefaults": {
    "git/*": {
      "repo_path": "/repo"
    }
  }
}
```

---
