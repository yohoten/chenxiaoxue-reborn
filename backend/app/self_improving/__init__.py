"""
Self-Improving Module for ChenXiaoxue AI Assistant

This module implements a tiered memory system that allows the AI assistant
to learn from user corrections, store preferences, and improve over time.

Architecture:
- HOT tier (memory.md): Always loaded, ≤100 lines
- WARM tier (projects/, domains/): Loaded on context match
- COLD tier (archive/): Archived patterns, loaded on explicit query
"""

from .storage import SelfImprovingStorage
from .manager import SelfImprovingManager

# Singleton instance for easy access
_storage_instance = None
_manager_instance = None


def get_storage() -> SelfImprovingStorage:
    """Get or create the storage singleton."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = SelfImprovingStorage()
    return _storage_instance


def get_manager() -> SelfImprovingManager:
    """Get or create the manager singleton."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SelfImprovingManager(get_storage())
    return _manager_instance


__all__ = ['SelfImprovingStorage', 'SelfImprovingManager', 'get_storage', 'get_manager']
