from textual.app import App
from textual.widgets import Static, Input
from textual.containers import Horizontal
from textual.reactive import reactive
from logging_config import get_logger

logger = get_logger('demo')

logger.info("Starting demo application")

class ParameterRow(Horizontal):
    DEFAULT_CSS = """
    ParameterRow {
        height: 2;
        margin: 0;
        padding: 0;
        width: 100%;
    }
    
    ParameterRow > Static {
        width: 20;
        background: red;
        color: yellow;
        padding: 0 1;
    }
    
    ParameterRow > Input {
        width: 1fr;
        background: #2C2C2C;
        color: #FFFFFF;
        border: none;
        padding: 0 1;
    }
    
    ParameterRow > Input:focus {
        background: #3C3C3C;
        color: #FFFFFF;
        border: tall #5294E2;
    }
    
    ParameterRow > Input > .input--cursor {
        background: #FFFFFF;
        color: #000000;
        text-style: reverse;
    }
    
    ParameterRow > Input > .input--placeholder {
        color: #888888;
    }
    """

    name = reactive("")
    value = reactive("")
    
    def __init__(self, name: str, value: str):
        super().__init__()
        self.name = name
        self.value = value
        logger.info(f"Init ParameterRow: name={name}, value={value}")

    def compose(self):
        logger.info(f"Composing ParameterRow for {self.name}")
        yield Static(f"{self.name}:", classes="label")
        input_widget = Input(
            value="",
            placeholder=str(self.value),
            id=f"input_{self.name}",
        )
        # Set Input attributes
        input_widget.cursor_blink = True
        input_widget.can_focus = True
        input_widget.expand = True
        logger.info("Input widget created with cursor_blink=True")
        yield input_widget

    def on_mount(self) -> None:
        logger.info(f"Mounting ParameterRow {self.name}")
        input_widget = self.query_one(Input)
        logger.info(f"Initial input state - value: {input_widget.value}, placeholder: {input_widget.placeholder}")

    def on_input_changed(self, event: Input.Changed) -> None:
        logger.info(f"Input changing for {self.name}: new value={event.value}")
        input_widget = self.query_one(Input)
        logger.info(f"Input widget state during change - value: {input_widget.value}, placeholder: {input_widget.placeholder}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        logger.info(f"Input submitted for {self.name}: submitted={event.value}")
        self.value = event.value
        input_widget = self.query_one(Input)
        input_widget.placeholder = event.value
        input_widget.value = ""
        logger.info(f"After submission - value: {input_widget.value}, placeholder: {input_widget.placeholder}")

    def watch_value(self, value: str) -> None:
        logger.info(f"Value changed for {self.name}: {value}")


class DemoApp(App):
    DEFAULT_CSS = """
    Screen {
        background: black;
    }
    """

    def compose(self):
        logger.info("Composing DemoApp")
        yield ParameterRow("test", "initial value")
        yield ParameterRow("test2", "another value")

    def on_mount(self) -> None:
        logger.info("DemoApp mounted")


def main():
    logger.info("Starting main")
    app = DemoApp()
    app.run()


if __name__ == "__main__":
    main()