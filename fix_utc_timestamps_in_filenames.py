from pathlib import Path
from datetime import datetime, timezone, timedelta

dir = Path("./shots")

timestamp_jump = datetime.strptime("20230516-123833", "%Y%m%d-%H%M%S")

for p in dir.glob("*.png"):
    print(p.name)
    timestamp = datetime.strptime(p.name, "rotselaar_%Y%m%d-%H%M%S.png")
    # print(timestamp)
    if timestamp < timestamp_jump:
        new_timestamp = timestamp + timedelta(hours=2)
        new_timestr = new_timestamp.strftime("%Y%m%d-%H%M%S")
        new_shot_file = f"rotselaar_{new_timestr}.png"
        print(new_shot_file)
        p.rename(new_shot_file)
