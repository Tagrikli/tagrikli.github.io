# Malvolio

A minimal static site generator for personal webpages.

## Installation

```bash
uv sync
```

## Usage

### Build the site

```bash
uv run malvolio build
```

Options:
- `--clean` - Clean output files before building

### Development server with live reload

```bash
uv run malvolio serve
```

Options:
- `--port PORT` - Port to serve on (default: 8000)

The server will automatically rebuild the site when you modify templates or content files.

## Project Structure

```
malvolio/
├── config.py      # Configuration management
├── builder.py     # Core build logic
└── cli.py         # Command-line interface

templates/         # Jinja2 HTML templates
├── base.html
├── index.html
├── thought.html
└── experience.html

content/           # Source content (edit these files)
├── thought/
│   ├── meta.yaml
│   └── *.html
└── experience/
    ├── meta.yaml
    └── *.html

public/            # Generated output (don't edit)
├── index.html
├── thought.html
├── experience.html
├── content/       # Rendered content pages
│   ├── thought/
│   └── experience/
└── static/        # Static assets
    ├── css/
    └── media/
```

## Adding Content

1. Create a new HTML file in the appropriate content directory (e.g., `content/thought/my-article.html`)
2. Add an entry in the corresponding `meta.yaml` file:

```yaml
my-article:
  heading: "My Article Title"
  date: "2024-01-15"
  summary: "A brief description of the article"
```

3. Run `uv run malvolio build` or use `uv run malvolio serve` for live preview.

## How It Works

- **List pages** (`thought.html`, `experience.html`) are rendered from `meta.yaml` using their respective templates
- **Individual content pages** are wrapped in `base.html` template automatically
- Source files in `content/` are never modified; output goes to `public/`
