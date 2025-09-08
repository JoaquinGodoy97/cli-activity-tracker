import pandas as pd
from rich.console import Console
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .progress_tracker import ProgressTracker
    from .activity import Activity

console = Console()

class ActivityManager:
    def __init__(self, sheets_id: str): 
        from ..services.google_sheets_service import GoogleSheetsService
        self.activities = GoogleSheetsService.load_activities(sheets_id)
    
    def list_activities(self, tracker: 'ProgressTracker') -> None:
        """Display all available activities with their status."""
        if self.activities.empty:
            print("📭 No activities found.")
            return
        
        for i, act in self.activities.iterrows():
            completed = tracker.is_activity_completed(act) if not tracker.progress.empty else False
            status = "✅" if completed else "⏳"
            activity_highlight = f"[#ff6b6b]{act['activity']}[/#ff6b6b]" if not completed else f"[#4CAF50]{act['activity']}[/#4CAF50]"
            console.print(f"{i+1}. {activity_highlight} (Urgent: [bold #3F51B5]{act['urgent']}[/bold #3F51B5]) {status}", highlight=False)

    def get_activity(self, index: int) -> 'Activity':
        """Get activity data by index."""
        from .activity import Activity
        raw_activity = self.activities.iloc[index]
        return Activity(raw_activity)
