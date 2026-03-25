import requests
from bs4 import BeautifulSoup

url = "https://www.espn.com/f1/results/_/id/600052045"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table')
if len(tables) > 1:
    results_table = tables[1]
    rows = results_table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            pos = cols[0].text.strip()
            driver = cols[1].text.strip()
            team = cols[2].text.strip()
            if "Red Bull" in team:
                print(f"Driver: {driver}, Team: {team}, Pos: {pos}")
