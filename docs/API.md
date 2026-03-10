# API Reference

## WindowManager

The core class for managing Windows windows.

### `get_all_windows(visible_only: bool = True) -> List[WindowInfo]`

Retrieves all open windows.

- **Parameters**:
  - `visible_only` (bool): If `True`, only returns visible windows. Defaults to `True`.
- **Returns**:
  - A list of `WindowInfo` objects.

### `find_windows(title: Optional[str] = None, class_name: Optional[str] = None, exact_match: bool = False) -> List[WindowInfo]`

Finds windows matching the given criteria.

- **Parameters**:
  - `title` (str, optional): The window title to search for.
  - `class_name` (str, optional): The window class name to search for.
  - `exact_match` (bool): If `True`, requires exact string match. Otherwise, checks for containment. Defaults to `False`.
- **Returns**:
  - A list of matching `WindowInfo` objects.

### `get_window_by_handle(handle: int) -> Optional[WindowInfo]`

Retrieves window information by handle.

- **Parameters**:
  - `handle` (int): The window handle.
- **Returns**:
  - A `WindowInfo` object if found, otherwise `None`.

### Window Controls

- `close_window(handle: int) -> bool`: Closes the window.
- `minimize_window(handle: int) -> bool`: Minimizes the window.
- `maximize_window(handle: int) -> bool`: Maximizes the window.
- `restore_window(handle: int) -> bool`: Restores the window.
- `move_window(handle: int, x: int, y: int, width: int, height: int) -> bool`: Moves and resizes the window.
- `set_foreground(handle: int) -> bool`: Brings the window to the foreground.

## WindowInfo

A dataclass representing window information.

- **Attributes**:
  - `handle` (int): The window handle (HWND).
  - `title` (str): The window title.
  - `class_name` (str): The window class name.
  - `pid` (int): The process ID associated with the window.
  - `process_name` (str, optional): The name of the process.
  - `rect` (tuple, optional): The window rectangle (left, top, right, bottom).
  - `is_visible` (bool): Whether the window is visible.

## WindowMonitor

Monitors window events such as creation, destruction, and state changes.

### `__init__(callback: Optional[Callable[[str, int, str], None]] = None)`

Initializes the monitor.

- **Parameters**:
  - `callback`: A function to call when an event occurs. Signature: `callback(event_name, hwnd, title)`.

### `start()`

Starts the monitoring thread.

### `stop()`

Stops the monitoring thread.

## Events

The following events are monitored:
- `Create`: Window created.
- `Destroy`: Window destroyed.
- `Show`: Window shown.
- `Hide`: Window hidden.
- `Foreground`: Window became foreground.
- `NameChange`: Window title changed.
