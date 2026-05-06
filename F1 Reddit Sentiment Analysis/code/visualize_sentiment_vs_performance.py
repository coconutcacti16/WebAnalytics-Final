import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Load the ABSA data
df = pd.read_csv('absa_detailed_output.csv')

# Driver to Team Mapping (F1 2025 predicted/actual lineup)
driver_to_team = {
    'Norris': 'McLaren', 'Piastri': 'McLaren',
    'Verstappen': 'Red Bull', 'Lawson': 'Red Bull',
    'Hamilton': 'Ferrari', 'Leclerc': 'Ferrari',
    'Russell': 'Mercedes', 'Antonelli': 'Mercedes',
    'Alonso': 'Aston Martin', 'Stroll': 'Aston Martin',
    'Gasly': 'Alpine', 'Doohan': 'Alpine',
    'Albon': 'Williams', 'Sainz': 'Williams',
    'Hulkenberg': 'Haas', 'Bearman': 'Haas', 'Ocon': 'Haas', 'Magnussen': 'Haas',
    'Tsunoda': 'VCARB', 'Hadjar': 'VCARB',
    'Bortoleto': 'Kick Sauber'
}

# Function to extract rank from title
def extract_rank(title):
    title = title.lower()
    if 'wins' in title:
        return 1
    if 'pole' in title:
        return 1 # Pole is usually synonymous with top performance
    match = re.search(r'\bp([1-9]|1[0-9]|20)\b', title)
    if match:
        return int(match.group(1))
    match = re.search(r'position ([1-9]|1[0-9]|20)', title)
    if match:
        return int(match.group(1))
    return None

# Filter for relevant aspects (driver and team)
df_filtered = df[df['Aspect'].isin(['driver', 'team', 'win', 'pole', 'podium', 'pace'])]

# Group by Race, Title, and extract entities and sentiment
results = []
for (race, title), group in df_filtered.groupby(['Race', 'Title']):
    rank = extract_rank(title)
    if rank is None:
        continue
    
    # Identify which driver/team is mentioned in the title
    title_lower = title.lower()
    found_drivers = [d for d in driver_to_team.keys() if d.lower() in title_lower]
    
    # Get average sentiment for this post
    sentiment = group['Polarity'].mean()
    
    for driver in found_drivers:
        results.append({
            'Race': race,
            'Driver': driver,
            'Team': driver_to_team[driver],
            'Rank': rank,
            'Sentiment': sentiment
        })

res_df = pd.DataFrame(results)

# Calculate Team Cumulative Performance for the race weekend
# (Inverse of rank: 1 -> 20, 20 -> 1, then sum or average)
res_df['Performance_Score'] = 21 - res_df['Rank']

# Aggregate by Race and Team to get cumulative placement
team_race_perf = res_df.groupby(['Race', 'Team'])['Performance_Score'].sum().reset_index()
team_race_perf.rename(columns={'Performance_Score': 'Team_Performance'}, inplace=True)

# Merge back to get driver sentiment per race
driver_sentiment = res_df.groupby(['Race', 'Driver', 'Team'])['Sentiment'].mean().reset_index()

final_df = pd.merge(driver_sentiment, team_race_perf, on=['Race', 'Team'])

# Create the visualization
plt.figure(figsize=(14, 10))
sns.set_style("darkgrid")

# Define a palette for teams
palette = {
    'Red Bull': '#0600EF', 'McLaren': '#FF8700', 'Ferrari': '#DC0000',
    'Mercedes': '#00D2BE', 'Williams': '#005AFF', 'Alpine': '#0090FF',
    'Haas': '#787878', 'Aston Martin': '#006F62', 'VCARB': '#6692FF',
    'Kick Sauber': '#52E252'
}

# Scatter plot: Team Performance vs Driver Sentiment
scatter = sns.scatterplot(
    data=final_df, 
    x='Team_Performance', 
    y='Sentiment', 
    hue='Team', 
    palette=palette,
    s=150, 
    alpha=0.7,
    edgecolor='w'
)

# Add trend line
sns.regplot(
    data=final_df, 
    x='Team_Performance', 
    y='Sentiment', 
    scatter=False, 
    color='white', 
    line_kws={"color": "gray", "alpha": 0.5, "ls": "--"}
)

# Label top points (high sentiment or high performance)
for i in range(final_df.shape[0]):
    if final_df.Team_Performance.iloc[i] > 15 or abs(final_df.Sentiment.iloc[i]) > 0.1:
        plt.text(
            final_df.Team_Performance.iloc[i]+0.2, 
            final_df.Sentiment.iloc[i], 
            f"{final_df.Driver.iloc[i]} ({final_df.Race.iloc[i]})", 
            fontsize=9, 
            color='white',
            bbox=dict(facecolor='black', alpha=0.3, edgecolor='none')
        )

plt.title('Driver Sentiment vs. Team Race Weekend Performance', fontsize=20, color='white', pad=20)
plt.xlabel('Team Cumulative Performance Score (High = Better Placement)', fontsize=14, color='white')
plt.ylabel('Average Driver Sentiment (Polarity)', fontsize=14, color='white')

# Legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', facecolor='#2c3e50', labelcolor='white')

# Aesthetics
plt.gca().set_facecolor('#1e1e1e')
plt.gcf().set_facecolor('#1e1e1e')
plt.tick_params(colors='white')

plt.tight_layout()
output_file = 'sentiment_vs_performance.png'
plt.savefig(output_file, facecolor='#1e1e1e', dpi=300)
print(f"Generated {output_file}")
