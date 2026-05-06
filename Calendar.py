import requests
from icalendar import Calendar, Event
from difflib import SequenceMatcher
from datetime import datetime
import os

# ---------------------------------------------------
# Keywords to search
# ---------------------------------------------------

keywords = [
    "Climbing Connections",
    "Member Guest Hour"
]

# ---------------------------------------------------
# Calendar URLs
# ---------------------------------------------------

urls_with_prefix = {
    "https://app.rockgympro.com/ical/public/0d6c7fa257084fd3b9628ca1759d88eb": "TRC Durham",
    "https://app.rockgympro.com/ical/public/ff72f7c8859742ada90d47dfdf1bbb97": "TRC Morrisville",
    "https://app.rockgympro.com/ical/public/7fa510dd88f746378b4e0d79da753e70": "TRC Raleigh",
    "https://app.rockgympro.com/ical/public/8a61329b24414b9e9f5313d64661c0c8": "TRC Salvage Yard",
}

# ---------------------------------------------------
# Fuzzy matching function
# ---------------------------------------------------

def get_best_similarity(summary, keywords):

    summary_lower = summary.lower()

    best_score = 0
    best_keyword = None

    for keyword in keywords:

        keyword_lower = keyword.lower()

        # direct contains = perfect score
        if keyword_lower in summary_lower:
            return 1.0, keyword

        similarity = SequenceMatcher(
            None,
            summary_lower,
            keyword_lower
        ).ratio()

        if similarity > best_score:
            best_score = similarity
            best_keyword = keyword

    return best_score, best_keyword

# ---------------------------------------------------
# Create filtered calendar
# ---------------------------------------------------

filtered_calendar = Calendar()
filtered_calendar.add('prodid', '-//Filtered Rock Gym Calendar//mxm.dk//')
filtered_calendar.add('version', '2.0')

# ---------------------------------------------------
# Process each calendar
# ---------------------------------------------------

for url, prefix in urls_with_prefix.items():

    print("\n" + "=" * 70)
    print(f"READING CALENDAR: {prefix}")
    print("=" * 70)

    try:

        response = requests.get(url)

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ Failed to fetch calendar")
            continue

        cal = Calendar.from_ical(response.content)

        for component in cal.walk():

            if component.name != "VEVENT":
                continue

            summary = str(component.get("SUMMARY", ""))

            start = component.get("DTSTART")
            end = component.get("DTEND")

            start_dt = start.dt if start else None
            end_dt = end.dt if end else None

            best_score, best_keyword = get_best_similarity(
                summary,
                keywords
            )

            # ---------------------------------------------------
            # PRINT EVENT INFO
            # ---------------------------------------------------





            # ---------------------------------------------------
            # INCLUDE / FILTER
            # ---------------------------------------------------

            if best_score >= 0.85:
                print("\n" + "-" * 60)
                print(f"EVENT   : {summary}")
                if start_dt:

                    print(f"DATE    : {start_dt.strftime('%Y-%m-%d')}")

                if isinstance(start_dt, datetime):
                    print(f"START   : {start_dt.strftime('%I:%M %p')}")

                if end_dt and isinstance(end_dt, datetime):
                    print(f"END     : {end_dt.strftime('%I:%M %p')}")

                print(f"KEYWORD : {best_keyword}")
                print(f"SCORE   : {best_score:.2f}")

                print("✅ INCLUDED")

                new_event = Event()

                # copy all properties
                for key, value in component.items():
                    new_event.add(key, value)

                # copy subcomponents
                for subcomponent in component.subcomponents:
                    new_event.add_component(subcomponent)

                # modify summary
                new_event["SUMMARY"] = f"{prefix} {summary}"

                # add category
                new_event.add("CATEGORIES", prefix)

                filtered_calendar.add_component(new_event)


               
    except Exception as e:
        print(e)
# ---------------------------------------------------
# Final event count
# ---------------------------------------------------

filtered_event_count = len([
    c for c in filtered_calendar.walk()
    if c.name == "VEVENT"
])

print("\n" + "#" * 70)
print("FINAL SUMMARY")
print("#" * 70)

print(f"TOTAL FILTERED EVENTS : {filtered_event_count}")

# ---------------------------------------------------
# Save ICS
# ---------------------------------------------------

folder = r"C:\Users\ocen\Desktop\Integration\Calendar"

output_path = os.path.join(
    os.path.dirname(__file__),
    "filtered_rockgym_events.ics"
)

print("\nSaving to:")
print(output_path)

try:

    with open(output_path, "wb") as f:

        data = filtered_calendar.to_ical()

        print("BYTES TO WRITE:", len(data))

        f.write(data)

    print("✅ FILE WRITTEN SUCCESSFULLY")

except Exception as e:

    print("❌ ERROR WHILE WRITING:", e)
