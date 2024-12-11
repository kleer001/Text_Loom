from textual.containers import ScrollableContainer
from textual.widgets import Static
from textual.app import ComposeResult
from TUI.messages import OutputMessage
from TUI.logging_config import get_logger

class OutputWindow(ScrollableContainer):
    DEFAULT_CSS = """
    OutputWindow {
        width: 100%;
        height: 50%;
        background: $background;
        border: solid $primary;
        color: $foreground;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger('output')
        self._output = Static()

    def compose(self) -> ComposeResult:
        yield self._output

    def on_mount(self) -> None:
        self.logger.debug("OutputWindow mounted")
        self._output.update("[italic]NO NODE SELECTED[/italic]")
        self.border_title = "Output"

    def on_output_message(self, message: OutputMessage) -> None:
        self.logger.debug("OutputWindow received output message")
        try:
            if not message.output_data:
                self.logger.debug("Received empty output data")
                self._output.update("[italic]NO OUTPUT DATA[/italic]")
                return

            if any(line is None for line in message.output_data):
                self.logger.debug("Received None in output data")
                self._output.update("[italic]NO OUTPUT DATA[/italic]")
                return

            formatted_output = "\n".join(str(line) for line in message.output_data if line is not None)
            if not formatted_output.strip():
                self.logger.debug("Output data was empty after formatting")
                self._output.update("[italic]EMPTY OUTPUT[/italic]")
                return

            self.logger.debug(f"Updating display with output: {formatted_output}")
            self._output.update(formatted_output)
            self.scroll_end(animate=False)

        except Exception as e:
            error_msg = f"Error displaying output: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self._output.update(f"[red]ERROR: {error_msg}[/red]")
            self.scroll_end(animate=False)
