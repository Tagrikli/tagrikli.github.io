# Architecture Improvements for Malvolio Static Site Generator

## Executive Summary

This document outlines minimal, practical improvements to the static site generator while preserving its simplicity. The focus is on improving the development workflow without over-engineering.

---

## Current State Analysis

### Existing Structure
```
Malvolio/
├── main.py              # All logic in one file (~70 lines)
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── thought.html
│   └── experience.html
├── public/
│   ├── content/         # Content directories
│   │   ├── thought/     # HTML + meta.yaml
│   │   └── experience/  # HTML + meta.yaml
│   └── static/          # CSS, media
└── pyproject.toml
```

### Current Pain Points
1. **No live preview** - must manually run `main.py` after every change
2. **No file watching** - no auto-regeneration on changes
3. **Hardcoded paths** - paths defined at module level, not configurable
4. **Incomplete cleanup** - `clear_renders()` only removes specific files
5. **No CLI interface** - script runs everything on execution
6. **Mixed concerns** - configuration, rendering, and execution combined

---

## Proposed Architecture

### 1. Project Structure

Keep the current structure but add a minimal module split:

```
Malvolio/
├── malvolio/                 # Package directory
│   ├── __init__.py
│   ├── cli.py               # CLI entry point
│   ├── builder.py           # Core build logic
│   └── config.py            # Configuration management
├── templates/               # Unchanged
├── public/                  # Unchanged
│   ├── content/
│   └── static/
├── main.py                  # Simple entry: from malvolio.cli import main; main()
└── pyproject.toml           # Add CLI script entry point
```

**Rationale**: Three small modules keep responsibilities clear without creating a deep hierarchy. The package approach allows future extension without restructuring.

### 2. Module Breakdown

#### [`malvolio/config.py`](malvolio/config.py) - Configuration
```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    """Site configuration with sensible defaults."""
    templates_dir: Path = Path("templates")
    public_dir: Path = Path("public")
    content_dir: Path = Path("public/content")
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(**{k: Path(v) for k, v in data.items()})
    
    @property
    def output_files(self) -> list[Path]:
        """List of generated output files."""
        return [
            self.public_dir / "index.html",
            self.public_dir / "thought.html",
            self.public_dir / "experience.html",
        ]
```

#### [`malvolio/builder.py`](malvolio/builder.py) - Build Logic
```python
from pathlib import Path
import jinja2
import yaml
from .config import Config

class Builder:
    """Static site builder with clean output management."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config.templates_dir)
        )
    
    def clean(self) -> None:
        """Remove all generated files."""
        for file in self.config.output_files:
            file.unlink(missing_ok=True)
    
    def build(self) -> None:
        """Build all pages."""
        self.clean()
        self._render_index()
        self._render_content_pages()
    
    def _render_index(self) -> None:
        # ... existing index logic
    
    def _render_content_pages(self) -> None:
        # ... existing page rendering logic
```

#### [`malvolio/cli.py`](malvolio/cli.py) - CLI Interface
```python
import argparse
import sys
from .builder import Builder
from .config import Config

def main():
    parser = argparse.ArgumentParser(description="Malvolio Static Site Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # build command
    subparsers.add_parser("build", help="Build the site")
    
    # serve command
    serve_parser = subparsers.add_parser("serve", help="Serve with live reload")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--no-watch", action="store_true", 
                              help="Disable file watching")
    
    args = parser.parse_args()
    
    if args.command == "build":
        Builder().build()
        print("Site built successfully.")
    elif args.command == "serve":
        serve(port=args.port, watch=not args.no_watch)

def serve(port: int, watch: bool):
    """Start development server with optional file watching."""
    # Implementation details in section 5
    pass

if __name__ == "__main__":
    main()
```

### 3. CLI Interface Design

**Commands:**

| Command | Description |
|---------|-------------|
| `malvolio build` | Build the site once |
| `malvolio serve` | Start dev server with live reload |
| `malvolio serve --no-watch` | Serve without file watching |
| `malvolio serve --port 3000` | Use custom port |

**pyproject.toml entry point:**
```toml
[project.scripts]
malvolio = "malvolio.cli:main"
```

### 4. Configuration Approach

**Keep it simple with dataclasses:**

- Use a `Config` dataclass with sensible defaults
- No external config files needed (YAML/JSON) - adds complexity
- If configuration is needed later, add a `malvolio.yaml` or use environment variables

