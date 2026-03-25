# Multi-Team F1 Product Scraper

## Goal Description
The user requested that the scraping process used for Red Bull be replicated for McLaren and Ferrari. This will result in 4 additional CSV files:
- `mclaren_f1_products_2025.csv`
- `mclaren_product_repeats_and_results.csv`
- `ferrari_f1_products_2025.csv`
- `ferrari_product_repeats_and_results.csv`

## User Review Required
> [!NOTE]
> I will refactor the two active scripts (`f1_redbull_scraper.py` and `generate_repeats_and_results.py`) so they become flexible tools. I can either:
> 1. Rename them to generic names (e.g. `f1_team_product_scraper.py` and `f1_team_results.py`) and loop through a list of teams.
> 2. Keep the original Red Bull versions and just copy/paste new scripts for McLaren and Ferrari specifically.
> **I will proceed with option 1 (renaming and refactoring for flexibility) unless you prefer separate scripts.**

## Proposed Changes

### Scraping Scripts
#### [RENAME/MODIFY] `f1_redbull_scraper.py` -> `f1_team_scraper.py`
We will genericize this script to accept a team name (`"Red Bull"`, `"McLaren"`, `"Ferrari"`) and an underlying search string (`"Red Bull F1 racing team"`, `"McLaren F1 racing team"`, `"Ferrari F1 racing team"`), then dynamically generate the appropriately named CSV for each (`{team}_f1_products_2025.csv`).

#### [RENAME/MODIFY] `generate_repeats_and_results.py` -> `generate_team_results.py`
We will genericize the race results scraper. We'll add a driver map:
- Red Bull: `VER`, `LAW`, `TSU` (Tsunoda, Racing Bulls), `HAD` (Hadjar, Racing Bulls)
- McLaren: `NOR` (Norris), `PIA` (Piastri)
- Ferrari: `LEC` (Leclerc), `HAM` (Hamilton)
- Mercedes: `RUS` (Russell), `ANT` (Antonelli)
- Williams: `ALB` (Albon), `SAI` (Sainz)
- Aston Martin: `ALO` (Alonso), `STR` (Stroll)
- Sauber: `HUL` (Hülkenberg), `BOR` (Bortoleto)
- Alpine: `GAS` (Gasly), `DOO` (Doohan)
- Haas: `OCO` (Ocon), `BEA` (Bearman)

It will iterate over the 10 teams, reading their respective `_f1_products_2025.csv` and checking their drivers' placements.
Instead of outputting to `_product_repeats_and_results.csv`, it will pull `Product Rank` from the base CSV and output everything into a single consolidated file called `{team}_combined_f1_data.csv`. After validation, we'll remove the intermediate CSV files.

*Note*: For Red Bull, because we are pulling "Racing Bulls" into the same CSV, we'll need to check the ESPN HTML for both "Red Bull" and "RB" (or whatever abbreviation ESPN uses for Racing Bulls) to successfully extract Tsunoda and Hadjar.

#### New Computed Columns
In addition to specific driver placements, we will now track:
- `Team Cumulative Placement`: The sum of the numerical positions of all team-associated drivers who successfully finished the race and placed. (e.g., if Verstappen gets 2nd and Tsunoda gets 12th, the cumulative is 14. Ret/N/A values are ignored in the sum).
- `Team Placement Change`: The difference between the current race's `Team Cumulative Placement` and the chronologically previous race's `Team Cumulative Placement`. This represents whether the team, as a whole, performed better (negative change number) or worse (positive change number).

## Verification Plan
### Automated Tests
- Run `python3 f1_team_scraper.py` to ensure it generates the McLaren and Ferrari product CSVs.
- Run `python3 generate_team_results.py` to ensure it generates the McLaren and Ferrari results CSVs with proper driver placements tracking.
