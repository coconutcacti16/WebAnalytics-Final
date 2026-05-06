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

def run_analysis(file_path, output_dir):
    df = pd.read_csv(file_path)
    
    # Preprocess price changes
    df['Price Change Numeric'] = df['Price Change'].apply(parse_price_change)
    
    # Filter for non-zero changes
    changes_df = df[df['Price Change Numeric'].notna() & (df['Price Change Numeric'] != 0)].copy()
    changes_df['Abs Price Change'] = changes_df['Price Change Numeric'].abs()
    
    # Group by Team
    analysis = changes_df.groupby('Team').agg(
        Frequency=('Price Change Numeric', 'count'),
        Total_Amount=('Abs Price Change', 'sum'),
        Average_Amount=('Abs Price Change', 'mean'),
        Volatility=('Price Change Numeric', 'std')
    ).reset_index()
    
    # If a team has only 1 change, std is NaN, fill with 0
    analysis['Volatility'] = analysis['Volatility'].fillna(0)
    
    # Save CSV result
    analysis.to_csv(os.path.join(output_dir, 'price_change_analysis.csv'), index=False)
    
    # Combined Visualization (Bubble Chart)
    plt.figure(figsize=(12, 8))
    
    # Scale bubble sizes for visibility
    # Use a minimum size and scale by Total_Amount
    size_scale = analysis['Total_Amount'] / analysis['Total_Amount'].max() * 2000 + 500
    
    scatter = sns.scatterplot(
        data=analysis,
        x='Frequency',
        y='Volatility',
        size='Total_Amount',
        hue='Team',
        palette='viridis',
        sizes=(500, 3000),
        alpha=0.7,
        edgecolor='w',
        linewidth=2
    )
    
    # Add labels to each bubble
    for i in range(analysis.shape[0]):
        plt.text(
            analysis.Frequency[i], 
            analysis.Volatility[i], 
            analysis.Team[i], 
            fontsize=12, 
            fontweight='bold',
            ha='center', 
            va='center'
        )
    
    plt.title('F1 Product Price Dynamics: Frequency, Volatility, and Total Impact', fontsize=18, pad=20)
    plt.xlabel('Frequency of Changes (Count)', fontsize=14)
    plt.ylabel('Volatility (Std Dev of Changes)', fontsize=14)
    
    # Customize legend
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, title='Team & Impact ($)')
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'combined_price_dynamics.png'))
    print(f"Combined analysis saved to {output_dir}")

if __name__ == "__main__":
    csv_file = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper/Master_F1_Products.csv"
    output_folder = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper/Analysis"
    run_analysis(csv_file, output_folder)
