import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.progress_tracker import ProgressTracker 

class Activity:
    def __init__(self, data):
        self.name = data["activity"]
        self.time = int(data["activity_time"])
        self.reward = data["reward"]
        self.is_urgent = data["urgent"].lower() == "yes"
        self.quota = data["quota_per_week"]
        self.trigger_question = data["trigger_question"]
    
    def is_repeated(self, tracker: 'ProgressTracker') -> bool: 

        if tracker.progress.empty:
            return False
        
        try:
            todayActivities = tracker.progress[
                tracker.progress["date"].dt.day == datetime.datetime.now().day
            ]
        
            isActivityRepeated = self.name in todayActivities["tasks_finished"].to_list()
            return isActivityRepeated

        except Exception as e:
            print(e, "could not bring activities")
        
    def should_trigger(): 
        pass