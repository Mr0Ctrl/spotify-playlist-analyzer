import pandas as pd
import config
from itertools import product
import numpy as np


def get_audio_averages(df: pd.DataFrame) -> dict:
    """Calculates the averages of selected columns for the radar chart."""
    averages = {}
    for col in config.PERCENTAGE_COLUMNS:
        # Calculate the average of values between 0.0 and 1.0
        averages[col] = df[col].mean()
    return averages

def get_genre_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Separates genres and returns a DataFrame sorted by usage frequency."""
    genre_list = {}
    
    # Examine each row in the Artist Genres column
    for entry in df[config.Columns.ARTIST_GENRES].dropna():
        # Split genres separated by commas
        genres = [g.strip() for g in str(entry).split(',')]
        for g in genres:
            if g and g != "nan":
                genre_list[g] = genre_list.get(g, 0) + 1
                
    # Convert dictionary to DataFrame and sort
    genre_df = pd.DataFrame(list(genre_list.items()), columns=["Genre", "Count"])
    return genre_df.sort_values(by="Count", ascending=False)

def get_track_similarity_network(df: pd.DataFrame) -> tuple:
    """Calculates pairwise distances and builds a similarity network."""
    num_tracks = len(df)
    
    # 1. Create all possible pairs (Cartesian product)
    pairs = pd.DataFrame(product(df.index, df.index))
    
    # 2. Filter out identity (A to A) and duplicate pairs (A-B vs B-A)
    pairs = pairs[pairs[0] < pairs[1]].copy()
    
    # 3. Calculate distance for each pair based on PERCENTAGE_COLUMNS
    # Manhattan distance sum(|a - b|)
    dist_sum = 0
    for col in config.PERCENTAGE_COLUMNS:
        dist_sum += abs(df[col].iloc[pairs[0]].values - df[col].iloc[pairs[1]].values)
    
    pairs[config.GLOB_DIST_COL] = dist_sum
    
    # 4. Edge Filtering: Keep only the most similar tracks (shortest distance)
    pairs = pairs.sort_values(config.GLOB_DIST_COL)
    
    kept_edges = []
    edge_counts = np.zeros(num_tracks)
    
    for _, row in pairs.iterrows():
        node_a, node_b = int(row[0]), int(row[1])
        
        # Keep edges if at least one node hasn't reached the limit
        if edge_counts[node_a] < config.MAX_EDGES_PER_NODE or edge_counts[node_b] < config.MAX_EDGES_PER_NODE:
            kept_edges.append((node_a, node_b, row[config.GLOB_DIST_COL]))
            edge_counts[node_a] += 1
            edge_counts[node_b] += 1
            
    return list(range(num_tracks)), kept_edges