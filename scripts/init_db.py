#!/usr/bin/env python3
"""
Initialize SQLite database with Indonesian region data.
Download data from: https://github.com/yusufsyaifudin/wilayah-indonesia
"""
import sqlite3
import json
import urllib.request
from pathlib import Path

DB_PATH = "data/regions.db"

# URLs for region data
URLS = {
    "provinces": "https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/provinces.json",
    "regencies": "https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/regencies.json",
    "districts": "https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/districts.json",
}

def download_data():
    """Download region data from GitHub"""
    data = {}
    for key, url in URLS.items():
        print(f"Downloading {key}...")
        with urllib.request.urlopen(url) as response:
            data[key] = json.load(response)
    return data

def init_db(data):
    """Initialize SQLite database"""
    Path(DB_PATH).parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regencies (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            province_code TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS districts (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            regency_code TEXT NOT NULL
        )
    """)

    # Insert provinces - uses 'id' field
    for p in data["provinces"]:
        cursor.execute("INSERT OR REPLACE INTO provinces VALUES (?, ?)", (p["id"], p["name"]))

    # Insert regencies - uses 'id' and 'province_id'
    for r in data["regencies"]:
        # Determine type from name prefix
        name = r["name"]
        if name.startswith("KOTA "):
            reg_type = "Kota"
            name_clean = name
        elif name.startswith("KABUPATEN "):
            reg_type = "Kabupaten"
            name_clean = name
        else:
            reg_type = "Kabupaten"
            name_clean = name

        cursor.execute(
            "INSERT OR REPLACE INTO regencies VALUES (?, ?, ?, ?)",
            (r["id"], name_clean, r["province_id"], reg_type)
        )

    # Insert districts - uses 'id' and 'regency_id'
    for d in data["districts"]:
        cursor.execute(
            "INSERT OR REPLACE INTO districts VALUES (?, ?, ?)",
            (d["id"], d["name"], d["regency_id"])
        )

    conn.commit()
    conn.close()

    print(f"Database created at {DB_PATH}")
    print(f"Provinces: {len(data['provinces'])}")
    print(f"Regencies: {len(data['regencies'])}")
    print(f"Districts: {len(data['districts'])}")

if __name__ == "__main__":
    data = download_data()
    init_db(data)
