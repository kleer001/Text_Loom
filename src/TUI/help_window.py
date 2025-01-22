from typing import Dict, List
from pathlib import Path
from textual import work
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import DataTable
from textual.widgets import Static
from textual.containers import Container

from rich.text import Text

from TUI.logging_config import get_logger

logger = get_logger('help', level=0)

class HelpWindow(Container):
    DEFAULT_CSS = """
    HelpWindow {
        width: 100%;
        height: 12.5%;
        
    }
    
    DataTable {
        height: 100%;
        border: none;
}
    """

    help_sections: Dict[str, str] = {}
    current_section = reactive("")

    def compose(self) -> ComposeResult:
        yield Static()
        yield DataTable()

    def on_mount(self) -> None:
        self._load_help_text()
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "none"
        self.table.zebra_stripes = True
        self.table.show_header = True
        self.call_after_refresh(self.update_table)

    def update_table(self) -> None:
        if self.table.size.height > 0:
            self.watch_current_section()
        else:
            self.call_after_refresh(self.update_table)

    def _load_help_text(self) -> None:
        try:
            help_path = Path("TUI/help_tui.md")
            if not help_path.exists():
                error_msg = f"Help file not found at {help_path.absolute()}"
                logger.error(error_msg)
                self.current_section = "ERROR"
                self.help_sections["ERROR"] = error_msg
                return

            current_section = ""
            current_content = []
            
            with help_path.open() as f:
                logger.info(f"Loading help text from {help_path.absolute()}")
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        if current_section:
                            logger.debug(f"Adding section {current_section} with {len(current_content)} lines")
                            self.help_sections[current_section] = "\n".join(current_content)
                        current_section = line[1:-1].upper()
                        current_content = []
                        logger.debug(f"Found new section {current_section} at line {line_num}")
                    elif current_section:
                        current_content.append(line)

            if current_section and current_content:
                logger.debug(f"Adding final section {current_section} with {len(current_content)} lines")
                self.help_sections[current_section] = "\n".join(current_content)

            logger.info(f"Loaded {len(self.help_sections)} help sections: {list(self.help_sections.keys())}")

        except Exception as e:
            error_msg = f"Error loading help: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.current_section = "ERROR"
            self.help_sections["ERROR"] = error_msg

    def _create_table_data(self, content: str) -> List[List[Text]]:
        try:
            lines = [line for line in content.split('\n') if line.strip()]
            if not lines:
                return [[Text("")]]
                
            visible_rows = max(3, self.table.size.height + 1)
            total_lines = len(lines)
            min_columns = max(1, (total_lines + visible_rows - 1) // visible_rows)
            table_data = [[] for _ in range(visible_rows)]
            
            for col_idx in range(min_columns):
                start_idx = col_idx * visible_rows
                column = lines[start_idx:start_idx + visible_rows]
                
                for row_idx, line in enumerate(column):
                    colon_idx = line.find(':')
                    if colon_idx != -1:
                        styled_text = Text()
                        styled_text.append(line[:colon_idx])
                        styled_text.append(line[colon_idx:])
                    else:
                        styled_text = Text(line)
                    table_data[row_idx].append(styled_text)
                    
                for row in table_data[len(column):]:
                    row.append(Text(""))
                    
            return table_data
            
        except Exception as e:
            logger.error(f"Error creating table data: {str(e)}", exc_info=True)
            return [[Text("Error formatting help text")]]
                    

    def watch_current_section(self) -> None:
        section = self.current_section.upper()
        content = self.help_sections.get(section, f"No help available for {section}")
        table_data = self._create_table_data(content)
        self.table.clear(columns=True)
        column_count = len(table_data[0]) if table_data else 1
        headers = [Text(f"{section} Mode commands ", style="bold ")] + ["" for _ in range(column_count - 1)]
        self.table.add_columns(*headers)
        self.table.add_rows(table_data)