**Why not a config file?**
- Current project has ~4 paths and no settings
- A config file would add indirection without benefit
- Dataclass defaults are self-documenting and type-safe

### 5. Development Server Approach

**Recommended: Python's built-in http.server + livereload**

```python
# In cli.py
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

def serve(port: int, watch: bool):
    """Start development server."""
    builder = Builder()
    builder.build()  # Initial build
    
    if watch:
        # Start file watcher in background thread
        watcher = FileWatcher(
            paths=["templates", "public/content"],
            callback=lambda: builder.build()
        )
        watcher.start()
    
    # Start HTTP server
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="public", **kwargs)
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        webbrowser.open(f"http://localhost:{port}")
        httpd.serve_forever()
```

**Alternative: Use the `livereload` package**

If browser auto-refresh is desired, use the `livereload` package:

```python
from livereload import Server

def serve(port: int, watch: bool):
    builder = Builder()
    builder.build()
    
    server = Server()
    
    if watch:
        server.watch("templates/", builder.build)
        server.watch("public/content/", builder.build)
    
    server.serve(port=port, root="public")
```

**Recommendation**: Start with `livereload` package - it provides both file watching and browser auto-refresh with minimal code.

### 6. File Watching Strategy

**Option A: livereload package (Recommended)**
- Already handles watching and browser reload
- Simple API: `server.watch(path, callback)`
- Add dependency: `livereload>=2.6.3`

**Option B: watchdog package**
- More powerful but requires more code
- Better if complex watching logic needed
- Overkill for this project

**Option C: Polling**
- Simple but inefficient
- Only use if no dependencies allowed

**Implementation with livereload:**
```python
from livereload import Server
from pathlib import Path

def serve(port: int, watch: bool):
    builder = Builder()
    builder.build()
    
    server = Server()
    
    if watch:
        # Watch templates
        server.watch("templates/", lambda: builder.build())
        # Watch content directories
        server.watch("public/content/", lambda: builder.build())
    
    print(f"Server running at http://localhost:{port}")
    server.serve(port=port, root="public")
```

### 7. Content Management

**Current approach: HTML files + meta.yaml**

The current system works well:
- Content is HTML (full control over markup)
- Metadata in YAML (structured data for listings)
- Already has dependencies: `markdown` and `python-frontmatter` in pyproject.toml

**Recommendation: Keep current approach, add Markdown support as option**

Why keep HTML:
- Full control over markup
- No abstraction leakage
- Simple mental model

Optional Markdown enhancement:
```python
# In builder.py, add a method to detect and process markdown
def _load_content(self, path: Path) -> str:
    """Load content file, converting markdown if needed."""
    if path.suffix == ".md":
        import markdown
        with open(path) as f:
            return markdown.markdown(f.read())
    else:
        return path.read_text()
```

**For new content files, consider frontmatter:**
```markdown
---
heading: "What is Innocence"
date: "01-08-2016"
summary: "I don't know what is knowing but..."
---

# What is Innocence

Actual content here in **markdown**...
```

This would allow:
- Single file per content item (no separate meta.yaml needed)
- Markdown authoring
- Still works with existing HTML files

---

## Implementation Priority

### Phase 1: Core Improvements
1. Split into modules (config, builder, cli)
2. Add CLI interface with `build` command
3. Improve `clean()` to be comprehensive

### Phase 2: Development Experience
4. Add `serve` command with `livereload`
5. Add file watching for templates and content
6. Browser auto-refresh on rebuild

### Phase 3: Optional Enhancements
7. Markdown support for content files
8. Frontmatter support for single-file content

---

## Dependencies

**Add:**
```toml
[project.dependencies]
# Existing
jinja2 = ">=3.1.6"
markdown = ">=3.10.1"
python-frontmatter = ">=1.1.0"
pyyaml = ">=6.0.3"
# New
livereload = ">=2.6.3"  # For dev server with auto-reload
```

---

## Summary

| Issue | Solution |
|-------|----------|
| No live preview | Add `serve` command with `livereload` |
| No file watching | `livereload` handles watching + browser refresh |
| Hardcoded paths | `Config` dataclass with defaults |
| Incomplete cleanup | `clean()` iterates over output files list |
| No CLI interface | `argparse` with `build` and `serve` commands |
| Mixed concerns | Split into config/builder/cli modules |

**Key principle**: Each improvement solves a real pain point without adding unnecessary abstraction. The total code increase is minimal (~100-150 lines) while significantly improving the development workflow.
