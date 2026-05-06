import os
import csv
import requests
from bs4 import BeautifulSoup
import re

def get_race_ids():
    """Fetches the 2025 F1 Schedule from ESPN and maps Race Name to Race ID."""
    url = "https://www.espn.com/f1/schedule/_/year/2025"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    race_map = {}
    
    table = soup.find('table')
    if not table:
        print("No schedule table found on ESPN.")
        return race_map
        
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            date_text = cols[0].text.strip()
            race_name = cols[1].text.strip()
            
            if date_text.lower() == 'dates' or not date_text:
                continue
                
            # Find the link inside the race name column
            link = cols[1].find('a')
            if link and 'href' in link.attrs:
                href = link['href']
                match = re.search(r'/id/(\d+)', href)
                if match:
                    race_id = match.group(1)
                    race_map[race_name] = race_id
    
    return race_map

def get_team_placements(race_id, team_search, drivers):
    """Scrapes the ESPN results page for a race and extracts specific driver placements.
    `drivers` is a list of dicts: [{'code': 'VER', 'name': 'Verstappen'}, ...]
    """
    url = f"https://www.espn.com/f1/results/_/id/{race_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    
    # Initialize all driver positions to N/A
    placements = {d['code']: "N/A" for d in drivers}
    
    # If the page doesn't exist or redirects weirdly
    if response.status_code != 200:
        return placements
        
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    # Usually the results table is the second table or the one with "Pos", "Driver", "Team"
    results_table = None
    for table in tables:
        # Check if the table has 'Pos' and 'Driver' headers
        headers_row = table.find('tr')
        if headers_row:
            headers_text = headers_row.text.lower()
            if 'pos' in headers_text and 'driver' in headers_text:
                results_table = table
                break
                
    if not results_table and len(tables) > 1:
        # Fallback to the second table if headers aren't clear
        results_table = tables[1]
    
    if results_table:
        rows = results_table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                pos = cols[0].text.strip()
                driver = cols[1].text.strip()
                team_col = cols[2].text.strip()
                
                # Check if this row belongs to any of the valid team search terms
                is_target_team = False
                if isinstance(team_search, list):
                    for ts in team_search:
                        if ts.lower() in team_col.lower():
                            is_target_team = True
                            break
                else:
                    if team_search.lower() in team_col.lower():
                        is_target_team = True
                        
                if is_target_team:
                    for d in drivers:
                        if d['code'] in driver or d['name'] in driver:
                            placements[d['code']] = pos
                            break

    return placements

def price_to_float(price_str):
    """Converts a price string like '$49.99' to a float."""
    if not price_str or price_str == 'N/A':
        return 0.0
    # Add defensive string conversion
    price_str = str(price_str)
    # Remove '$', commas, and any other non-numeric characters besides period
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        if cleaned:
            return float(cleaned)
    except ValueError:
        pass
    return 0.0

def format_price(val):
    return f"${val:.2f}"

