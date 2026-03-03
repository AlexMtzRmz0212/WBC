#!/usr/bin/env python3
"""
Generate an ICS calendar file for the 2023 World Baseball Classic schedule.
All times are based on US Eastern Time broadcast schedules and converted to UTC.
"""

import datetime
import sys

# Try to use zoneinfo (Python 3.9+), fallback to pytz
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone as ZoneInfo  # requires `pip install pytz`

# ------------------------------------------------------------
# Game data: each entry is (date_str, time_str, pool, team1, team2, broadcaster)
# ------------------------------------------------------------
GAMES = [
    # Pool B
    ("04-Mar", "10:00 PM", "B", "Chinese Taipei", "Australia", "FS1 / Fox Deportes"),
    ("05-Mar", "5:00 AM", "B", "Czech Republic", "South Korea", "FS1 / Fox Deportes"),
    ("05-Mar", "10:00 PM", "B", "Australia", "Czech Republic", "FS1 / Fox Deportes"),
    ("06-Mar", "5:00 AM", "B", "Japan", "Chinese Taipei", "FS1 / Fox Deportes"),
    ("06-Mar", "10:00 PM", "B", "Chinese Taipei", "Czech Republic", "FS2"),
    ("07-Mar", "5:00 AM", "B", "South Korea", "Japan", "FS1 / Fox Deportes"),
    ("07-Mar", "10:00 PM", "B", "Chinese Taipei", "South Korea", "FS2"),
    ("08-Mar", "6:00 AM", "B", "Australia", "Japan", "FS1 / Fox Deportes"),
    ("09-Mar", "6:00 AM", "B", "South Korea", "Australia", "FS1 / Fox Deportes"),
    ("10-Mar", "6:00 AM", "B", "Czech Republic", "Japan", "FS1 / Fox Deportes"),

    # Pool A (San Juan)
    ("06-Mar", "11:00 AM", "A", "Cuba", "Panama", "FS2 / Fox Deportes"),
    ("06-Mar", "6:00 PM", "A", "Puerto Rico", "Colombia", "FS1 / Fox Deportes"),
    ("07-Mar", "11:00 AM", "A", "Colombia", "Canada", "FS2 / Fox Deportes"),
    ("07-Mar", "6:00 PM", "A", "Panama", "Puerto Rico", "FS1 / Fox Deportes"),
    ("08-Mar", "12:00 PM", "A", "Colombia", "Cuba", "FS2"),
    ("08-Mar", "7:00 PM", "A", "Panama", "Canada", "FS2"),
    ("09-Mar", "12:00 PM", "A", "Colombia", "Panama", "FS2"),
    ("09-Mar", "7:00 PM", "A", "Cuba", "Puerto Rico", "FS1"),
    ("10-Mar", "7:00 PM", "A", "Canada", "Puerto Rico", "Tubi"),
    ("11-Mar", "3:00 PM", "A", "Canada", "Cuba", "FS2 / Fox Deportes"),

    # Pool C
    ("06-Mar", "1:00 PM", "C", "Mexico", "Great Britain", "FS1 / Fox Deportes"),
    ("06-Mar", "8:00 PM", "C", "USA", "Brazil", "FOX / Fox Deportes"),
    ("07-Mar", "1:00 PM", "C", "Brazil", "Italy", "Fox Sports App"),
    ("07-Mar", "8:00 PM", "C", "Great Britain", "USA", "FOX"),
    ("08-Mar", "1:00 PM", "C", "Great Britain", "Italy", "Tubi"),
    ("08-Mar", "8:00 PM", "C", "Brazil", "Mexico", "FS1 / Fox Deportes"),
    ("09-Mar", "1:00 PM", "C", "Brazil", "Great Britain", "Tubi"),
    ("09-Mar", "8:00 PM", "C", "Mexico", "USA", "FOX / Fox Deportes"),
    ("10-Mar", "9:00 PM", "C", "Italy", "USA", "FS1 / Fox Deportes"),
    ("11-Mar", "7:00 PM", "C", "Italy", "Mexico", "Tubi"),

    # Pool D
    ("06-Mar", "12:00 PM", "D", "Netherlands", "Venezuela", "Tubi"),
    ("06-Mar", "7:00 PM", "D", "Nicaragua", "Dominican Republic", "FS2"),
    ("07-Mar", "12:00 PM", "D", "Nicaragua", "Netherlands", "Tubi"),
    ("07-Mar", "7:00 PM", "D", "Israel", "Venezuela", "FS2"),
    ("08-Mar", "12:00 PM", "D", "Netherlands", "Dominican Republic", "FOX / Fox Deportes"),
    ("08-Mar", "7:00 PM", "D", "Nicaragua", "Israel", "Tubi"),
    ("09-Mar", "12:00 PM", "D", "Dominican Republic", "Israel", "FS1 / Fox Deportes"),
    ("09-Mar", "7:00 PM", "D", "Venezuela", "Nicaragua", "FS2"),
    ("10-Mar", "7:00 PM", "D", "Israel", "Netherlands", "FS App / Fox Deportes"),
    ("11-Mar", "8:00 PM", "D", "Dominican Republic", "Venezuela", "FS1 / Fox Deportes"),
]

POOL_LOCATIONS = {
    "A": "San Juan, Puerto Rico",
    "B": "Tokyo, Japan",
    "C": "Phoenix, Arizona, USA",
    "D": "Miami, Florida, USA",
}

def parse_datetime_ny(date_str, time_str, year=2026):
    """Parse '04-Mar' and '10:00 PM' into an aware datetime in America/New_York."""
    day, month_abbr = date_str.split('-')
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    month = month_map[month_abbr]
    time_obj = datetime.datetime.strptime(time_str, "%I:%M %p").time()
    naive = datetime.datetime(year, month, int(day), time_obj.hour, time_obj.minute)
    # Assume all times are US Eastern Time (broadcast schedule)
    return naive.replace(tzinfo=ZoneInfo("America/New_York"))

def escape_ics_text(text):
    return text.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')

def generate_ics(games, filename="wbc2026_schedule.ics"):
    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//WBC Schedule Generator//EN")
    lines.append("CALSCALE:GREGORIAN")
    lines.append("METHOD:PUBLISH")

    for game in games:
        date_str, time_str, pool, team1, team2, broadcaster = game
        start_ny = parse_datetime_ny(date_str, time_str)
        end_ny = start_ny + datetime.timedelta(hours=3)  # assume 3-hour game

        # Convert to UTC for the ICS (using 'Z' suffix)
        start_utc = start_ny.astimezone(datetime.timezone.utc)
        end_utc = end_ny.astimezone(datetime.timezone.utc)

        dt_format = "%Y%m%dT%H%M%SZ"
        dtstart = start_utc.strftime(dt_format)
        dtend = end_utc.strftime(dt_format)

        summary = f"{team1} vs {team2} (Pool {pool})"
        location = POOL_LOCATIONS.get(pool, "")
        description = f"Broadcast: {broadcaster}\\nPool: {pool}\\nLocation: {location}"

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{start_utc.strftime('%Y%m%dT%H%M%S')}-{team1}-{team2}@wbc2026")
        lines.append(f"DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime(dt_format)}")
        lines.append(f"DTSTART:{dtstart}")
        lines.append(f"DTEND:{dtend}")
        lines.append(f"SUMMARY:{escape_ics_text(summary)}")
        lines.append(f"DESCRIPTION:{escape_ics_text(description)}")
        if location:
            lines.append(f"LOCATION:{escape_ics_text(location)}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines))
    print(f"✅ ICS file written to {filename}")

if __name__ == "__main__":
    generate_ics(GAMES)