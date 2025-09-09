import pandas as pd
import requests

class GoogleSheetsService:
    @staticmethod
    def load_activities(sheets_id: str) -> pd.DataFrame:
        """Load activities from Google Sheets CSV export."""
        # ACTIVITIES_FILE = f"https://docs.google.com/spreadsheets/d/{sheets_id}/export?format=csv"
        # activities = pd.read_csv(ACTIVITIES_FILE)

        url = sheets_id

        url1 = "https://api.sheety.co/f8e2e2fdfbaa0f65df6bce63f16d9f7a/testActivityTracker/sheet1"

        response = requests.get(url)
        data = response.json()

        sheet_key = list(data.keys())[0]
        activities = pd.DataFrame(data[sheet_key])

        if activities.empty:
            return pd.DataFrame()
        
        return activities
