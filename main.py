import time
import win32gui
from window_manager import WindowManager, setup_logger

# Setup logging
logger = setup_logger("WeChatMonitor")

def main():
    manager = WindowManager()
    
    target_title = "微信"
    target_process = "Weixin.exe"
    
    logger.info(f"Starting monitor for window: Title='{target_title}', Process='{target_process}'")
    
    current_hwnd = None
    
    try:
        while True:
            # 1. Ensure we have a valid handle
            if not current_hwnd or not win32gui.IsWindow(current_hwnd):
                windows = manager.find_windows(title=target_title, process_name=target_process)
                if windows:
                    # Prefer visible windows if multiple match
                    visible_windows = [w for w in windows if w.is_visible]
                    if visible_windows:
                        current_hwnd = visible_windows[0].handle
                    else:
                        current_hwnd = windows[0].handle
                    logger.info(f"Found target window: {current_hwnd}")
                else:
                    logger.debug("Target window not found, retrying...")
                    time.sleep(2)
                    continue

            # 2. Check state and restore if needed
            # Check if minimized (Iconic), not visible, or not foreground (occluded/lost focus)
            is_iconic = win32gui.IsIconic(current_hwnd)
            is_visible = win32gui.IsWindowVisible(current_hwnd)
            foreground_hwnd = win32gui.GetForegroundWindow()
            is_foreground = (current_hwnd == foreground_hwnd)
            
            if is_iconic or not is_visible or not is_foreground:
                reason = []
                if is_iconic: reason.append("Minimized")
                if not is_visible: reason.append("Hidden")
                if not is_foreground: reason.append("Not Foreground/Occluded")
                
                logger.info(f"Window state issue ({', '.join(reason)}). Restoring/Bringing to front...")
                
                # If not visible at all (e.g. in tray), we might need to show it first
                if not is_visible:
                    # SW_SHOW = 5
                    win32gui.ShowWindow(current_hwnd, 5)
                
                if is_iconic:
                    manager.restore_window(current_hwnd)
                
                # Force to foreground if it's not already
                if not is_foreground:
                    manager.set_foreground(current_hwnd)
            
            # Sleep a bit to avoid high CPU usage
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
