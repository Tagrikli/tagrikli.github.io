"""Configuration management for Malvolio."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageConfig:
    """Configuration for a single page type."""
    name: str
    meta_file: Path
    content_dir: str  # URL path for hrefs (e.g., "content/thought")
    template: str
    output_file: Path
    source_dir: Path  # Source directory for content files


@dataclass
class Config:
    """Site configuration with sensible defaults."""
    
    # Directory paths
    templates_dir: Path = field(default_factory=lambda: Path("templates"))
    public_dir: Path = field(default_factory=lambda: Path("docs"))
    source_dir: Path = field(default_factory=lambda: Path("content"))
    
    # Output files
    index_output: Path = field(default_factory=lambda: Path("docs/index.html"))
    
    # Page configurations
    pages: list[PageConfig] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default page configurations if not provided."""
        if not self.pages:
            self.pages = [
                PageConfig(
                    name="thought",
                    meta_file=self.source_dir / "thought" / "meta.yaml",
                    content_dir="content/thought",
                    template="thought.html",
                    output_file=self.public_dir / "thought.html",
                    source_dir=self.source_dir / "thought",
                ),
                PageConfig(
                    name="experience",
                    meta_file=self.source_dir / "experience" / "meta.yaml",
                    content_dir="content/experience",
                    template="experience.html",
                    output_file=self.public_dir / "experience.html",
                    source_dir=self.source_dir / "experience",
                ),
            ]
    
    @property
    def output_files(self) -> list[Path]:
        """List of all output files that should be cleaned."""
        return [self.index_output] + [page.output_file for page in self.pages]
    
    @property
    def output_dirs(self) -> list[Path]:
        """List of output directories that should be cleaned."""
        return [self.public_dir / "content"]
    
    @property
    def watch_paths(self) -> list[Path]:
        """List of paths to watch for changes."""
        return [
            self.templates_dir,
            self.source_dir,
        ]
