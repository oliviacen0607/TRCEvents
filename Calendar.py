import requests
from icalendar import Calendar
from io import BytesIO
from icalendar import Event

keywords = ["Climbing Connections", "Member Guest Hour"]

urls_with_prefix = {
    "https://app.rockgympro.com/ical/public/0d6c7fa257084fd3b9628ca1759d88eb": "TRC Durham",
    "https://app.rockgympro.com/ical/public/ff72f7c8859742ada90d47dfdf1bbb97": "TRC Morrisville",
    "https://app.rockgympro.com/ical/public/7fa510dd88f746378b4e0d79da753e70": "TRC Raleigh",
    "https://app.rockgympro.com/ical/public/8a61329b24414b9e9f5313d64661c0c8": "TRC Salvage Yard",
}

filtered_calendar = Calendar()
filtered_calendar.add('prodid', '-//Filtered Rock Gym Calendar//mxm.dk//')
filtered_calendar.add('version', '2.0')


# 遍历链接
for url, prefix in urls_with_prefix.items():
    response = requests.get(url)
    cal = Calendar.from_ical(response.content)
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get("SUMMARY"))
            if any(keyword in summary for keyword in keywords):
                new_event = Event()
                for key, value in component.items():
                    new_event.add(key, value)
                for subcomponent in component.subcomponents:
                    new_event.add_component(subcomponent)

                # 修改标题
                new_event["SUMMARY"] = f"{prefix} {summary}"
                new_event.add("CATEGORIES", prefix)

                filtered_calendar.add_component(new_event)
import os

folder = r"C:\Users\ocen\Desktop\Integration\Calendar"
output_path = os.path.join(folder, "filtered_rockgym_events.ics")
print("Attempting to save to:", output_path)

try:
    with open(output_path, "wb") as f:
        data = filtered_calendar.to_ical()
        print("Bytes to write:", len(data))
        f.write(data)
    print("✅ File written successfully")
except Exception as e:
    print("❌ Error while writing:", e)
