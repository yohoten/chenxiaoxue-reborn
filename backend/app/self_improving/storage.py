"""
Self-Improving Storage Module
Manages HOT/WARM/COLD tiered memory storage.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class SelfImprovingStorage:
    """Manages the self-improving memory file system."""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to backend/app/self_improving/
            self.base_dir = Path(__file__).parent
        else:
            self.base_dir = Path(base_dir)
        
        # Ensure directories exist
        self.projects_dir = self.base_dir / "projects"
        self.domains_dir = self.base_dir / "domains"
        self.archive_dir = self.base_dir / "archive"
        
        for dir_path in [self.projects_dir, self.domains_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Core files
        self.memory_file = self.base_dir / "memory.md"  # HOT
        self.corrections_file = self.base_dir / "corrections.md"
        self.index_file = self.base_dir / "index.md"
        self.heartbeat_file = self.base_dir / "heartbeat-state.md"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize core memory files with templates if they don't exist."""
        if not self.memory_file.exists():
            self.memory_file.write_text(self._get_memory_template())
        
        if not self.corrections_file.exists():
            self.corrections_file.write_text(self._get_corrections_template())
        
        if not self.index_file.exists():
            self.index_file.write_text(self._get_index_template())
        
        if not self.heartbeat_file.exists():
            self.heartbeat_file.write_text(self._get_heartbeat_template())
    
    def _get_memory_template(self) -> str:
        return """# Self-Improving Memory (HOT Tier)

## Confirmed Preferences
<!-- Patterns confirmed by user, never decay -->

## Active Patterns
<!-- Patterns observed 3+ times, subject to decay -->

## Recent (last 7 days)
<!-- New corrections pending confirmation -->
"""
    
    def _get_corrections_template(self) -> str:
        return """# Corrections Log

| Date | What I Got Wrong | Correct Answer | Status |
|------|-----------------|----------------|--------|
"""
    
    def _get_index_template(self) -> str:
        return """# Memory Index

| File | Lines | Last Updated |
|------|-------|--------------|
| memory.md | 0 | — |
| corrections.md | 0 | — |
"""
    
    def _get_heartbeat_template(self) -> str:
        return """# Self-Improving Heartbeat State

last_heartbeat_started_at: never
last_reviewed_change_at: never
last_heartbeat_result: never

## Last actions
- none yet
"""
    
    def read_hot_memory(self) -> str:
        """Read HOT tier memory (memory.md)."""
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding='utf-8')
        return ""
    
    def write_hot_memory(self, content: str):
        """Write to HOT tier memory (memory.md)."""
        self.memory_file.write_text(content, encoding='utf-8')
        self._update_index("memory.md")
    
    def append_to_corrections(self, entry: str):
        """Append a correction entry to corrections.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_entry = f"\n## {timestamp}\n{entry}\n"
        
        with open(self.corrections_file, 'a', encoding='utf-8') as f:
            f.write(full_entry)
        
        self._update_index("corrections.md")
    
    def read_corrections(self, limit: int = 50) -> str:
        """Read recent corrections (last N entries)."""
        if not self.corrections_file.exists():
            return ""
        
        content = self.corrections_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Return last N lines
        return '\n'.join(lines[-limit:])
    
    def get_project_memory(self, project_name: str) -> str:
        """Read WARM tier project-specific memory."""
        project_file = self.projects_dir / f"{project_name}.md"
        if project_file.exists():
            return project_file.read_text(encoding='utf-8')
        return ""
    
    def write_project_memory(self, project_name: str, content: str):
        """Write to WARM tier project-specific memory."""
        project_file = self.projects_dir / f"{project_name}.md"
        project_file.write_text(content, encoding='utf-8')
        self._update_index(f"projects/{project_name}.md")
    
    def get_domain_memory(self, domain_name: str) -> str:
        """Read WARM tier domain-specific memory."""
        domain_file = self.domains_dir / f"{domain_name}.md"
        if domain_file.exists():
            return domain_file.read_text(encoding='utf-8')
        return ""
    
    def write_domain_memory(self, domain_name: str, content: str):
        """Write to WARM tier domain-specific memory."""
        domain_file = self.domains_dir / f"{domain_name}.md"
        domain_file.write_text(content, encoding='utf-8')
        self._update_index(f"domains/{domain_name}.md")
    
    def archive_memory(self, source_file: str, reason: str = ""):
        """Move memory from WARM to COLD (archive)."""
        # Implementation for archiving old memories
        pass
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about memory tiers."""
        stats = {
            "hot": {
                "file": "memory.md",
                "lines": self._count_lines(self.memory_file),
                "size_kb": self._get_file_size_kb(self.memory_file)
            },
            "warm": {
                "projects": self._count_files(self.projects_dir),
                "domains": self._count_files(self.domains_dir)
            },
            "cold": {
                "archived": self._count_files(self.archive_dir)
            },
            "corrections": {
                "entries": self._count_entries(self.corrections_file)
            }
        }
        return stats
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        if not file_path.exists():
            return 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0
    
    def _get_file_size_kb(self, file_path: Path) -> float:
        """Get file size in KB."""
        if not file_path.exists():
            return 0.0
        return file_path.stat().st_size / 1024
    
    def _count_files(self, directory: Path) -> int:
        """Count markdown files in a directory."""
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.md")))
    
    def _count_entries(self, file_path: Path) -> int:
        """Count correction entries (lines starting with ##)."""
        if not file_path.exists():
            return 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.strip().startswith('##'))
        except:
            return 0
    
    def _update_index(self, file_name: str):
        """Update index.md with file metadata."""
        # Simple implementation - can be enhanced
        pass
    
    def search_memory(self, query: str) -> List[Dict]:
        """Search across all memory tiers for relevant content."""
        results = []
        
        # Search HOT memory
        hot_content = self.read_hot_memory()
        if query.lower() in hot_content.lower():
            results.append({
                "tier": "HOT",
                "source": "memory.md",
                "content": hot_content[:200] + "..." if len(hot_content) > 200 else hot_content
            })
        
        # Search corrections
        corrections = self.read_corrections()
        if query.lower() in corrections.lower():
            results.append({
                "tier": "HOT",
                "source": "corrections.md",
                "content": corrections[:200] + "..." if len(corrections) > 200 else corrections
            })
        
        # Search WARM tier (projects and domains)
        for md_file in self.projects_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                results.append({
                    "tier": "WARM",
                    "source": f"projects/{md_file.name}",
                    "content": content[:200] + "..." if len(content) > 200 else content
                })
        
        for md_file in self.domains_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                results.append({
                    "tier": "WARM",
                    "source": f"domains/{md_file.name}",
                    "content": content[:200] + "..." if len(content) > 200 else content
                })
        
        return results
