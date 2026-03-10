import pytest
from unittest.mock import MagicMock, patch
from window_manager import WindowManager, WindowInfo

@pytest.fixture
def mock_win32gui():
    with patch("window_manager.core.win32gui") as mock:
        yield mock

@pytest.fixture
def mock_win32process():
    with patch("window_manager.core.win32process") as mock:
        yield mock

@pytest.fixture
def mock_psutil():
    with patch("window_manager.core.psutil") as mock:
        yield mock

@pytest.fixture
def manager():
    return WindowManager()

def test_get_all_windows(manager, mock_win32gui, mock_win32process, mock_psutil):
    # Setup mock data
    mock_win32gui.IsWindowVisible.return_value = True
    mock_win32gui.GetWindowText.return_value = "Test Window"
    mock_win32gui.GetClassName.return_value = "TestClass"
    mock_win32gui.GetWindowRect.return_value = (0, 0, 100, 100)
    mock_win32process.GetWindowThreadProcessId.return_value = (0, 1234)
    
    mock_process = MagicMock()
    mock_process.name.return_value = "test.exe"
    mock_psutil.Process.return_value = mock_process
    
    # Simulate EnumWindows calling the callback once
    def side_effect(callback, ctx):
        callback(1, ctx)
    mock_win32gui.EnumWindows.side_effect = side_effect
    
    windows = manager.get_all_windows()
    
    assert len(windows) == 1
    assert windows[0].handle == 1
    assert windows[0].title == "Test Window"
    assert windows[0].class_name == "TestClass"
    assert windows[0].pid == 1234
    assert windows[0].process_name == "test.exe"

def test_find_windows(manager, mock_win32gui, mock_win32process, mock_psutil):
    # Setup mock data
    mock_win32gui.IsWindowVisible.return_value = True
    
    def get_text(hwnd):
        if hwnd == 1: return "Target Window"
        if hwnd == 2: return "Other Window"
        return ""
    mock_win32gui.GetWindowText.side_effect = get_text
    
    mock_win32gui.GetClassName.return_value = "TestClass"
    mock_win32process.GetWindowThreadProcessId.return_value = (0, 1234)
    
    mock_process = MagicMock()
    mock_process.name.return_value = "test.exe"
    mock_psutil.Process.return_value = mock_process
    
    def side_effect(callback, ctx):
        callback(1, ctx)
        callback(2, ctx)
    mock_win32gui.EnumWindows.side_effect = side_effect
    
    # Test find by title
    found = manager.find_windows(title="Target")
    assert len(found) == 1
    assert found[0].title == "Target Window"
    
    # Test find by exact title
    found = manager.find_windows(title="Target", exact_match=True)
    assert len(found) == 0
    
    found = manager.find_windows(title="Target Window", exact_match=True)
    assert len(found) == 1

    # Test find by process_name
    found = manager.find_windows(process_name="test.exe")
    assert len(found) == 2 # Both windows have same PID in this mock
    
    found = manager.find_windows(process_name="other.exe")
    assert len(found) == 0


def test_window_controls(manager, mock_win32gui):
    handle = 12345
    
    # Close
    manager.close_window(handle)
    mock_win32gui.PostMessage.assert_called_with(handle, 16, 0, 0) # WM_CLOSE = 16 (0x10)
    
    # Minimize
    manager.minimize_window(handle)
    mock_win32gui.ShowWindow.assert_called_with(handle, 6) # SW_MINIMIZE = 6
    
    # Maximize
    manager.maximize_window(handle)
    mock_win32gui.ShowWindow.assert_called_with(handle, 3) # SW_MAXIMIZE = 3
    
    # Restore
    manager.restore_window(handle)
    mock_win32gui.ShowWindow.assert_called_with(handle, 9) # SW_RESTORE = 9
    
    # Move
    manager.move_window(handle, 10, 20, 300, 200)
    mock_win32gui.MoveWindow.assert_called_with(handle, 10, 20, 300, 200, True)

