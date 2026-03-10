import sys
import time
import subprocess
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from window_manager import WindowManager, WindowMonitor, setup_logger

# Setup logging
logger = setup_logger("Demo", level=10) # DEBUG

def monitor_callback(event, hwnd, title):
    print(f"[MONITOR] Event: {event}, HWND: {hwnd}, Title: '{title}'")

def main():
    manager = WindowManager()
    monitor = WindowMonitor(callback=monitor_callback)
    
    print("Starting Window Monitor...")
    monitor.start()
    
    # List all windows
    print("\nListing all visible windows:")
    windows = manager.get_all_windows(visible_only=True)
    for w in windows[:5]: # Show first 5
        print(f"  {w}")
    print(f"Total visible windows: {len(windows)}")
    
    # Create a test window (Notepad)
    print("\nLaunching Notepad for testing...")
    notepad_process = subprocess.Popen("notepad.exe")
    time.sleep(2) # Wait for window to appear
    
    # Find Notepad window
    print("\nFinding Notepad window...")
    notepad_windows = manager.find_windows(title="Notepad", exact_match=False)
    
    if not notepad_windows:
        print("Could not find Notepad window!")
        monitor.stop()
        notepad_process.terminate()
        return

    target_window = notepad_windows[0]
    print(f"Found: {target_window}")
    
    hwnd = target_window.handle
    
    # Test manipulations
    print("\nTesting manipulations:")
    
    print("  Minimizing...")
    manager.minimize_window(hwnd)
    time.sleep(1)
    
    print("  Restoring...")
    manager.restore_window(hwnd)
    time.sleep(1)
    
    print("  Maximizing...")
    manager.maximize_window(hwnd)
    time.sleep(1)
    
    print("  Restoring...")
    manager.restore_window(hwnd)
    time.sleep(1)
    
    print("  Moving to (100, 100) with size 800x600...")
    manager.move_window(hwnd, 100, 100, 800, 600)
    time.sleep(1)
    
    # Verify monitoring caught these events
    print("\nWaiting for events to be logged...")
    time.sleep(2)
    
    # Close Notepad
    print("\nClosing Notepad...")
    manager.close_window(hwnd)
    time.sleep(1)
    
    # Stop monitor
    print("\nStopping Monitor...")
    monitor.stop()
    
    # Ensure process is gone
    if notepad_process.poll() is None:
        notepad_process.terminate()
        
    print("\nDemo completed.")

if __name__ == "__main__":
    main()
