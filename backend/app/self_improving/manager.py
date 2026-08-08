"""
Self-Improving Manager Module
Core logic for learning signals, self-reflection, and memory promotion/demotion.
"""

import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from .storage import SelfImprovingStorage


class SelfImprovingManager:
    """Manages self-improving learning and memory operations."""
    
    def __init__(self, storage: Optional[SelfImprovingStorage] = None):
        self.storage = storage or SelfImprovingStorage()
        
        # Learning signal patterns (from SKILL.md)
        self.correction_patterns = [
            # English patterns
            r"no,\s+that's\s+not\s+right",
            r"actually,\s+it\s+should\s+be",
            r"you're\s+wrong\s+about",
            r"i\s+prefer\s+\w+,\s+not\s+\w+",
            r"remember\s+that\s+i\s+always",
            r"i\s+told\s+you\s+before",
            r"stop\s+doing\s+\w+",
            r"why\s+do\s+you\s+keep",
            # Chinese patterns
            r"不[，,]\s*(那|这).*(不对|错了|不正确)",
            r"其实.*应该",
            r"你.*(错|搞错|弄错)了",
            r"我.*(告诉|说)过你",
            r"别.*再",
            r"停止.*做",
            r"不要.*做",
        ]
        
        self.preference_patterns = [
            # English patterns
            r"i\s+like\s+when\s+you",
            r"always\s+do\s+\w+\s+for\s+me",
            r"never\s+do\s+\w+",
            r"my\s+style\s+is",
            r"for\s+\[?\w+\]?,\s+use",
            # Chinese patterns
            r"我.*喜欢.*你",
            r"总是.*为我",
            r"永远.*不要",
            r"我的.*风格.*是",
            r"对于.*使用",
            r"我.*偏好",
            r"我.*更.*喜欢",
        ]
    
    def detect_learning_signal(self, user_message: str) -> Optional[Dict]:
        """
        Detect if user message contains a learning signal.
        Returns signal type and matched text if found.
        """
        message_lower = user_message.lower()
        
        # Check for corrections
        for pattern in self.correction_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return {
                    "type": "correction",
                    "matched_text": match.group(0),
                    "full_message": user_message,
                    "confidence": "high"
                }
        
        # Check for preferences
        for pattern in self.preference_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return {
                    "type": "preference",
                    "matched_text": match.group(0),
                    "full_message": user_message,
                    "confidence": "confirmed"
                }
        
        return None
    
    def log_correction(self, correction_text: str, context: str = "", 
                      correction_type: str = "communication"):
        """
        Log a user correction to corrections.md.
        
        Args:
            correction_text: The corrected information
            context: Where/context of the correction
            correction_type: Type (format, technical, communication, project-specific)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = f"""### {timestamp} — {correction_type.title()}
