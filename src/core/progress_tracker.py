import os
import pandas as pd
from datetime import datetime, timedelta
from src.config.settings import PROGRESS_FILE
from typing import TYPE_CHECKING, Dict, Any
import calendar
from rich.console import Console
from src.utils.time_utils import TimeUtility

if TYPE_CHECKING:
    from src.core.activity import Activity
    

console = Console()

class ProgressTracker:
    def __init__(self): 
        self.progress = self.load_progress()

    def load_progress(self):

        columns = ["date", "tasks_finished", "time_dedicated", "rewards"]
    
        if not os.path.exists(PROGRESS_FILE):
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_csv(PROGRESS_FILE, index=False)
            console.print("📁 Created new progress.csv file.")
            return empty_df

        # Load and robustly coerce dates to datetimelike values
        df = pd.read_csv(PROGRESS_FILE)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def is_activity_completed(self, activity: object):

        today_anchor = TimeUtility.get_now().date().day

        todayActivities = self.progress[
                self.progress["date"].dt.day == today_anchor
            ]

        return activity["activity"] in todayActivities.values

    def update_progress(self, filtered_progress: pd.DataFrame):
        filtered_progress.to_csv(PROGRESS_FILE, index=False)

    def refresh(self):
        self.progress = self.load_progress()

    def delete_progress(self): 

        period_handlers = {
            "month": self.handle_month_deletion,
            "day": self.handle_day_deletion,
            "entry": self.handle_single_entry_deletion
        }

        while True:

            if self.progress.empty:
                print("📭 No progress found so far.")
                break

            period = input("Delete progress by 'month', 'day' or 'entry'? Type a period or 'back' to exit: ").strip().lower()

            if period == "back":
                print("🔙 Returning to previous menu.")
                break
                
            handler = period_handlers.get(period)
            if handler:
                handler()
            else:
                print(f"❌ '{period}' is not supported.")

    def handle_month_deletion(self):
        target = input("Which month? (e.g., september): ").strip().lower()
        try:
            month_number = list(calendar.month_name).index(target.capitalize())
            entries = self.filter_by_month(month_number)
            self.confirm_and_delete(entries, target)
        except ValueError:
            print(f"❌ '{target}' is not a valid month.")

    # Delete by day is not privding 
    def handle_day_deletion(self):
        target = input("Which day? (e.g., 2025-09-05): ").strip()
        try:
            target_date = pd.to_datetime(target).date()
            entries = self.filter_by_day(target_date)
            self.confirm_and_delete(entries, target)
        except Exception:
            print(f"❌ '{target}' is not a valid date.")

    def handle_single_entry_deletion(self):
        target_day = input("Which day? (e.g., 2025-09-05): ").strip()
        
        try:
            target_date = pd.to_datetime(target_day).date()
            entries = self.filter_by_day(target_date)
            for idx, row in entries.iterrows():
                print(f"{idx}. {row['tasks_finished']} ({row['date'].date()})")
            
            try:
                target_index = int(input(f"Which entry do you want to delete from day {target_day}? (e.g., 5): "))
                entry = self.filter_by_single_entry(target_date, target_index)

            except Exception:
                print(f"❌ '{target_index}' is not a valid task.")
            
            entry_df = pd.DataFrame([entry])
            entry_df.index = [entry.name]
            self.confirm_and_delete(entry_df, target_date)

        except Exception:
            print(f"❌ '{target_index}' is not a valid date.")
    
    def confirm_and_delete(self, entries, label):
        if entries.empty:
            print(f"📭 No progress found for {label}.")
            return

        print(f"\n🗑️ Entries to delete for {label}:")
        for idx, row in entries.iterrows():
            date_val = row['date']
            if pd.notna(date_val):
                try:
                    date_text = date_val.date() if hasattr(date_val, 'date') else str(date_val)
                except Exception:
                    date_text = str(date_val)
            else:
                date_text = "Unknown date"
            print(f"{idx}. {row['tasks_finished']} ({date_text})")

        confirm = input("\nAre you sure you want to delete these entries? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.update_progress(self.progress[~self.progress.index.isin(entries.index)])
            print(f"✅ Deleted progress for {label}.")
            self.refresh()
        else:
            print("❌ Deletion cancelled.")

    def filter_by_month(self, month_number):        
        return self.progress[self.progress["date"].dt.month == month_number]
    
    def filter_by_day(self, target_date): 
        return self.progress[self.progress["date"].dt.date == target_date]
    
    def filter_by_single_entry(self, target_date, index):
        return self.progress[self.progress["date"].dt.date == target_date].loc[index]

    def show_progress(self):
        total_time_not_urgent = 0
        work_time = 0
        for i, row in self.progress.iterrows():
            date_val = row["date"]
            if pd.notna(date_val):
                try:
                    date_str = date_val.strftime("%Y-%m-%d")
                except Exception:
                    # Fallback for non-datetime-like values
                    date_str = str(date_val)
            else:
                date_str = "Unknown date"

            if row["tasks_finished"] == "work":
                work_time += row['time_dedicated']
            else: 
                total_time_not_urgent += row['time_dedicated']

            reward = f"| Reward: {row['rewards']}"
            console.print(f"{date_str} | Task: {row['tasks_finished']} | Time: {row['time_dedicated']} mins {reward if pd.notna(row['rewards']) else ""}")

        hours_nu = total_time_not_urgent // 60
        mins_nu = total_time_not_urgent % 60

        working_hours = work_time // 60
        minutes = work_time % 60

        minutes_nu_text = f"and {mins_nu} min." if mins_nu != 0 else ""
        minutes_work_text = f" and {minutes} min" if minutes != 0 else ""

        # NU first then Working hours.
        console.print(f"\nTotal time dedicated: {hours_nu} of hours {minutes_nu_text} dedicated and {working_hours} working hours{minutes_work_text}.\n")
        
        while True:
            go_back = input("Enter 'back' if you want to go back to main menu: ").strip().lower()
            if go_back == "back":
                return

    # Checks quota over the months divided by weekly quota
    def check_weekly_progress(self, activity: 'Activity') -> None: # utility

        month_name = TimeUtility.get_now().strftime('%B')

        weekly_counts = self.filter_weeks_by_activity(activity)
        week_by_month_number = len(weekly_counts.index.tolist()) if not weekly_counts.empty else 0

        tu = TimeUtility(TimeUtility.get_now())
        tu.get_weeks_of_month()
        all_weeks_by_month = tu.get_weeks_of_month_iso()

        first_activity_date = weekly_counts.index.min() if not weekly_counts.empty else None

        if not week_by_month_number:
            print(f"Happy to guide you on your first week of {month_name}!")

        if weekly_counts.empty:
            return

        current_week = weekly_counts.index.tolist()[len(weekly_counts.index.tolist()) - 1]

        for i, week_num in enumerate(all_weeks_by_month, start=1):
            count = weekly_counts.get(week_num, 0)

            first_activity_msg = f" 👈 Where you started!" if first_activity_date == week_num else ""

            if week_num <= current_week:
                if count == 0:
                    status = "➖ Only 0/" + str(int(activity.quota))
                else:
                    status = "✅ Met" if count >= int(activity.quota) else f"❌ Only {count}/{int(activity.quota)}" + str(first_activity_msg)
                print(f"Week {i} of {month_name}: {status}")
    
    def add_empty_week_progress(self, week_index, month_name, activity):
        for i in range(0, week_index):
            print(f"Week {i} of {month_name}: ❌ Only 0/{int(activity.quota)}")

    # Returns a weekly dateframe filter by activity
    def filter_weeks_by_activity(self, activity: 'Activity') -> pd.Series:  
        target_month = TimeUtility.get_now().month

        if self.progress.empty:
            return pd.Series(dtype=int)

        monthly_data = self.progress[
            self.progress["date"].dt.month == target_month
        ].copy()

        monthly_data["year_week"] = monthly_data["date"].dt.isocalendar().week

        weekly_counts = (
            monthly_data[monthly_data["tasks_finished"] == activity.name]
            .groupby("year_week")
            .size()
        )

        return weekly_counts

    def add_activity(self, activity: 'Activity') -> None:
        """Add activity to progress tracking."""
        today = TimeUtility.get_now().date().isoformat()
        progress_entry = {
                "date": today,
                "tasks_finished": activity.name,
                "time_dedicated": activity.time,
                "rewards": activity.reward
                }
        
        from ..services.data_service import DataService
        DataService.save_progress(progress_entry)
        self.refresh()
        
        print(f"✅ Progress updated: {activity.name} ({activity.time} mins)")
    
    def save_progress(self, progress_entry: Dict[str, Any]) -> None:
        """Save progress entry using DataService."""
        from ..services.data_service import DataService
        DataService.save_progress(progress_entry)
    