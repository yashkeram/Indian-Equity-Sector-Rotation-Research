import json
import requests
import pandas as pd

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Step 1: open the official Historical Data page
page_url = "https://www.niftyindices.com/reports/historical-data"

page = session.get(
    page_url,
    headers=headers,
    timeout=60
)

print("PAGE HTTP:", page.status_code)
print("PAGE TYPE:", page.headers.get("Content-Type"))
print("COOKIES:", session.cookies.get_dict())

# Step 2: call the historical-data endpoint using the same session
api_url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"

api_headers = {
    "User-Agent": headers["User-Agent"],
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": page_url,
    "Origin": "https://www.niftyindices.com",
}

index_name = "NIFTY FMCG"

payload = {
    "cinfo": json.dumps({
        "name": index_name,
        "startDate": "01-Aug-2026",
        "endDate": "30-Sep-2026",
        "indexName": index_name
    })
}

response = session.post(
    api_url,
    headers=api_headers,
    json=payload,
    timeout=60
)

print("\nAPI HTTP:", response.status_code)
print("API TYPE:", response.headers.get("Content-Type"))
print("API LENGTH:", len(response.text))
print("API PREVIEW:")
print(response.text[:1000])

if "application/json" not in response.headers.get("Content-Type", "").lower():
    print("\nNSE still returned HTML instead of JSON.")
    raise SystemExit(1)

result = response.json()

print("\nJSON RECEIVED:", type(result))

if "d" in result:
    rows = json.loads(result["d"])
    df = pd.DataFrame(rows)

    print("ROWS:", len(df))
    print("COLUMNS:", df.columns.tolist())
    print("\nDATA:")
    print(df.head())
else:
    print("No 'd' field found.")
    print(result)