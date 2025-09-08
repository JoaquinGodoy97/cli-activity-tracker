import datetime
import calendar

class TimeUtility:
    def __init__(self, today):
        self.today = today
        self.year = self.today.year
        self.month = self.today.month
        self.day = self.today.day

    @staticmethod
    def hours_remaining_in_day() -> tuple[int, int]:
        """Calculate hours and minutes remaining in the current day."""
        now = datetime.datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        remaining = end_of_day - now
        return int(remaining.total_seconds() // 3600), int((remaining.total_seconds() % 3600) // 60)

    def get_weeks_of_month(self):
        cal = calendar.Calendar(firstweekday=0)  # Monday as start of week
        month_days = cal.monthdatescalendar(self.year, self.month)
        
        weeks = []
        for week in month_days:
            weeks.append([day for day in week if day.month == self.month])
        
        self.weeks_by_month_list = weeks
        return weeks
    
    def get_current_week_index(self):
        for i, week in enumerate(self.weeks_by_month_list):
            if self.today in week:
                return i + 1, week
        return None, None
    
    def get_weeks_of_month_iso(self):
        weeks = self.get_weeks_of_month()
        return sorted({day.isocalendar().week for week in weeks for day in week})
