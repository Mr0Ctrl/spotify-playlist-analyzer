import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import config

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