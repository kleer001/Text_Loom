from textual.widgets import Static
from textual.message import Message
from .messages import OutputMessage
from .logging_config import get_logger

class OutputWindow(Static):
    DEFAULT_CSS = """
    OutputWindow {
        width: 100%;
        height: 37.5%;
        background: azure;
        border: solid $background;
        color: black;
        padding: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger('output')
    
    def on_mount(self) -> None:
        self.logger.debug("OutputWindow mounted")
        self.update("[italic]NO NODE SELECTED[/italic]")
        self.border_title = "Output"        

    
    def on_output_message(self, message: OutputMessage) -> None:
        self.logger.debug("OutputWindow received output message")
        try:
            if not message.output_data:
                self.logger.debug("Received empty output data")
                self.update("[italic]NO OUTPUT DATA[/italic]")
                return
                
            if any(line is None for line in message.output_data):
                self.logger.debug("Received None in output data")
                self.update("[italic]NO OUTPUT DATA[/italic]")
                return
                
            formatted_output = "\n".join(str(line) for line in message.output_data if line is not None)
            if not formatted_output.strip():
                self.logger.debug("Output data was empty after formatting")
                self.update("[italic]EMPTY OUTPUT[/italic]")
                return
                
            self.logger.debug(f"Updating display with output: {formatted_output}")
            self.update(formatted_output)
            
        except Exception as e:
            error_msg = f"Error displaying output: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.update(f"[red]ERROR: {error_msg}[/red]")