- **Correction:** "{correction_text}"
- **Context:** {context}
- **Count:** 1 (first occurrence)
"""
        
        self.storage.append_to_corrections(entry)
    
    def log_preference(self, preference_text: str, scope: str = "global"):
        """
        Log an explicit user preference to memory.md.
        
        Args:
            preference_text: The preference statement
            scope: global, domain, or project
        """
        current_memory = self.storage.read_hot_memory()
        
        # Add to appropriate section
        if "## Confirmed Preferences" in current_memory:
            # Insert after the header
            lines = current_memory.split('\n')
            new_lines = []
            inserted = False
            
            for line in lines:
                new_lines.append(line)
                if line.strip() == "## Confirmed Preferences" and not inserted:
                    timestamp = datetime.now().strftime("%Y-%m")
                    new_lines.append(f"- {preference_text} (confirmed {timestamp})")
                    inserted = True
            
            updated_memory = '\n'.join(new_lines)
        else:
            # Append to end
            timestamp = datetime.now().strftime("%Y-%m")
            updated_memory = current_memory + f"\n\n## Confirmed Preferences\n- {preference_text} (confirmed {timestamp})\n"
        
        self.storage.write_hot_memory(updated_memory)
    
    def log_self_reflection(self, task_type: str, reflection: str, lesson: str,
                           outcome: str = "partial"):
        """
        Log a self-reflection entry after completing significant work.
        
        Args:
            task_type: Type of task (e.g., "Building Flutter UI")
            reflection: What was noticed about the work
            lesson: What to do differently next time
            outcome: success, partial, or failed
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        reflection_entry = f"""## {timestamp} — {task_type}

**What I did:** Completed {task_type.lower()}
**Outcome:** {outcome}
**Reflection:** {reflection}
**Lesson:** {lesson}
**Status:** ⏳ candidate
"""
        
        # For now, append to corrections as a special type
        # In future, could have dedicated reflections.md
        self.storage.append_to_corrections(reflection_entry)
    
    def get_memory_for_context(self, context_hint: str = "") -> str:
        """
        Load relevant memory based on context.
        
        Args:
            context_hint: Hint about current context (project name, domain, etc.)
        
        Returns:
            Combined memory content to inject into conversation
        """
        # Always load HOT memory
        hot_memory = self.storage.read_hot_memory()
        
        context_memory = ""
        
        # If context hint provided, try to load relevant WARM memory
        if context_hint:
            # Check if it's a project reference
            project_memory = self.storage.get_project_memory(context_hint)
            if project_memory:
                context_memory += f"\n\n# Project Context ({context_hint})\n{project_memory}\n"
            
            # Check common domains
            for domain in ["code", "writing", "communication"]:
                domain_memory = self.storage.get_domain_memory(domain)
                if domain_memory:
                    context_memory += f"\n\n# Domain Context ({domain})\n{domain_memory}\n"
        
        return hot_memory + context_memory
    
    def promote_pattern(self, pattern_text: str, source: str = "corrections"):
        """
        Promote a pattern from corrections to HOT memory after repeated use.
        
        Args:
            pattern_text: The pattern to promote
            source: Where it came from (corrections, reflections, etc.)
        """
        current_memory = self.storage.read_hot_memory()
        
        # Add to Active Patterns section
        if "## Active Patterns" in current_memory:
            lines = current_memory.split('\n')
            new_lines = []
            inserted = False
            
            for line in lines:
                new_lines.append(line)
                if line.strip() == "## Active Patterns" and not inserted:
                    new_lines.append(f"- {pattern_text} (promoted from {source})")
                    inserted = True
            
            updated_memory = '\n'.join(new_lines)
        else:
            timestamp = datetime.now().strftime("%Y-%m")
            updated_memory = current_memory + f"\n\n## Active Patterns\n- {pattern_text} (promoted {timestamp})\n"
        
        self.storage.write_hot_memory(updated_memory)
    
    def forget_topic(self, topic: str) -> bool:
        """
        Remove all mentions of a topic from memory tiers.
        
        Args:
            topic: The topic to forget
        
        Returns:
            True if something was removed, False otherwise
        """
        removed = False
        
        # Search and remove from HOT memory
        hot_memory = self.storage.read_hot_memory()
        if topic.lower() in hot_memory.lower():
            # Simple removal - can be enhanced with smarter filtering
            lines = hot_memory.split('\n')
            filtered_lines = [line for line in lines if topic.lower() not in line.lower()]
            updated_memory = '\n'.join(filtered_lines)
            self.storage.write_hot_memory(updated_memory)
            removed = True
        
        # TODO: Implement removal from WARM and COLD tiers
        
        return removed
    
    def run_heartbeat(self):
        """
        Run heartbeat maintenance: promote/demote memories, compact files.
        This should be called periodically (e.g., daily).
        """
        # Update heartbeat state
        timestamp = datetime.now().isoformat()
        heartbeat_content = f"""# Self-Improving Heartbeat State

last_heartbeat_started_at: {timestamp}
last_reviewed_change_at: {timestamp}
last_heartbeat_result: HEARTBEAT_OK

## Last actions
- Heartbeat run at {timestamp}
- No material changes detected
"""
        self.storage.heartbeat_file.write_text(heartbeat_content, encoding='utf-8')
        
        # TODO: Implement actual promotion/demotion logic
        # - Scan corrections for patterns used 3x in 7 days → promote to HOT
        # - Scan HOT for patterns unused 30 days → demote to WARM
        # - Compact oversized files
    
    def get_stats(self) -> Dict:
        """Get comprehensive memory statistics."""
        return self.storage.get_memory_stats()
