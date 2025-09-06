# productivity-tracker-cli  

The project is a **CLI Productivity Tracker** that helps you organize activities, track progress, and reflect on how much time you dedicate to urgent vs. non-urgent tasks.  

The system connects with a Google Sheets file containing your activities, and logs daily progress into a local `progress.csv`.  

With a simple interface, you can:  

- [x] Add and complete activities  
- [x] Track weekly quotas  
- [x] Review your progress history  
- [x] Delete past records by month, day, or single entry  

The tool is designed to encourage consistency, balance between urgent work and rewarding activities, and to provide insights into how you are spending your time.  

---

## Purpose  

The **Productivity Tracker** provides a way to build habits and measure how you dedicate your time.  
The main idea is to log and visualize both urgent (work) and non-urgent (rewarding) activities, keeping a fair balance.  

---

## Responsibilities  

1. **Activities Management**  
   - Connects to your own Google Sheets file with activities.  
   - Displays all available activities with urgency flags.  
   - Lets you pick and complete tasks.  

2. **Progress Tracking**  
   - Saves progress into `progress.csv`.  
   - Records task name, duration, and rewards.  
   - Checks if activities were already completed today.  

3. **Weekly Quotas**  
   - Verifies if you meet your defined weekly quota per activity.  
   - Prints per-week status with ✅ or ❌ markers.  

4. **Progress Review**  
   - Summarizes time spent on urgent vs. non-urgent tasks.  
   - Allows filtering and deletion of logs by month, day, or entry.  

---

## Setup Instructions  

To run the app locally:  

1. Clone the repository.  
2. Make sure you have **Python 3.x** installed.  
3. Install dependencies:  
   ```bash
   pip install pandas

Run the program:
```bash
python main_oop.py
```
On startup, provide your Google Sheets ID (with the activities list).

--------------------------------------------

## Techs

• Python
• Pandas
• Google Sheets (CSV export)
• CLI