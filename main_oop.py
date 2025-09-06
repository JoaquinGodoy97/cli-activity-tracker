from __future__ import annotations
import pandas as pd
from typing import List
import os
import datetime
import calendar
import time

class Style:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

PROGRESS_FILE="progress.csv"

class QuestionUtility:
    @staticmethod
    def ask_yes_no(question):
        answer = input(f"{question} (y/n): ").lower().strip()
        return answer in ["y", "yes"]

class ActivityManager:
    def __init__(self, sheets_id: str): 
        ACTIVITIES_FILE = f"https://docs.google.com/spreadsheets/d/{sheets_id}/export?format=csv"
        self.activities = pd.read_csv(ACTIVITIES_FILE)

        if self.activities.empty:
            return []
    
    def list_activities(self, tracker: ProgressTracker): 

        if self.activities.empty:
            print("📭 No activities found.")
            return
        
        # print("📭 No progress found so far.")

        for i, act in self.activities.iterrows():

            completed = tracker.is_activity_completed(act) if not tracker.progress.empty else False
            status = "✅" if completed else "⏳"
            print(f"{Style.RED if not completed else ""} {i+1}. {act["activity"]} (Urgent: {act["urgent"]}) {Style.END} {status}")

    def get_activity(self, index: int) -> Activity:
        return self.activities.iloc[index]

class ProgressTracker:
    def __init__(self): 
        self.progress = self.load_progress()

    def load_progress(self):

        columns = ["date", "tasks_finished", "time_dedicated", "rewards"]
    
        if not os.path.exists(PROGRESS_FILE):
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_csv(PROGRESS_FILE, index=False)
            print("📁 Created new progress.csv file.")
            return empty_df

        return pd.read_csv(PROGRESS_FILE, parse_dates=["date"])

    def is_activity_completed(self, activity: object):

        todayActivities = self.progress[
                self.progress["date"].dt.day == datetime.datetime.now().day
            ]

        return activity["activity"] in todayActivities.values

    def update_progress(self, filtered_progress: ProgressTracker):
        filtered_progress.to_csv("progress.csv", index=False)

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
            print(f"{idx}. {row['tasks_finished']} ({row['date'].date()})")

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
            date_str = row["date"].strftime("%Y-%m-%d")

            if row["tasks_finished"] == "work":
                work_time += row['time_dedicated']
            else: 
                total_time_not_urgent += row['time_dedicated']

            reward = f"| Reward: {row['rewards']}"
            print(f"{date_str} | Task: {row['tasks_finished']} | Time: {row['time_dedicated']} mins {reward if pd.notna(row['rewards']) else ""}")

        hours_nu = total_time_not_urgent // 60
        mins_nu = total_time_not_urgent % 60

        working_hours = work_time // 60
        minutes = work_time % 60

        minutes_nu_text = f"and {mins_nu} min." if mins_nu != 0 else ""
        minutes_work_text = f" and {minutes} min" if minutes != 0 else ""

        # NU first then Working hours.
        print(f"\nTotal time dedicated: {hours_nu} of hours {minutes_nu_text} dedicated and {working_hours} working hours{minutes_work_text}.\n")
        
        while True:
            go_back = input("Enter 'back' if you want to go back to main menu: ")
            if go_back == "back":
                return
    
    # Checks quota over the months divided by weekly quota
    def check_weekly_progress(self, activity: Activity): # utility

        month_name = datetime.datetime.now().strftime('%B')

        weekly_counts = self.filter_weeks_by_activity(activity)
        week_by_month_number = len(weekly_counts.index.tolist()) if not weekly_counts.empty else 0

        if not week_by_month_number or week_by_month_number == 0:
            print(f"Week 1 of {month_name}: ❌ Only 0/{int(activity.quota)}\n")

        for week, count in weekly_counts.items():
        
            status = "✅ Met" if count >= int(activity.quota) else f"❌ Only {count}/{int(activity.quota)}"
            print(f"Week {week_by_month_number} of {month_name}: {status}\n")
    
    # Returns a weekly dateframe filter by activity
    def filter_weeks_by_activity(self, activity: Activity):
        # for now just month, later I can add year
        # target_month = 8 # just testing other month

        target_month = datetime.datetime.now().month

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

    def add_activity(self, activity: Activity):
        today = datetime.date.today().isoformat()
        progress_entry = {
                "date": today,
                "tasks_finished": activity.name,
                "time_dedicated": activity.time,
                "rewards": activity.reward
                }
        
        self.save_progress(progress_entry)
        self.refresh()
        
        print(f"✅ Progress updated: {activity.name} ({activity.time} mins)")
    
    def save_progress(self, progress_entry):
        filename=PROGRESS_FILE
        new_row = pd.DataFrame([progress_entry])  # Wrap in list to create a single-row DataFrame

        if os.path.exists(filename):
            existing = pd.read_csv(filename)
            updated = pd.concat([existing, new_row], ignore_index=True)
        else:
            updated = new_row

        updated.to_csv(filename, index=False)

