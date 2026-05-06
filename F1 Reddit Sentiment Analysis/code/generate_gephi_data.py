import pandas as pd
import re
from collections import Counter

# Load the data
df = pd.read_csv('F1_2025_Reddit_Data.csv')

# Define entities to search for
drivers = [
    'Verstappen', 'Norris', 'Piastri', 'Hamilton', 'Leclerc', 'Sainz', 'Russell', 
    'Antonelli', 'Alonso', 'Stroll', 'Hulkenberg', 'Albon', 'Gasly', 'Tsunoda', 
    'Bearman', 'Colapinto', 'Lawson', 'Doohan', 'Bortoleto', 'Hadjar', 'Ocon', 'Magnussen'
]

teams = [
    'Red Bull', 'McLaren', 'Ferrari', 'Mercedes', 'Williams', 'Alpine', 'Haas', 
    'Kick Sauber', 'Sauber', 'VCARB', 'Racing Bulls', 'Aston Martin'
]

races = df['Race'].unique().tolist()

# Mapping common variations
team_map = {
    'Racing Bulls': 'VCARB',
    'Sauber': 'Kick Sauber',
    'Redbull': 'Red Bull'
}

def extract_entities(text):
    found_drivers = set()
    found_teams = set()
    found_races = set()
    
    text_lower = str(text).lower()
    
    for d in drivers:
        if d.lower() in text_lower:
            found_drivers.add(d)
            
    for t in teams:
        if t.lower() in text_lower:
            mapped_t = team_map.get(t, t)
            found_teams.add(mapped_t)
            
    for r in races:
        if r.lower() in text_lower:
            found_races.add(r)
            
    return list(found_drivers), list(found_teams), list(found_races)

# Process titles
edges = []
nodes = Counter()

for index, row in df.iterrows():
    d_list, t_list, r_list = extract_entities(row['Title'])
    
    # Also include the race from the 'Race' column
    r_list = list(set(r_list + [row['Race']]))
    
    all_entities = []
    for d in d_list:
        all_entities.append((d, 'Driver'))
    for t in t_list:
        all_entities.append((t, 'Team'))
    # for r in r_list:
    #     all_entities.append((r, 'Race'))
    
    # Update nodes
    for entity, etype in all_entities:
        nodes[entity] += 1
        
    # Create edges (combinations)
    for i in range(len(all_entities)):
        for j in range(i + 1, len(all_entities)):
            e1, t1 = all_entities[i]
            e2, t2 = all_entities[j]
            if e1 != e2:
                # Sort to ensure undirected consistency
                pair = tuple(sorted([e1, e2]))
                edges.append(pair)

# Aggregate edges
edge_counts = Counter(edges)

# Create nodes.csv
nodes_df = pd.DataFrame([
    {'Id': name, 'Label': name, 'Type': ('Team' if name in [team_map.get(t, t) for t in teams] else 'Driver'), 'Weight': count}
    for name, count in nodes.items()
])
nodes_df.to_csv('gephi_nodes.csv', index=False)

# Create edges.csv
edges_df = pd.DataFrame([
    {'Source': pair[0], 'Target': pair[1], 'Weight': count, 'Type': 'Undirected'}
    for pair, count in edge_counts.items()
])
edges_df.to_csv('gephi_edges.csv', index=False)

print(f"Generated gephi_nodes.csv with {len(nodes_df)} nodes.")
print(f"Generated gephi_edges.csv with {len(edges_df)} edges.")
