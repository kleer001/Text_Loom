from textual.widgets import Static
from textual.binding import Binding

from core.token_manager import get_token_manager
from TUI.logging_config import get_logger

logger = get_logger('token')


class TokenWindow(Static):
    DEFAULT_CSS = """
    TokenWindow {
        width: 100%;
        height: 3;
        background: $background;
        color: $foreground-muted;
        padding: 0 1;
        border: solid $primary-muted;
        text-align: left;
    }
    """

    BINDINGS = [
        Binding("r", "refresh_tokens", "Refresh Tokens", show=False),
    ]

    def on_mount(self):
        self.refresh_data()
        self.set_interval(5.0, self.refresh_data)

    def format_number(self, num: int) -> str:
        return f"{num:,}"

    def refresh_data(self):
        try:
            token_manager = get_token_manager()
            totals = token_manager.get_totals()

            status_text = (
                f"🪙 Tokens: "
                f"In: {self.format_number(totals['input_tokens'])} | "
                f"Out: {self.format_number(totals['output_tokens'])} | "
                f"Total: {self.format_number(totals['total_tokens'])}"
            )
            self.update(status_text)
        except Exception as e:
            logger.error(f"Error refreshing token data: {str(e)}")
            self.update(f"🪙 Tokens: Error loading data")

    def action_refresh_tokens(self):
        logger.debug("Manual token refresh triggered")
        self.refresh_data()
