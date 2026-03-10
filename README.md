# Windows Window Manager

A Python library for managing Windows windows using `win32gui` and `ctypes`. This project provides a robust interface for identifying, controlling, and monitoring windows on Windows systems.

## Features

- **Window Identification**: Get detailed information about all open windows (Handle, Title, Class Name, PID, Process Name).
- **Window Search**: Find windows by title or class name with exact or partial matching.
- **Window Control**:
  - Minimize, Maximize, Restore
  - Close
  - Move and Resize
  - Set to Foreground
- **Real-time Monitoring**: Monitor window creation, destruction, and state changes.
- **Robust Error Handling**: Handles permissions and invalid handles gracefully.

## Installation

This project uses `uv` for dependency management.

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv sync
    ```

## Usage

### Basic Example

```python
from window_manager import WindowManager

manager = WindowManager()

# List all visible windows
windows = manager.get_all_windows(visible_only=True)
for window in windows:
    print(window)

# Find a window
notepad = manager.find_windows(title="Notepad")[0]

# Minimize
manager.minimize_window(notepad.handle)

# Restore
manager.restore_window(notepad.handle)
```

### Monitoring Example

```python
import time
from window_manager import WindowMonitor

def callback(event, hwnd, title):
    print(f"Event: {event}, Window: {title}")

monitor = WindowMonitor(callback=callback)
monitor.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
```

## Running Tests

```bash
uv run pytest tests
```

## Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.