def main():
    print("Fetching ESPN race schedule and IDs...")
    race_map = get_race_ids()
    print(f"Mapped {len(race_map)} races to IDs.")
    
    teams_config = [
        {
            "name": "redbull",
            "team_search": ["Red Bull", "Racing Bulls", "RB"],
            "drivers": [
                {"code": "VER", "name": "Verstappen"},
                {"code": "LAW", "name": "Lawson"},
                {"code": "TSU", "name": "Tsunoda"},
                {"code": "HAD", "name": "Hadjar"}
            ]
        },
        {
            "name": "mclaren",
            "team_search": "McLaren",
            "drivers": [
                {"code": "NOR", "name": "Norris"},
                {"code": "PIA", "name": "Piastri"}
            ]
        },
        {
            "name": "ferrari",
            "team_search": "Ferrari",
            "drivers": [
                {"code": "LEC", "name": "Leclerc"},
                {"code": "HAM", "name": "Hamilton"}
            ]
        },
        {
            "name": "mercedes",
            "team_search": "Mercedes",
            "drivers": [
                {"code": "RUS", "name": "Russell"},
                {"code": "ANT", "name": "Antonelli"}
            ]
        },
        {
            "name": "williams",
            "team_search": "Williams",
            "drivers": [
                {"code": "ALB", "name": "Albon"},
                {"code": "SAI", "name": "Sainz"}
            ]
        },
        {
            "name": "astonmartin",
            "team_search": "Aston Martin",
            "drivers": [
                {"code": "ALO", "name": "Alonso"},
                {"code": "STR", "name": "Stroll"}
            ]
        },
        {
            "name": "sauber",
            "team_search": ["Sauber", "Kick Sauber"],
            "drivers": [
                {"code": "HUL", "name": "Hülkenberg"},
                {"code": "BOR", "name": "Bortoleto"}
            ]
        },
        {
            "name": "alpine",
            "team_search": "Alpine",
            "drivers": [
                {"code": "GAS", "name": "Gasly"},
                {"code": "DOO", "name": "Doohan"}
            ]
        },
        {
            "name": "haas",
            "team_search": "Haas",
            "drivers": [
                {"code": "OCO", "name": "Ocon"},
                {"code": "BEA", "name": "Bearman"}
            ]
        }
    ]
    
    for team in teams_config:
        team_name = team["name"]
        print(f"\n--- Processing {team_name.upper()} ---")
        
        # Fetch results for each race mapped
        race_results = {}
        print("Fetching race results for drivers...")
        for race_name, race_id in race_map.items():
            results = get_team_placements(
                race_id, 
                team["team_search"], 
                team["drivers"]
            )
            race_results[race_name] = results
            
        # Pre-compute Cumulative Placement and Team Placement Change
        print("Calculating cumulative placements...")
        race_cumulative = {}
        previous_cum_placement = None
        
        for race_name in race_map.keys():
            placements = race_results[race_name]
            
            cum_placement = 0
            has_valid_placement = False
            for d in team["drivers"]:
                pos_str = placements[d['code']]
                if pos_str.isdigit():
                    cum_placement += int(pos_str)
                    has_valid_placement = True
                    
            if has_valid_placement:
                if previous_cum_placement is not None:
                    placement_change = cum_placement - previous_cum_placement
                    if placement_change > 0:
                        change_str = f"+{placement_change}"
                    else:
                        change_str = str(placement_change)
                else:
                    change_str = "N/A"
                    
                race_cumulative[race_name] = {
                    "cumulative": str(cum_placement),
                    "change": change_str
                }
                previous_cum_placement = cum_placement
            else:
                race_cumulative[race_name] = {
                    "cumulative": "N/A",
                    "change": "N/A"
                }
        
        input_file = f"{team_name}_f1_products_2025.csv"
        old_output_file = f"{team_name}_product_repeats_and_results.csv"
        output_file = f"{team_name}_combined_f1_data.csv"
        
        # Read the input CSV
        print(f"Reading {input_file}...")
        data = []
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"Error: {input_file} not found. Skipping {team_name}.")
            continue
            
        previous_prices = {}
        output_data = []
        
        for row in data:
            product_rank = row.get('Product Rank', 'N/A')
            product_name = row['Product Name']
            current_price_str = row['Price']
            current_price = price_to_float(current_price_str)
            
            race_name = row['Race Name']
            
            # Get driver placements, defaulting to N/A
            default_placements = {d['code']: "N/A" for d in team["drivers"]}
            placements = race_results.get(race_name, default_placements)
            
            if product_name in previous_prices:
                prev_price = previous_prices[product_name]
                price_change = current_price - prev_price
                prev_price_display = format_price(prev_price)
                if price_change > 0:
                    change_display = f"+{format_price(price_change)}"
                elif price_change < 0:
                    change_display = f"-{format_price(abs(price_change))}"
                else:
                    change_display = "$0.00"
            else:
                prev_price_display = "N/A"
                change_display = "N/A"
                
            previous_prices[product_name] = current_price
            
            # Get cumulative placements
            cum_data = race_cumulative.get(race_name, {"cumulative": "N/A", "change": "N/A"})
            
            # Build output row dynamically based on drivers list
            output_row = {
                "Race Date": row["Race Date"],
                "Race Name": race_name,
                "Product Rank": product_rank,
                "Product Name": product_name,
                "Current Price": format_price(current_price) if current_price_str != 'N/A' else 'N/A',
                "Previous Price": prev_price_display,
                "Price Change": change_display,
                "Team Cumulative Placement": cum_data["cumulative"],
                "Team Placement Change": cum_data["change"]
            }
            
            # Display name logic handling lists or strings
            display_team_search = team["team_search"][0] if isinstance(team["team_search"], list) else team["team_search"]
            
            for d in team["drivers"]:
                col_name = f"{display_team_search} Driver {d['code']} Pos"
                output_row[col_name] = placements[d['code']]
                
            output_data.append(output_row)
            
        print(f"Writing {output_file}...")
        
        display_team_search = team["team_search"][0] if isinstance(team["team_search"], list) else team["team_search"]
        driver_headers = [f"{display_team_search} Driver {d['code']} Pos" for d in team["drivers"]]
            
        headers = [
            "Race Date", 
            "Race Name",
            "Product Rank",
            "Product Name", 
            "Current Price", 
            "Previous Price", 
            "Price Change",
            "Team Cumulative Placement",
            "Team Placement Change"
        ] + driver_headers
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(output_data)
            
        print(f"Successfully processed {len(output_data)} rows and saved to {output_file}.")
        
        # Clean up intermediate files
        try:
            if os.path.exists(input_file):
                os.remove(input_file)
                print(f"Deleted intermediate file: {input_file}")
            if os.path.exists(old_output_file):
                os.remove(old_output_file)
                print(f"Deleted old split file: {old_output_file}")
        except Exception as e:
            print(f"Failed to delete intermediate files for {team_name}: {e}")

if __name__ == "__main__":
    main()
