from datetime import datetime
import pytz
import os

def get_current_time():
    tz_name = os.getenv("DEFAULT_TZ", "Africa/Nairobi")
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return f"<p>🕒 Current time in {tz_name}: <b>{now.strftime('%A, %d %B %Y, %I:%M %p')}</b></p>"
    except Exception as e:
        return f"<p>Could not retrieve time: {e}</p>"
