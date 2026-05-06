import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def parse_price_change(val):
    if pd.isna(val) or val == 'N/A':
        return None
    try:
        # Remove $, commas, and handle negative signs ($-2.45)
        clean_val = str(val).replace('$', '').replace(',', '')
        return float(clean_val)
    except ValueError:
        return None

def normalize_team(name):
    if not isinstance(name, str): return name
    name = name.strip()
    # Basic normalization for casing and spacing consistency
    mapping = {
        'Astonmartin': 'Aston Martin',
        'Mclaren': 'McLaren',
        'Redbull': 'Red Bull'
    }
    return mapping.get(name, name)

def run_combined_analysis(root_dir, output_dir):
    files = [
        os.path.join(root_dir, "Master_F1_Products.csv"),
        os.path.join(root_dir, "Historical Data", "Master_F1_Products_2021.csv"),
        os.path.join(root_dir, "Historical Data", "Master_F1_Products_2022.csv"),
        os.path.join(root_dir, "Historical Data", "Master_F1_Products_2023.csv"),
        os.path.join(root_dir, "Historical Data", "Master_F1_Products_2024.csv")
    ]
    
    all_dfs = []
    for f in files:
        if os.path.exists(f):
            print(f"Loading {f}...")
            temp_df = pd.read_csv(f)
            # Add year column if possible, but not strictly needed for this specific analysis
            all_dfs.append(temp_df)
        else:
            print(f"Warning: File not found: {f}")
            
    if not all_dfs:
        print("No files found to analyze.")
        return
        
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Normalize Team Names
    df['Team'] = df['Team'].apply(normalize_team)
    
    # Group by Team on the FULL dataframe first to ensure all teams are included
    all_teams = df['Team'].unique()
    
    # Preprocess price changes
    df['Price Change Numeric'] = df['Price Change'].apply(parse_price_change)
    df['Abs Price Change'] = df['Price Change Numeric'].abs()
    
    # Create a base analysis with all teams
    analysis_base = pd.DataFrame({'Team': all_teams})
    
    # Filter for non-zero changes for frequency and volatility calculation
    changes_df = df[df['Price Change Numeric'].notna() & (df['Price Change Numeric'] != 0)].copy()
    
    if not changes_df.empty:
        stats = changes_df.groupby('Team').agg(
            Frequency=('Price Change Numeric', 'count'),
            Total_Amount=('Abs Price Change', 'sum'),
            Average_Amount=('Abs Price Change', 'mean'),
            Volatility=('Price Change Numeric', 'std')
        ).reset_index()
        
        analysis = pd.merge(analysis_base, stats, on='Team', how='left')
    else:
        # Fallback if no changes at all
        analysis = analysis_base.copy()
        for col in ['Frequency', 'Total_Amount', 'Average_Amount', 'Volatility']:
            analysis[col] = 0.0

    # Fill NaNs with 0 (for teams with no changes)
    analysis['Frequency'] = analysis['Frequency'].fillna(0)
    analysis['Total_Amount'] = analysis['Total_Amount'].fillna(0)
    analysis['Average_Amount'] = analysis['Average_Amount'].fillna(0)
    analysis['Volatility'] = analysis['Volatility'].fillna(0)
    
    # Save CSV result
    analysis.to_csv(os.path.join(output_dir, 'historical_price_change_analysis.csv'), index=False)
    
    # Combined Visualization (Bubble Chart)
    plt.style.use('dark_background')
    plt.figure(figsize=(14, 10))
    
    # Use dark theme for sns
    sns.set_theme(style="darkgrid", rc={
        "axes.facecolor": "#000000",
        "figure.facecolor": "#000000",
        "grid.color": "#333333",
        "text.color": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white"
    })
    
    scatter = sns.scatterplot(
        data=analysis,
        x='Frequency',
        y='Volatility',
        size='Total_Amount',
        hue='Team',
        palette='bright', # More vibrant for dark background
        sizes=(1000, 8000), 
        alpha=0.8,
        edgecolor='w',
        linewidth=1.5
    )
    
    # Add labels to each bubble with anti-overlap logic
    coords = {}
    for i in range(analysis.shape[0]):
        x, y = analysis.Frequency[i], analysis.Volatility[i]
        key = (round(x, 2), round(y, 2))
        if key not in coords:
            coords[key] = []
        coords[key].append(analysis.Team[i])
        
    for (x, y), teams in coords.items():
        if len(teams) > 1 and x == 0 and y == 0:
            for j, team in enumerate(teams):
                plt.text(
                    x, 
                    y - (j * 0.5) - 0.5, 
                    team, 
                    fontsize=10, 
                    fontweight='bold',
                    color='white',
                    ha='right', 
                    va='center',
                    bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', pad=1)
                )
        else:
            for j, team in enumerate(teams):
                plt.text(
                    x, 
                    y + (j * 0.4) + 0.4, 
                    team, 
                    fontsize=11, 
                    fontweight='bold',
                    color='white',
                    ha='center', 
                    va='bottom',
                    bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', pad=1)
                )
    
    plt.title('Historical F1 Product Price Dynamics (2021-2025)\nFrequency, Volatility, and Cumulative Financial Impact', 
              fontsize=22, fontweight='bold', color='white', pad=30)
    plt.xlabel('Frequency of Price Changes (Historical Total)', fontsize=15, color='white')
    plt.ylabel('Price Volatility (Std Dev of Changes)', fontsize=15, color='white')
    
    # Customize legend
    legend = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, 
                        title='Team (Bubble size = Total Impact $)')
    plt.setp(legend.get_title(), color='white')
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'combined_historical_price_dynamics.png')
    plt.savefig(output_path, dpi=300, facecolor='black')
    print(f"Historical combined analysis saved to {output_path}")

if __name__ == "__main__":
    root_folder = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper"
    output_folder = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper/Analysis"
    run_combined_analysis(root_folder, output_folder)
