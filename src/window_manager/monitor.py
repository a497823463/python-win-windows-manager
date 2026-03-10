import ctypes
from ctypes import wintypes
import threading
import time
import win32con
import win32api
import win32gui
from typing import Callable, Optional
from .utils import setup_logger

logger = setup_logger("WindowMonitor")

# Constants for SetWinEventHook
EVENT_MIN = 0x00000001
EVENT_MAX = 0x7FFFFFFF
EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_OBJECT_CREATE = 0x8000
EVENT_OBJECT_DESTROY = 0x8001
EVENT_OBJECT_SHOW = 0x8002
EVENT_OBJECT_HIDE = 0x8003
EVENT_OBJECT_NAMECHANGE = 0x800C
WINEVENT_OUTOFCONTEXT = 0x0000

# Callback function type
WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD
)

user32 = ctypes.windll.user32

class WindowMonitor:
    """
    Monitors window events such as creation, destruction, and state changes.
    """
    
    def __init__(self, callback: Optional[Callable[[str, int, int], None]] = None):
        """
        Initializes the WindowMonitor.
        
        Args:
            callback: A function to call when an event occurs. 
                      Signature: callback(event_name, hwnd, id_object)
        """
        self._callback = callback
        self._hook = None
        self._thread = None
        self._stop_event = threading.Event()
        self._logger = logger

    def _event_handler(self, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        """
        Internal callback for SetWinEventHook.
        """
        if idObject != 0: # OBJID_WINDOW = 0
            return

        event_name = "Unknown"
        if event == EVENT_OBJECT_CREATE:
            event_name = "Create"
        elif event == EVENT_OBJECT_DESTROY:
            event_name = "Destroy"
        elif event == EVENT_OBJECT_SHOW:
            event_name = "Show"
        elif event == EVENT_OBJECT_HIDE:
            event_name = "Hide"
        elif event == EVENT_SYSTEM_FOREGROUND:
            event_name = "Foreground"
        elif event == EVENT_OBJECT_NAMECHANGE:
            event_name = "NameChange"
        
        # Only log/callback for interesting events on actual windows
        # Filter out some noise if necessary, but for now report all OBJID_WINDOW
        
        # We can try to get window title here, but be careful as the window might be destroying
        title = ""
        try:
            if event != EVENT_OBJECT_DESTROY:
                 # win32gui.GetWindowText might fail if window is gone
                 length = user32.GetWindowTextLengthW(hwnd)
                 buff = ctypes.create_unicode_buffer(length + 1)
                 user32.GetWindowTextW(hwnd, buff, length + 1)
                 title = buff.value
        except Exception:
            pass

        log_msg = f"Event: {event_name}, HWND: {hwnd}, Title: {title}"
        self._logger.info(log_msg)
        
        if self._callback:
            try:
                self._callback(event_name, hwnd, title)
            except Exception as e:
                self._logger.error(f"Error in user callback: {e}")

    def _run(self):
        """
        The thread function that runs the message loop.
        """
        self._logger.info("Starting monitor thread...")
        
        # Keep reference to the callback to prevent garbage collection
        self._c_callback = WinEventProcType(self._event_handler)
        
        # Set hook
        self._hook = user32.SetWinEventHook(
            EVENT_MIN,
            EVENT_MAX,
            0,
            self._c_callback,
            0,
            0,
            WINEVENT_OUTOFCONTEXT
        )
        
        if not self._hook:
            self._logger.error("Failed to set win event hook")
            return
            
        # Message loop
        msg = wintypes.MSG()
        while not self._stop_event.is_set():
            # PeekMessage is non-blocking, so we can check stop_event
            # But SetWinEventHook needs a message pump.
            # GetMessage blocks.
            # We can use MsgWaitForMultipleObjects or just PeekMessage with a sleep.
            
            if user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1): # PM_REMOVE = 1
                if msg.message == win32con.WM_QUIT:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            else:
                time.sleep(0.01) # Small sleep to avoid CPU spin
        
        # Unhook
        user32.UnhookWinEvent(self._hook)
        self._logger.info("Monitor thread stopped.")

    def start(self):
        """Starts the monitoring thread."""
        if self._thread and self._thread.is_alive():
            self._logger.warning("Monitor already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the monitoring thread."""
        if not self._thread or not self._thread.is_alive():
            return
            
        self._stop_event.set()
        self._thread.join(timeout=2)
        if self._thread.is_alive():
            self._logger.warning("Monitor thread did not stop gracefully")
