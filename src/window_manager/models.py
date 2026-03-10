from dataclasses import dataclass
from typing import Optional

@dataclass
class WindowInfo:
    """
    Represents information about a window.
    """
    handle: int
    title: str
    class_name: str
    pid: int
    process_name: Optional[str] = None
    rect: Optional[tuple[int, int, int, int]] = None  # (left, top, right, bottom)
    is_visible: bool = False
    
    def __str__(self):
        return (f"Window(handle={self.handle}, title='{self.title}', "
                f"class='{self.class_name}', pid={self.pid}, "
                f"process='{self.process_name}')")
