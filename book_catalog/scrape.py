import os
import requests

# Create folders
os.makedirs("openlibrary_json", exist_ok=True)
os.makedirs("openlibrary_covers", exist_ok=True)

# Sample list of 100 work IDs (replace with real IDs or scrape from a source)
work_ids = [
    "OL64365W",
    "OL262460W",
    "OL134333W",
    "OL52114W",
    "OL45865W",
    "OL52257W",
    "OL46876W",
    "OL7984948W",
    "OL7924103W",
    "OL827976W",
    "OL2688199W",
    "OL47750W",
    "OL59979W",
    "OL1914079W",
    "OL103858W",
    "OL3740416W",
    "OL59797W",
    "OL5969057W",
    "OL53026W",
    "OL2950942W",
    "OL17376W",
    "OL13061121W",
    "OL35377003W",
    "OL24401815W",
    "OL13581312W",
    "OL14949631W",
    "OL29349936W",
    "OL17498461W",
    "OL43037440W",
    "OL6041036W",
    "OL6043391W",
    "OL2651611W",
    "OL3252475W",
    "OL6411072W",
    "OL1169615W",
    "OL24703307W",
    "OL8479787W"
]

for work_id in work_ids:
    work_url = f"https://openlibrary.org/works/{work_id}.json"
    try:
        response = requests.get(work_url)
        response.raise_for_status()
        data = response.json()

        print(data)

        # Save JSON
        json_path = f"openlibrary_json/{work_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Save cover if exists
        covers = data.get("covers", [])
        if covers:
            cover_id = covers[0]
            image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            img_data = requests.get(image_url).content
            image_path = f"openlibrary_covers/{work_id}.jpg"
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)

        print(f"Saved: {work_id}")

    except Exception as e:
        print(f"Failed: {work_id} - {e}")
