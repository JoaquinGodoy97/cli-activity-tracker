import pandas as pd
import os
from ..config.settings import PROGRESS_FILE
from typing import Dict, Any

class DataService:
    
    @staticmethod
    def save_progress(progress_entry: Dict[str, Any]) -> None:
        """Save progress entry to CSV file."""
        filename = PROGRESS_FILE
        new_row = pd.DataFrame([progress_entry])  # Wrap in list to create a single-row DataFrame

        if os.path.exists(filename):
            existing = pd.read_csv(filename)
            updated = pd.concat([existing, new_row], ignore_index=True)
        else:
            updated = new_row

        updated.to_csv(filename, index=False)