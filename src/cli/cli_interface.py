from rich.console import Console
from typing import Optional
from .menu_handler import MenuHandler

console = Console()

class CLI:
    """Main CLI interface for the task tracker application."""
    
    def __init__(self):
        self.menu_handler: Optional[MenuHandler] = None

    def run(self) -> None:
        """Main entry point for the CLI application."""
        try:
            sheets_id = input("Share your GoogleSheets Activities file id: ")
            self.menu_handler = MenuHandler(sheets_id)
            self.menu_handler.run()
        except KeyboardInterrupt:
            print("\n👋 Exiting. See you next time.")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("👋 Exiting. See you next time.")
