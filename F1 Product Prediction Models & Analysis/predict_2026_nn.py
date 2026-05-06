import pandas as pd
import glob
import os
import re
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler

def train_and_predict_2026():
    base_path = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper"
    hist_dir = os.path.join(base_path, "Historical Data")
    analysis_dir = os.path.join(base_path, "Analysis")
    
    # 1. Load historical data (2021-2025)
    files = sorted(glob.glob(os.path.join(hist_dir, "Master_F1_Products_*.csv")))
    all_data = []
    
    for f in files:
        year_match = re.search(r'202\d', f)
        if not year_match: continue
        year = int(year_match.group())
        if year > 2025: continue
        
        df = pd.read_csv(f)
        df['Year'] = year
        df['Score'] = 21 - df['Product Rank']
        all_data.append(df[['Year', 'Team', 'Product Name', 'Score', 'Product Link']])
        
    full_df = pd.concat(all_data, ignore_index=True)
    
    # 2. Preprocess for Neural Network
    # We want to predict Score based on Year and Team
    # We'll also include Product Name characteristics (e.g., category)
    def get_cat(name):
        n = str(name).lower()
        if 'women' in n or 'ladies' in n: return 2
        if 'men' in n: return 1
        return 0
    
    full_df['Category'] = full_df['Product Name'].apply(get_cat)
    
    # Encode Team names
    le_team = LabelEncoder()
    full_df['Team_Enc'] = le_team.fit_transform(full_df['Team'])
    
    # Training set: Year, Team_Enc, Category -> Score
    X = full_df[['Year', 'Team_Enc', 'Category']]
    y = full_df['Score']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Neural Network Model (MLP)
    print("Training neural network model...")
    mlp = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    mlp.fit(X_scaled, y)
    
    # 4. Predict for 2026
    # We'll take unique products from historical data as candidates for 2026
    candidates = full_df[['Team', 'Product Name', 'Category', 'Product Link']].drop_duplicates(subset=['Team', 'Product Name'])
    candidates['Year'] = 2026
    candidates['Team_Enc'] = le_team.transform(candidates['Team'])
    
    X_pred = candidates[['Year', 'Team_Enc', 'Category']]
    X_pred_scaled = scaler.transform(X_pred)
    
    candidates['Predicted_Score'] = mlp.predict(X_pred_scaled)
    
    # Get top 3 predicted products per team
    predicted_top_3 = candidates.sort_values(['Team', 'Predicted_Score'], ascending=[True, False]).groupby('Team').head(3)
    
    # 5. Generate 2026 Predicted CSV
    # Mimic structure: Team, Race Date, Race Name, Product Rank, Product Name, Product Link
    # Since we don't have the full 2026 race-by-race actuals yet in this script, 
    # we'll generate the top products for the "start of season" races.
    
    races_2026 = [
        {"Date": "Mar 13 - 15", "Name": "Qatar Airways Australian GP"},
        {"Date": "Mar 20 - 23", "Name": "Heineken Chinese GP"},
        {"Date": "Apr 3 - 6", "Name": "Aramco Japanese GP"},
        {"Date": "Apr 11 - 13", "Name": "Gulf Air Bahrain GP"}
    ]
    
    rows = []
    for race in races_2026:
        for team in predicted_top_3['Team'].unique():
            team_products = predicted_top_3[predicted_top_3['Team'] == team]
            for i, (_, p) in enumerate(team_products.iterrows()):
                rows.append({
                    "Team": p['Team'],
                    "Race Date": race['Date'],
                    "Race Name": race['Name'],
                    "Product Rank": i + 1,
                    "Product Name": p['Product Name'],
                    "Product Link": p['Product Link']
                })
                
    predicted_df = pd.DataFrame(rows)
    output_path = os.path.join(analysis_dir, "PREDICTED_best_selling_2026.csv")
    predicted_df.to_csv(output_path, index=False)
    print(f"Predicted best sellers saved to {output_path}")

if __name__ == "__main__":
    train_and_predict_2026()
