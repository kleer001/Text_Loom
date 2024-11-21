from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.binding import Binding
from rich.text import Text
from .logging_config import get_logger
import sys
from io import StringIO
from threading import Lock

import TUI.palette as pal

logger = get_logger('status')



class CapturedOutput:
    def __init__(self):
        self.buffer = StringIO()
        self._lock = Lock()
        
    def write(self, text):
        with self._lock:
            self.buffer.write(text)
            
    def flush(self):
        pass
        
    def getvalue(self):
        with self._lock:
            return self.buffer.getvalue()

class StatusWindow(ScrollableContainer):
    BINDINGS = [
        Binding("ctrl+l", "clear", "Clear Output")
    ]
    
    DEFAULT_CSS = f"""
    StatusWindow {{
        width: 100%;
        height: 30%;
        background: {pal.STATUS_WIN_BACKGROUND};
        border: {pal.STATUS_WIN_BORDER} {pal.STATUS_WIN_BORDER_COLOR};
        color: {pal.STATUS_WIN_TEXT};
        padding: 0 1;
        overflow-y: scroll;
    }}
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger('status')
        self._output = Static()
        self._captured_stdout = CapturedOutput()
        self._captured_stderr = CapturedOutput()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._last_content_length = 0
        
    def compose(self) -> ComposeResult:
        yield self._output

    def on_mount(self):
        self.logger.debug("StatusWindow mounted")
        self.border_title = "Status"
        sys.stdout = self._captured_stdout
        sys.stderr = self._captured_stderr
        self.set_interval(0.1, self._update_output)

    def on_unmount(self):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        
    def _update_output(self):
        stdout_content = self._captured_stdout.getvalue()
        stderr_content = self._captured_stderr.getvalue()
        
        total_length = len(stdout_content) + len(stderr_content)
        
        if stdout_content or stderr_content:
            text = Text()
            if stdout_content:
                text.append(stdout_content)
            if stderr_content:
                text.append(stderr_content, style="red")
            self._output.update(text)
            
            if total_length != self._last_content_length:
                self._last_content_length = total_length
                self.scroll_end(animate=False)
            
    def action_clear(self):
        self._captured_stdout.buffer = StringIO()
        self._captured_stderr.buffer = StringIO()
        self._output.update("")
        self._last_content_length = 0
        self.logger.debug("Cleared status window")