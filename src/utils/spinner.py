from rich.console import Console
import time

class Spinner:
    def __init__(self):
        self.console = Console()
        self.spinner = "bouncingBall"
        self.spinner_style = "white"

    def start(self) -> None:
        """Start the spinner animation."""
        with self.console.status(f"\n[{self.spinner_style}]", spinner=self.spinner, spinner_style=self.spinner_style):
            time.sleep(2)
