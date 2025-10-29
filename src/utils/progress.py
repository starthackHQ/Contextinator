class ProgressTracker:
    """Simple progress tracker for chunking operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, n: int = 1):
        """Update progress by n steps."""
        self.current += n
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%)", end='', flush=True)
    
    def finish(self):
        """Mark progress as complete."""
        print()  # New line after progress
