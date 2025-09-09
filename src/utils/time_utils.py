from datetime import datetime
import calendar
import pandas as pd

class TimeUtility:
    _virtual_now = None  # Class-level override

    def __init__(self, today):
        self.today = today
        self.year = self.today.year
        self.month = self.today.month
        self.day = self.today.day

    @classmethod
    def time_warped_detection(cls) -> bool:
        return cls.get_now().date().day != datetime.now().date().day

    @classmethod
    def set_virtual_now(cls, dt: datetime) -> None:
        cls._virtual_now = dt

    @classmethod
    def reset_virtual_now(cls) -> None:
        cls._virtual_now = None

    @classmethod
    def get_now(cls) -> datetime:
        return cls._virtual_now or datetime.now()

    @classmethod
    def hours_remaining_in_day(cls) -> tuple[int, int]:
        """Calculate hours and minutes remaining in the current day."""
        now = cls.get_now()
    
        print("this is now ", now)
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
    
    @staticmethod
    def pd_to_datetime(series: "pd.Series"):
        """Coerce a pandas Series to datetime, preserving NaT on failure."""
        
        return pd.to_datetime(series, errors="coerce")
