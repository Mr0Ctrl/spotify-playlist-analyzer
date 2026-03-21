import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import config
import networkx as nx
from utils import math_utils
from itertools import combinations
import seaborn as sns
import pandas as pd



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


def create_correlation_grid(df, triplets, charts_per_page=8):
    """Scatter plots with color mapping for given triplets."""
    pages = []
    
    for i in range(0, len(triplets), charts_per_page):
        n_plots = min(charts_per_page, len(triplets) - i)
        
        # Fixed 2 rows, 4 columns layout
        fig, axes = plt.subplots(2, 4, figsize=(16, 4))
        fig.suptitle("Audio Feature Correlations", fontsize=12, fontweight='bold')
        
        # Flatten axes to 1D array
        axes = axes.flatten()
        
        # Create plots
        for j, (x, y, c) in enumerate(triplets[i:i+charts_per_page]):
            ax = axes[j]
            
            # Calculate correlation
            corr_val = df[x].corr(df[y])
            
            # Scatter plot with color
            sc = ax.scatter(df[x], df[y], c=df[c], cmap='viridis', 
                          alpha=0.6, s=40, edgecolors='white', linewidth=0.5)
            # Labels and title
            ax.set_xlabel(x, fontsize=10)
            ax.set_ylabel(y, fontsize=10)
            ax.set_title(f"r = {corr_val:.2f} | Color: {c}", fontsize=8, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_aspect('auto', adjustable='box')
            
            # Add colorbar
            cbar = plt.colorbar(sc, ax=ax, shrink=0.6)
            cbar.ax.tick_params(labelsize=4)
        
        # Hide unused subplots
        for j in range(n_plots, len(axes)):
            axes[j].axis('off')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        pages.append(fig)
    
    return pages

def create_flow_analysis_grid(df, features, window_size=5):
    """
    Şarkı sırasına göre özelliklerin değişimini çizer.
    Her sayfada 4 adet grafik olacak şekilde listeler döner.
    """
    pages = []
    # 8 özelliği 4'erli gruplara ayır
    for i in range(0, len(features), 4):
        fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
        subset_features = features[i:i+4]
        
        for j, col in enumerate(subset_features):
            ax = axes[j]
            # Ham veri (soluk çizgi)
            ax.plot(df.index, df[col], alpha=0.2, color='gray')
            # Hareketli ortalama (kalın renkli çizgi)
            smooth_data = df[col].rolling(window=window_size, center=True).mean()
            ax.plot(df.index, smooth_data, color=config.DataColors.TEMPO, linewidth=2)
            
            ax.set_ylabel(col, fontsize=10)
            ax.set_ylim(0, 1)
            ax.grid(True, alpha=0.3)
            
        axes[-1].set_xlabel("Track Index (Order in Playlist)")
        plt.tight_layout()
        pages.append(fig)
    return pages
    
def create_top_bottom_tables_page(df: pd.DataFrame, features: list, title: str = "Feature Extremes (Top & Bottom 10 Tracks)"):
    """
    Belirtilen özellikler için en yüksek ve en düşük 10 şarkıyı
    2 sayfaya (her sayfada 8 tablo, 2 satır x 4 sütun) bölecek şekilde tablolar oluşturur.
    """
    pages = []
    
    # 8 özelliği 4'erli 2 gruba ayırıyoruz (her sayfa için 4 özellik -> 4 Top + 4 Bottom = 8 Tablo)
    feature_chunks = [features[i:i + 4] for i in range(0, len(features), 4)]
    
    for chunk_idx, chunk in enumerate(feature_chunks):
        # A4 Landscape boyutunda, 2 satır (Top, Bottom), 4 sütun (Özellikler)
        fig, axes = plt.subplots(2, 4, figsize=(15, 8.5))
        fig.suptitle(f"{title} - Part {chunk_idx + 1}", fontsize=16, weight='bold', y=0.98)
        
        for col_idx, feature in enumerate(chunk):
            # --- 1. Top 10 (En Yüksekler) ---
            # İlgili özelliğe göre azalan (descending) sırala
            top_df = df.sort_values(by=feature, ascending=False).head(10)
            
            # Tablo için veriyi hazırla: Sadece Şarkı Adı ve Değer
            # Şarkı isimlerini uzunsa kesiyoruz (max 20 karakter)
            top_data = [
                [f"{row['Track Name'][:20]}...", f"{row[feature]:.2f}"] 
                for _, row in top_df.iterrows()
            ]
            
            ax_top = axes[0, col_idx]
            ax_top.axis('off')
            ax_top.set_title(f"Highest {feature}", fontsize=10, weight='bold', color='darkgreen', pad=5)
            
            table_top = ax_top.table(
                cellText=top_data,
                colLabels=["Track", "Value"],
                cellLoc='left',
                loc='center',
                colWidths=[0.75, 0.25]
            )
            table_top.auto_set_font_size(False)
            table_top.set_fontsize(8)
            table_top.scale(1, 1.2) # Satır aralıklarını hafif aç
            
            # Başlık satırını renklendir
            for (row, col), cell in table_top.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#2ecc71') # Yeşil tonu
            
            # --- 2. Bottom 10 (En Düşükler) ---
            # İlgili özelliğe göre artan (ascending) sırala
            bottom_df = df.sort_values(by=feature, ascending=True).head(10)
            
            bottom_data = [
                [f"{row['Track Name'][:20]}...", f"{row[feature]:.2f}"] 
                for _, row in bottom_df.iterrows()
            ]
            
            ax_bottom = axes[1, col_idx]
            ax_bottom.axis('off')
            ax_bottom.set_title(f"Lowest {feature}", fontsize=10, weight='bold', color='darkred', pad=5)
            
            table_bottom = ax_bottom.table(
                cellText=bottom_data,
                colLabels=["Track", "Value"],
                cellLoc='left',
                loc='center',
                colWidths=[0.75, 0.25]
            )
            table_bottom.auto_set_font_size(False)
            table_bottom.set_fontsize(8)
            table_bottom.scale(1, 1.2)
            
            # Başlık satırını renklendir
            for (row, col), cell in table_bottom.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#e74c3c') # Kırmızı tonu

        # Grid'i sıkılaştır ve sayfayı listeye ekle
        plt.tight_layout(rect=[0, 0.03, 1, 0.95], w_pad=2.0, h_pad=3.0)
        pages.append(fig)
        
    return pages

def create_playlist_dna_catplot(df, features, title="Playlist Audio Features DNA"):
    """
    Tüm ses özelliklerini tek bir sayfada categorical plot (violin + strip) 
    olarak gösterir. Listenin karakterini bir bakışta özetler.
    """
    # 1. Veriyi 'Long-format'a çeviriyoruz (Seaborn catplot için şart)
    # Sütunlar: [Feature_Name, Value] şeklinde olacak
    df_melted = df[features].melt(var_name='Feature', value_name='Value')

    # 2. Plot oluşturma
    # kind="violin" hem boxplot hem de yoğunluk (dağılım) bilgisini verir.
    # inner="quart" çeyreklik dilimleri gösterir.
    g = sns.catplot(
        data=df_melted, 
        x='Feature', 
        y='Value', 
        kind='violin', 
        inner='quart', 
        split=True,
        hue='Feature',           # Add hue parameter
        palette='viridis',
        legend=False,            # Hide legend (since it's redundant)
        height=6, 
        aspect=2,
        alpha=0.3,                # Width/Height ratio (A4 Landscape compatibility)
        bw_method=0.2            # Distribution smoothness
    )

    # 3. Üzerine ham veriyi (noktaları) ekleyelim (stripplot)
    # Bu, kaç şarkının nerede toplandığını 'gerçek' veri olarak görmemizi sağlar.
    sns.stripplot(
        data=df_melted, 
        x='Feature', 
        y='Value', 
        color='black', 
        size=5, 
        alpha=0.5, 
        ax=g.ax
    )

    # 4. Estetik düzenlemeler
    g.ax.set_title(title, fontsize=16, pad=20)
    g.ax.set_ylim(0, 1) # Spotify metrikleri 0-1 arasındadır
    g.ax.set_ylabel("Intensity (0.0 - 1.0)")
    g.ax.set_xlabel("Musical Parameters")
    plt.xticks(rotation=15) # Yazıların birbirine girmemesi için
    
    plt.tight_layout()
    
    # catplot bir FacetGrid döner, figürüne erişip döndürüyoruz
    return g.fig

