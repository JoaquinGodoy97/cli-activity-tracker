from rich.console import Console
from typing import Optional
from ..core.activity_manager import ActivityManager
from ..core.progress_tracker import ProgressTracker
from ..core.activity import Activity
from ..utils.time_utils import TimeUtility
from ..utils.question_utils import QuestionUtility
from ..utils.spinner import Spinner
from datetime import datetime, timedelta

console = Console()

class MenuHandler:
    """Handles menu interactions and user input processing."""
    
    def __init__(self, sheets_id: str):
        self.manager: Optional[ActivityManager] = None
        self.tracker = ProgressTracker()
        self.sheets_id = sheets_id

    def run(self) -> None:
        """Main menu loop."""

        self.manager = ActivityManager(self.sheets_id)

        while True:
            hours_left, mins_left = TimeUtility.hours_remaining_in_day()

            self._display_main_menu(hours_left, mins_left)
            choice = self._get_user_choice()
            
            if choice == -1:  # Exit
                print("👋 Exiting. See you next time.")
                break
            elif choice == len(self.manager.activities):  # Update progress
                self._handle_update_progress()
            elif choice == len(self.manager.activities) + 1:  # Show progress
                self._handle_show_progress()
            elif choice == len(self.manager.activities) + 2:  # Extend day
                self._handle_extend_day()
            elif choice == len(self.manager.activities) + 3:
                self._handle_refresh()
            elif choice == len(self.manager.activities) + 4 and TimeUtility.time_warped_detection():  # Delete progress
                self._handle_time_warp()
            elif 0 <= choice < len(self.manager.activities):  # Activity selection
                self._handle_activity_selection(choice)
            else:
                print("❌ Invalid choice. Try again.")
                Spinner().start()

    def _display_main_menu(self, hours_left: int, mins_left: int) -> None:
        """Display the main menu with activities and options."""
        print("\nAvailable activities:")
        self.manager.list_activities(self.tracker)
        console.print(f"\n{len(self.manager.activities) + 1}. Update progress", highlight=False)
        console.print(f"{len(self.manager.activities) + 2}. Show progress", highlight=False)
        console.print(f"{len(self.manager.activities) + 3}. Extend workday", highlight=False)
        console.print(f"{len(self.manager.activities) + 4}. Refresh\n", highlight=False)
        if TimeUtility.time_warped_detection():
            console.print(f"{len(self.manager.activities) + 5}. Back to the present!", highlight=False)
        
        console.print(f"\n⏳ You have approximately [bold #ff6b6b]{hours_left}[/bold #ff6b6b] hours and [bold #ff6b6b]{mins_left}[/bold #ff6b6b] mins. left today to work on your tasks.\n", highlight=False)

    def _get_user_choice(self) -> int:
        """Get user choice from input."""
        try:
            choice = int(input("\nChoose an activity number (or 0 to exit): ")) - 1
            return choice
        except (ValueError, IndexError):
            return -999  # Invalid choice

    def _handle_update_progress(self) -> None:
        """Handle progress update menu."""
        self.tracker.delete_progress()
        Spinner().start()

    def _handle_show_progress(self) -> None:
        """Handle show progress menu."""
        self.tracker.show_progress()
        Spinner().start()

    def _handle_extend_day(self) -> None:
        """Handle extending the workday."""
        """Extend the workday will give you a few more hours to work on your tasks."""

        hours_to_extend = int(input("How many hours do you want to extend your workday? (Enter a number): "))
        if hours_to_extend <= 0:
            print("❌ Invalid number of hours. Must be greater than 0.")
            Spinner().start()
            return

        try:
            extended_now = datetime.now() - timedelta(hours=hours_to_extend)
            TimeUtility.set_virtual_now(extended_now)
            print(f"✅ Day extended by {hours_to_extend}h. Virtual time is now {extended_now.strftime('%H:%M')}")
            self.tracker.refresh()
            Spinner().start()
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            Spinner().start()

    def _handle_time_warp(self) -> None:
        """Handle time warp."""
        TimeUtility.reset_virtual_now()
        print("✅ Time warp detected. Back to the present.")
        self.tracker.refresh()
        Spinner().start()

    def _handle_refresh(self) -> None:
        """Handle refresh progress."""
        self.tracker.refresh()
        Spinner().start()

    def _handle_activity_selection(self, choice: int) -> None:
        """Handle activity selection and processing."""
        try:
            activity = self.manager.get_activity(choice)
            self._process_activity(activity)
        except Exception as e:
            print(f"❌ Error processing activity: {e}")
        finally:
            Spinner().start()

    def _process_activity(self, activity: 'Activity') -> None:
        """Process the selected activity based on its type."""
        if activity.is_urgent:
            self._handle_urgent_activity(activity)
        else:
            self._handle_optional_activity(activity)

    def _handle_urgent_activity(self, activity: 'Activity') -> None:
        """Handle urgent activity processing."""
        print(f"⚡ Urgent task: {activity.name}")

        if activity.is_repeated(self.tracker):
            print("You've done this activity already today.")
        else:
            hours_worked = int(input("How many hours did you work? (Enter a number): "))
            activity.time = hours_worked * 60

            if QuestionUtility.ask_yes_no("Did you finish it?"):
                self.tracker.add_activity(activity)
            else:
                print("❌ Task not finished.")

    def _handle_optional_activity(self, activity: 'Activity') -> None:
        """Handle optional activity processing."""
        print(f"\nOptional task: {activity.name}")

        # Weekly progress
        self.tracker.check_weekly_progress(activity)

        if activity.is_repeated(self.tracker):
            print("You've done this activity already.")
        elif QuestionUtility.ask_yes_no(activity.trigger_question):
            self.tracker.add_activity(activity)
            self.tracker.refresh()
        else:
            print("⏭️ Skipped.")