class Activity:
    def __init__(self, data):
        self.name = data["activity"]
        self.time = int(data["activity_time"])
        self.reward = data["reward"]
        self.is_urgent = data["urgent"].lower() == "yes"
        self.quota = data["quota_per_week"]
        self.trigger_question = data["trigger_question"]
    
    def is_repeated(self, tracker: ProgressTracker): 

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

class CLI:
    def __init__(self):
        self.manager = None
        self.tracker = ProgressTracker()

    def run(self):

        sheets_id = input("Share your GoogleSheets Activities file id:")
        self.manager = ActivityManager(sheets_id)

        while True:
            print("\nAvailable activities:")
            self.manager.list_activities(self.tracker)
            print(f"\n{len(self.manager.activities) + 1}. Update progress")
            print(f"{len(self.manager.activities) + 2}. Show progress")

            try:

                updateProgress_choice =  len(self.manager.activities)
                show_progress_choice = len(self.manager.activities) + 1

                choice = int(input("\nChoose an activity number (or 0 to exit): ")) - 1

                if choice == -1:
                    print("👋 Exiting. See you next time.")
                    break

                elif choice == updateProgress_choice:
                    self.tracker.delete_progress()
                    continue

                elif choice == show_progress_choice:
                    self.tracker.show_progress()
                    continue

                elif choice < 0 or choice >= len(self.manager.activities):
                    print("❌ Invalid choice. Try again.")
                    time.sleep(2)
                    continue

                raw_activity = self.manager.get_activity(choice)
                activity = Activity(raw_activity)

            except (ValueError, IndexError):
                print("❌ Invalid choice. Try again.")
                continue 
                
            self.handle_activity(activity, self.tracker)
            time.sleep(2)

    def handle_activity(self, activity, tracker):
        if activity.is_urgent:
            print(f"⚡ Urgent task: {activity.name}")

            if activity.is_repeated(tracker):
                print("You've done this activity already.")

            elif not activity.is_repeated(tracker):

                hours_worked = int(input("How many hours did you work? (Enter a number): "))
                activity.time = hours_worked * 60

                if QuestionUtility.ask_yes_no("Did you finish it?"):
                    tracker.add_activity(activity)
                else:
                    print("❌ Task not finished.")

            else:
                print("⏭️ Skipped.")

        else:
            print(f"\nOptional task: {activity.name}")
            # print(f"Trigger: {activity.trigger_question}\n")

            # Weekly progress
            tracker.check_weekly_progress(activity)

            if activity.is_repeated(tracker):
                print("You've done this activity already.")
            
            elif QuestionUtility.ask_yes_no(activity.trigger_question):
                tracker.add_activity(activity)
                tracker.refresh()
            else:
                print("⏭️ Skipped.")

if __name__ == "__main__":
    CLI().run()