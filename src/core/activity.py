from datetime import datetime
from typing import TYPE_CHECKING
from src.utils.time_utils import TimeUtility

if TYPE_CHECKING:
    from src.core.progress_tracker import ProgressTracker 

class Activity:
    def __init__(self, data):
        self.name = data["activity"]
        self.time = int(data["activityTime"])
        self.reward = data["reward"]
        self.is_urgent = data["urgent"].lower() == "yes"
        self.quota = data["quotaPerWeek"]
        self.trigger_question = data["triggerQuestion"]
    
    def is_repeated(self, tracker: 'ProgressTracker') -> bool: 

        today_anchor = TimeUtility.get_now().date().day

        if tracker.progress.empty:
            return False
        
        try:
            # Ensure date column is datetimelike before using .dt
            if not hasattr(tracker.progress["date"], "dt"):
                tracker.progress["date"] = TimeUtility.pd_to_datetime(tracker.progress["date"])  # type: ignore

            todayActivities = tracker.progress[
                tracker.progress["date"].dt.day == today_anchor
            ]
        
            isActivityRepeated = self.name in todayActivities["tasks_finished"].to_list()
            return isActivityRepeated

        except Exception as e:
            print(e, "could not bring activities")
        
    # def should_trigger(): 
    #     pass