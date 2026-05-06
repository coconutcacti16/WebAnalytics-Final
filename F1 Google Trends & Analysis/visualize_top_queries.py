import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_improved_visual(csv_path, output_path):
    # Load data
    df = pd.read_csv(csv_path)
    
    # Setup the figure
    fig, ax = plt.subplots(figsize=(14, 12))
    fig.patch.set_facecolor('#0B0E14')  # Deep dark background
    ax.set_facecolor('#0B0E14')
    
    # Hide axes
    ax.axis('off')
    
    # Title
    plt.text(0.5, 0.95, 'F1 GOOGLE TRENDS: TOP RELATED QUERIES', 
             color='white', fontsize=28, fontweight='bold', 
             ha='center', va='center', transform=ax.transAxes,
             fontfamily='sans-serif')
    
    plt.text(0.5, 0.91, 'Global Search Interest Analysis (2021-2025)', 
             color='#8892B0', fontsize=16, 
             ha='center', va='center', transform=ax.transAxes)

    # Colors for each year
    colors = ['#00F5FF', '#FF007F', '#E0E0E0', '#FFD700', '#00FF7F']
    
    # Starting position
    y_start = 0.82
    y_step = 0.16
    
    for i, row in df.iterrows():
        year = str(row['Year'])
        color = colors[i % len(colors)]
        y_pos = y_start - (i * y_step)
        
        # Draw a "card" background using FancyBboxPatch
        box = patches.FancyBboxPatch((0.05, y_pos - 0.07), 0.9, 0.14, 
                                     boxstyle="round,pad=0.01,rounding_size=0.02",
                                     linewidth=1, edgecolor=color, 
                                     facecolor='#112240', alpha=0.3, 
                                     transform=ax.transAxes)
        ax.add_patch(box)
        
        # Year label
        plt.text(0.08, y_pos, year, color=color, fontsize=36, fontweight='bold', 
                 ha='left', va='center', transform=ax.transAxes)
        
        # Categories and content
        categories = [
            ('WEB', row['Web Search'], '#64FFDA'),
            ('SHOP', row['Shopping Search'], '#F4A261'),
            ('YOUTUBE', row['YouTube Search'], '#E76F51')
        ]
        
        x_start = 0.22
        for j, (cat_name, content, cat_color) in enumerate(categories):
            # Category label
            plt.text(x_start, y_pos + 0.03 - (j * 0.03), f"{cat_name}:", 
                     color=cat_color, fontsize=12, fontweight='bold', 
                     ha='left', va='center', transform=ax.transAxes)
            
            # Content
            # Handle long strings by splitting or just ensuring enough space
            plt.text(x_start + 0.1, y_pos + 0.03 - (j * 0.03), content, 
                     color='white', fontsize=14, 
                     ha='left', va='center', transform=ax.transAxes)

    # Footer
    plt.text(0.5, 0.02, 'Data Source: Google Trends Export | Generated for Women in STEM Web Analytics Project', 
             color='#495670', fontsize=10, style='italic',
             ha='center', va='center', transform=ax.transAxes)

    # Add a subtle "F1" accent line at the bottom
    line = plt.Line2D([0.1, 0.9], [0.05, 0.05], color='red', linewidth=3, alpha=0.5, transform=ax.transAxes)
    ax.add_line(line)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0B0E14')
    print(f"Improved visual saved to {output_path}")

if __name__ == "__main__":
    base_dir = "/Users/emma/Desktop/1 - web analytics/Final Project/F1 Schedule:Placement:Products scraper/F1 Schedule:Placement:Products scraper/F1 Google Trends"
    csv_file = os.path.join(base_dir, "f1_top_queries_2021_2025.csv")
    output_file = os.path.join(base_dir, "f1_top_queries_visual_improved.png")
    
    create_improved_visual(csv_file, output_file)
