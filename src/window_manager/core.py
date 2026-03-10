import logging
import win32gui
import win32process
import win32con
import psutil
from typing import List, Optional, Tuple, Dict, Any
from .models import WindowInfo
from .utils import setup_logger

logger = setup_logger()

class WindowManagerError(Exception):
    """Base exception for WindowManager errors."""
    pass

class WindowManager:
    """
    Core class for managing Windows windows.
    """
    
    def __init__(self):
        """Initializes the WindowManager."""
        self._logger = logger
    
    def get_all_windows(self, visible_only: bool = True) -> List[WindowInfo]:
        """
        Retrieves all open windows.
        
        Args:
            visible_only: If True, only returns visible windows.
            
        Returns:
            A list of WindowInfo objects.
        """
        windows: List[WindowInfo] = []
        
        def enum_handler(hwnd, ctx):
            if visible_only and not win32gui.IsWindowVisible(hwnd):
                return
            
            try:
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # Get process ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # Get process name
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    process_name = "Unknown"
                
                # Get window rect
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                except Exception:
                    rect = None
                
                window_info = WindowInfo(
                    handle=hwnd,
                    title=title,
                    class_name=class_name,
                    pid=pid,
                    process_name=process_name,
                    rect=rect,
                    is_visible=win32gui.IsWindowVisible(hwnd)
                )
                windows.append(window_info)
            except Exception as e:
                self._logger.warning(f"Error processing window {hwnd}: {e}")
            
        try:
            win32gui.EnumWindows(enum_handler, None)
        except Exception as e:
            self._logger.error(f"Failed to enumerate windows: {e}")
            raise WindowManagerError(f"Failed to enumerate windows: {e}")
            
        return windows

    def find_windows(self, title: Optional[str] = None, class_name: Optional[str] = None, process_name: Optional[str] = None, exact_match: bool = False) -> List[WindowInfo]:
        """
        Finds windows matching the given criteria.
        
        Args:
            title: The window title to search for.
            class_name: The window class name to search for.
            exact_match: If True, requires exact string match. Otherwise, checks for containment.
            
        Returns:
            A list of matching WindowInfo objects.
        """
        all_windows = self.get_all_windows(visible_only=False)
        matched_windows = []
        
        for window in all_windows:
            match = True
            
            if title:
                if exact_match:
                    if window.title != title:
                        match = False
                else:
                    if title.lower() not in window.title.lower():
                        match = False
            
            if match and class_name:
                if exact_match:
                    if window.class_name != class_name:
                        match = False
                else:
                    if class_name.lower() not in window.class_name.lower():
                        match = False
            
            if match and process_name:
                if window.process_name is None or window.process_name.lower() != process_name.lower():
                    match = False
            
            if match and (title or class_name or process_name):
                matched_windows.append(window)
                
        return matched_windows

    def get_window_by_handle(self, handle: int) -> Optional[WindowInfo]:
        """
        Retrieves window information by handle.
        
        Args:
            handle: The window handle.
            
        Returns:
            A WindowInfo object if found, otherwise None.
        """
        if not win32gui.IsWindow(handle):
            return None
            
        try:
            title = win32gui.GetWindowText(handle)
            class_name = win32gui.GetClassName(handle)
            _, pid = win32process.GetWindowThreadProcessId(handle)
            
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                process_name = "Unknown"
                
            try:
                rect = win32gui.GetWindowRect(handle)
            except Exception:
                rect = None

            return WindowInfo(
                handle=handle,
                title=title,
                class_name=class_name,
                pid=pid,
                process_name=process_name,
                rect=rect,
                is_visible=win32gui.IsWindowVisible(handle)
            )
        except Exception as e:
            self._logger.error(f"Error getting window info for handle {handle}: {e}")
            return None

    def close_window(self, handle: int) -> bool:
        """Closes the window with the given handle."""
        try:
            win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
            self._logger.info(f"Closed window {handle}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to close window {handle}: {e}")
            return False

    def minimize_window(self, handle: int) -> bool:
        """Minimizes the window."""
        try:
            win32gui.ShowWindow(handle, win32con.SW_MINIMIZE)
            self._logger.info(f"Minimized window {handle}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to minimize window {handle}: {e}")
            return False

    def maximize_window(self, handle: int) -> bool:
        """Maximizes the window."""
        try:
            win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)
            self._logger.info(f"Maximized window {handle}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to maximize window {handle}: {e}")
            return False

    def restore_window(self, handle: int) -> bool:
        """Restores the window."""
        try:
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            self._logger.info(f"Restored window {handle}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to restore window {handle}: {e}")
            return False
            
    def move_window(self, handle: int, x: int, y: int, width: int, height: int) -> bool:
        """Moves and resizes the window."""
        try:
            win32gui.MoveWindow(handle, x, y, width, height, True)
            self._logger.info(f"Moved window {handle} to ({x}, {y}, {width}, {height})")
            return True
        except Exception as e:
            self._logger.error(f"Failed to move window {handle}: {e}")
            return False

    def set_foreground(self, handle: int) -> bool:
        """Brings the window to the foreground."""
        try:
            # Sometimes setting foreground requires specific conditions or tricks
            # like attaching thread input if the foreground lock timeout is set.
            # For simplicity, we just try SetForegroundWindow.
            win32gui.SetForegroundWindow(handle)
            self._logger.info(f"Set window {handle} to foreground")
            return True
        except Exception as e:
            self._logger.error(f"Failed to set foreground window {handle}: {e}")
            return False
