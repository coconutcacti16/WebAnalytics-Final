import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Load Gephi data
nodes_df = pd.read_csv('gephi_nodes.csv')
edges_df = pd.read_csv('gephi_edges.csv')

# Create Graph
G = nx.Graph()

# Add nodes with attributes
for _, row in nodes_df.iterrows():
    G.add_node(row['Id'], label=row['Label'], node_type=row['Type'], weight=row['Weight'])

# Add edges with attributes
for _, row in edges_df.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['Weight'])

# Team Colors Mapping
team_colors = {
    'Red Bull': '#0600EF',
    'McLaren': '#FF8700',
    'Ferrari': '#DC0000',
    'Mercedes': '#00D2BE',
    'Williams': '#005AFF',
    'Alpine': '#0090FF',
    'Haas': '#787878',
    'Aston Martin': '#006F62',
    'VCARB': '#6692FF',
    'Kick Sauber': '#52E252'
}

# Define node colors and sizes
node_colors = []
node_sizes = []
for n, d in G.nodes(data=True):
    if d['node_type'] == 'Team':
        node_colors.append(team_colors.get(n, '#e74c3c')) # Default red if not mapped
        node_sizes.append(max(500, d['weight'] * 100))
    else:
        node_colors.append('#3498db') # Driver blue
        node_sizes.append(max(300, d['weight'] * 60))

# Visualize
plt.figure(figsize=(20, 16))
# Use Kamada-Kawai for a more balanced aesthetic
pos = nx.kamada_kawai_layout(G)

# Draw edges with varying thickness and transparency
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
max_weight = max(edge_weights) if edge_weights else 1
normalized_widths = [2 + (w / max_weight) * 8 for w in edge_weights]
nx.draw_networkx_edges(G, pos, width=normalized_widths, alpha=0.2, edge_color='#ecf0f1')

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors='#ffffff', linewidths=1.5)

# Draw labels with background box for readability
labels = {n: n for n in G.nodes()}
for node, (x, y) in pos.items():
    plt.text(x, y + 0.04, node, fontsize=12, fontweight='bold', ha='center', color='white',
             bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))

plt.title('F1 2025 Reddit Relationship Network Analysis', fontsize=26, color='white', fontweight='bold', pad=30)
plt.suptitle('Entity Co-occurrence in Community Discussions', fontsize=16, color='#bdc3c7', y=0.92)

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Teams (Thematic Colors)', markerfacecolor='#e74c3c', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='Drivers', markerfacecolor='#3498db', markersize=12),
    Line2D([0], [0], color='#ecf0f1', lw=2, label='Relationship Strength', alpha=0.5)
]
plt.legend(handles=legend_elements, loc='upper right', facecolor='#2c3e50', edgecolor='white', labelcolor='white', fontsize=12)

# Set background to ultra-dark
plt.gca().set_facecolor('#0b0e11')
plt.gcf().set_facecolor('#0b0e11')

plt.axis('off')
plt.tight_layout()

# Save final version
output_file = 'gephi_visual_model.png'
plt.savefig(output_file, facecolor='#0b0e11', dpi=300)
print(f"Generated {output_file}")
