"""
memory_brain.py

Lilly's long-term reasoning memory.
"""

class MemoryBrain:

    def __init__(self, memory):
        self.memory = memory

    def remember(self, fact):
        if fact not in self.memory["facts"]:
            self.memory["facts"].append(fact)

    def recall(self):
        return self.memory["facts"]

    def has_memory(self):
        return len(self.memory["facts"]) > 0
