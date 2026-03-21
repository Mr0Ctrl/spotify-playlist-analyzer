import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import config
import networkx as nx


def create_radar_chart(averages: dict, title: str) -> plt.Figure:
    """Plots audio features as a radar chart (spider web)."""
    labels = list(averages.keys())
    values = list(averages.values())
    num_vars = len(labels)

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
    pos = nx.spring_layout(G, weight='weight', k=0.4, iterations=256, seed=42)
    
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