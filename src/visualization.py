import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import config
import networkx as nx
from utils import math_utils
from itertools import combinations



def create_radar_chart(averages: dict, title: str) -> plt.Figure:
    """Plots audio features as a radar chart (spider web)."""
    labels = list(averages.keys())
    values = list(averages.values())
    num_vars = len(labels)

    values[-1] = values[-1]/200
    # Add the first value to the end to complete the circle
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Plot and fill
    ax.plot(angles, values, color=config.DataColors.VALENCE, linewidth=2)
    ax.fill(angles, values, color=config.DataColors.VALENCE, alpha=0.25)

    # Axis labels
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(title, size=15, pad=20)
    ax.set_ylim(0, 1) # Spotify data ranges from 0 to 1
    
    return fig

def create_wordcloud(genre_df, title: str) -> plt.Figure:
    """Plots genre frequencies as a word cloud."""
    # Convert DataFrame to dictionary (format required by WordCloud)
    genre_dict = dict(zip(genre_df['Genre'], genre_df['Count']))
    
    wc = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis'
    ).generate_from_frequencies(genre_dict)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.set_axis_off() # Hide axes
    ax.set_title(title, size=18, pad=10)
    
    return fig

def create_network_graph(nodes: list, edges: list, title: str) -> plt.Figure:
    """Draws a similarity graph with threshold-based filtering and colored components."""
    
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    # Add edges with weights
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    # Find connected components
    components = list(nx.connected_components(G))
    
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Use spring layout with weight as distance (smaller weight = stronger attraction)
    # This makes similar nodes (small weight) appear closer together
    pos = nx.spring_layout(G, weight='weight', k=0.25, iterations=512, seed=42,)

    
    # Colors for components (use tab10 colormap for up to 10 components)
    colors = plt.cm.tab10(np.linspace(0, 1, len(components)))
    
    # Draw edges with thickness based on similarity
    for u, v, w in edges:
        # Normalize weight to [0,1] for thickness (smaller distance = thicker edge)
        # Assuming weights are between 0 and 1 (distance)
        thickness = 1 + (1 - w) * 3  # Range: 1 to 4
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], 
                              width=thickness, alpha=0.5, edge_color='gray', ax=ax)
    
    # Draw nodes by component
    for comp_idx, component in enumerate(components):
        # Get nodes in this component
        comp_nodes = list(component)
        color = colors[comp_idx]
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, nodelist=comp_nodes, 
                              node_size=300, node_color=[color], 
                              alpha=0.7, ax=ax)
        
        # Draw labels for this component
        nx.draw_networkx_labels(G, pos, labels={node: node for node in comp_nodes}, 
                               font_size=8, ax=ax)
    
    ax.set_title(title, size=16, pad=20)
    ax.set_axis_off()
    
    return fig

def create_track_index_page(df, title, tracks_per_page=120, cols=3):
    """Prints the song list in 3 columns on the page."""
    num_tracks = len(df)
    pages = []
    page_size = (
            math_utils.mm_to_inches(config.A4_LANDSCAPE[0]),
            math_utils.mm_to_inches(config.A4_LANDSCAPE[1])
        )

    for start_idx in range(0, num_tracks, tracks_per_page):

        fig, ax = plt.subplots(figsize=page_size) # A4 Landscape
        ax.axis('off')
        ax.set_title(f"{title} (Part {start_idx//tracks_per_page + 1})", size=14, pad=20)
        
        subset = df.iloc[start_idx : start_idx + tracks_per_page]
        rows_per_col = tracks_per_page // cols
        
        for i, (idx, row) in enumerate(subset.iterrows()):
            col_idx = i // rows_per_col
            row_in_col = i % rows_per_col
            
            x_pos = -0.1 + (col_idx * (1.2 / cols))
            y_pos = 0.9 - (row_in_col * 0.022) # Satır aralığı
            
            text = f"{idx}. {row['Track Name'][:25]} - {str(row['Artist Name(s)'])[:25]}"
            ax.text(x_pos, y_pos, text, fontsize=7, family='monospace', verticalalignment='top')
            
        pages.append(fig)
    return pages

def create_distribution_plot(df, column, title, color, bins=20, unit="", x_label=None):
    """Generic histogram function for all types of numerical distributions."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    data = df[column].dropna()
    counts, edges, patches = ax.hist(data, bins=bins, color=color, edgecolor='white', alpha=0.8)
    
    # Bar üzerine sayıları yazma
    for count, edge in zip(counts, edges):
        if count > 0:
            ax.text(edge + (edges[1]-edges[0])/2, count + (max(counts)*0.01), 
                    int(count), ha='center', fontsize=8)

    ax.set_title(title, size=12)
    ax.set_xlabel(x_label if x_label else column + (f" ({unit})" if unit else ""))
    ax.set_ylabel("Frequency")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    return fig


def create_correlation_grid(df, columns, charts_per_page=8):
    """Özellikler arası korelasyonu 2D Histogramlar şeklinde sayfalara böler."""
    pairs = list(combinations(columns, 2))
    pages = []
    
    for i in range(0, len(pairs), charts_per_page):
        fig, axes = plt.subplots(2, 4, figsize=(15, 8)) # 2x4 layout
        fig.suptitle("Audio Feature Correlations", fontsize=16)
        axes = axes.flatten()
        
        subset_pairs = pairs[i : i + charts_per_page]
        
        for j, (col_x, col_y) in enumerate(subset_pairs):
            ax = axes[j]
            h = ax.hist2d(df[col_x], df[col_y], bins=15, cmap='Blues')
            ax.set_xlabel(col_x, fontsize=8)
            ax.set_ylabel(col_y, fontsize=8)
            ax.tick_params(labelsize=7)
            
        # Boş kalan eksenleri temizle
        for k in range(len(subset_pairs), len(axes)):
            axes[k].axis('off')
            
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        pages.append(fig)
    return pages

def create_ranking_plot(df, column, title, color, top_n=15, ascending=False):
    """En yüksek veya en düşük N şarkıyı sıralar."""
    # Veriyi sırala ve ilk N tanesini al
    rank_df = df.sort_values(by=column, ascending=ascending).head(top_n)
    
    # Görselleştirme için ters çevir (barh alttan başlar)
    rank_df = rank_df.iloc[::-1]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Etiket oluşturma: Index + Şarkı Adı
    labels = [f"#{idx} {name[:30]}" for idx, name in zip(rank_df.index, rank_df['Track Name'])]
    
    bars = ax.barh(labels, rank_df[column], color=color, alpha=0.8)
    ax.bar_label(bars, padding=3, fontsize=9)
    
    ax.set_title(title, size=14)
    ax.set_xlabel(column)
    plt.tight_layout()
    
    return fig