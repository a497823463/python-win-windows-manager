import pytest
from unittest.mock import MagicMock, patch
import time
from window_manager import WindowMonitor

@pytest.fixture
def mock_user32():
    with patch("window_manager.monitor.user32") as mock:
        yield mock

def test_monitor_lifecycle(mock_user32):
    # Mock SetWinEventHook to return a fake hook handle
    mock_user32.SetWinEventHook.return_value = 12345
    mock_user32.UnhookWinEvent.return_value = 1
    
    # Mock PeekMessage/GetMessage behavior to avoid infinite loop or blocking
    # We want PeekMessage to return False initially to simulate no messages
    # Then we want the loop to exit when stop is called.
    # The loop condition is `while not self._stop_event.is_set():`
    # So we just need to ensure PeekMessage doesn't block or return WM_QUIT immediately unless we want to test that.
    
    mock_user32.PeekMessageW.return_value = 0
    
    monitor = WindowMonitor()
    monitor.start()
    
    # Allow thread to start
    time.sleep(0.1)
    
    assert monitor._thread.is_alive()
    assert monitor._hook == 12345
    
    monitor.stop()
    
    # Allow thread to stop
    time.sleep(0.1)
    
    assert not monitor._thread.is_alive()
    mock_user32.UnhookWinEvent.assert_called_with(12345)
