import pandas as pd
from typing import Optional

class GoogleSheetsService:
    @staticmethod
    def load_activities(sheets_id: str) -> pd.DataFrame:
        """Load activities from Google Sheets CSV export."""
        ACTIVITIES_FILE = f"https://docs.google.com/spreadsheets/d/{sheets_id}/export?format=csv"
        activities = pd.read_csv(ACTIVITIES_FILE)
        
        if activities.empty:
            return pd.DataFrame()
        
        return activities
