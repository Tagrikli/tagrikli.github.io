"""Core build logic for Malvolio static site generator."""

import os
import re
import shutil
from pathlib import Path

import jinja2
import yaml

from .config import Config, PageConfig


class SiteBuilder:
    """Builds the static site from templates and content."""

    def __init__(self, config: Config | None = None):
        """Initialize the builder with configuration.
        
        Args:
            config: Site configuration. Uses defaults if not provided.
        """
        self.config = config or Config()
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config.templates_dir)
        )

    def clean(self) -> None:
        """Remove all generated output files and directories."""
        # Remove output files
        for output_file in self.config.output_files:
            output_file.unlink(missing_ok=True)
            print(f"Removed: {output_file}")
        
        # Remove output directories
        for output_dir in self.config.output_dirs:
            if output_dir.exists():
                shutil.rmtree(output_dir)
                print(f"Removed: {output_dir}")

    def build(self) -> None:
        """Build the complete site."""
        self._render_index()
        self._render_music()
        for page in self.config.pages:
            self._render_page(page)
        print("Build complete.")

    def rebuild(self) -> None:
        """Clean and rebuild the complete site."""
        self.clean()
        self.build()

    def _render_index(self) -> None:
        """Render the index page."""
        base_template = self.env.get_template("base.html")
        index_content_template = self.env.get_template("index.html")
        index_content = index_content_template.render()
        rendered_html = base_template.render(content=index_content)
        
        self._write_output(self.config.index_output, rendered_html)
        print(f"Rendered: {self.config.index_output}")

    def _render_music(self) -> None:
        """Render the music page."""
        base_template = self.env.get_template("base.html")
        music_content_template = self.env.get_template("music.html")
        music_content = music_content_template.render()
        rendered_html = base_template.render(content=music_content)
        
        music_output = self.config.public_dir / "music.html"
        self._write_output(music_output, rendered_html)
        print(f"Rendered: {music_output}")

    def _render_page(self, page: PageConfig) -> None:
        """Render a single page from its configuration.
        
        Args:
            page: Page configuration containing meta file, template, etc.
        """
        if not os.path.exists(page.meta_file):
            print(f"Warning: Meta file {page.meta_file} not found, skipping.")
            return

        # Load meta.yaml
        with open(page.meta_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Handle empty meta.yaml - render page with empty items
        if not data:
            print(f"Warning: {page.meta_file} is empty, rendering with no items.")
            data = {}

        # Extract items as list of dicts with href
        keys = list(data.keys())
        items = list(data.values())

        # Collect all unique tags
        all_tags = set()
        for item in items:
            if "tags" in item:
                all_tags.update(item["tags"])
        all_tags = sorted(list(all_tags))

        for item, key in zip(items, keys):
            item["href"] = f"{page.content_dir}/{key}.html"
            # Calculate reading time from content file
            source_file = page.source_dir / f"{key}.html"
            if source_file.exists():
                with open(source_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Strip HTML tags for word count
                text = re.sub(r"<[^>]+>", "", content)
                word_count = len(text.split())
                reading_time = max(1, round(word_count / 220))
                item["reading_time"] = reading_time
            else:
                item["reading_time"] = 1

        # Render the page content
        page_template = self.env.get_template(page.template)
        content_html = page_template.render(items=items, all_tags=all_tags)

        # Render the base template
        base_template = self.env.get_template("base.html")
        rendered_html = base_template.render(content=content_html)

        self._write_output(page.output_file, rendered_html)
        print(f"Rendered: {page.output_file}")
        
        # Render individual content pages
        self._render_content_pages(page, keys, items)

    def _render_content_pages(self, page: PageConfig, keys: list, items: list) -> None:
        """Render individual content pages wrapped in base template.
        
        Args:
            page: Page configuration.
            keys: List of content keys (slugs).
            items: List of content items with metadata.
        """
        base_template = self.env.get_template("base.html")
        
        for key, item in zip(keys, items):
            source_file = page.source_dir / f"{key}.html"
            output_file = self.config.public_dir / page.content_dir / f"{key}.html"
            
            if not os.path.exists(source_file):
                print(f"Warning: Content file {source_file} not found, skipping.")
                continue
            
            # Read the raw HTML content
            with open(source_file, "r", encoding="utf-8") as f:
                raw_content = f.read()
            
            # Wrap in base template
            rendered_html = base_template.render(content=raw_content)
            
            # Write to output directory
            self._write_output(output_file, rendered_html)
            print(f"Rendered: {output_file}")

    def _write_output(self, path: Path, content: str) -> None:
        """Write content to an output file.
        
        Args:
            path: Output file path.
            content: HTML content to write.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
