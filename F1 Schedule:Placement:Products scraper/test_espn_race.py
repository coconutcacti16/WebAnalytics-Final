import requests
from bs4 import BeautifulSoup

url = "https://www.espn.com/f1/results/_/id/600052045"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.title.text)

tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"Table {i} has {len(rows)} rows")
    if len(rows) > 0:
        for row in rows[:5]:
            cols = row.find_all(['td', 'th'])
            print(" | ".join([c.text.strip().replace('\n', ' ') for c in cols]))
    print("---")
