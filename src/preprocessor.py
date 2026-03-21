import pandas as pd
import config
from itertools import product
import numpy as np
from sklearn.neighbors import NearestNeighbors


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
    """Connects tracks that are similar beyond a threshold, not just top-k."""

    
    # Extract feature matrix
    feature_cols = config.PERCENTAGE_COLUMNS
    feature_matrix = df[feature_cols].values
    
    num_tracks = len(df)
    
    # Find k+1 neighbors (including self)
    nbrs = NearestNeighbors(n_neighbors=config.MAX_EDGES_PER_NODE + 1, metric='euclidean')
    nbrs.fit(feature_matrix)
    distances, indices = nbrs.kneighbors(feature_matrix)
    
    kept_edges = []
    edge_counts = np.zeros(num_tracks)
    
    for i in range(num_tracks):
        # Skip the first neighbor (which is the track itself)
        for j_idx in range(1, len(indices[i])):
            j = indices[i][j_idx]
            dist = distances[i][j_idx]
            
            # Only connect if similarity is above threshold (distance below threshold)
            if dist < config.SIMILARITY_THRESHOLD:
                if i < j and edge_counts[i] < config.MAX_EDGES_PER_NODE and edge_counts[j] < config.MAX_EDGES_PER_NODE:
                    kept_edges.append((i, j, dist))
                    edge_counts[i] += 1
                    edge_counts[j] += 1
    
    return list(range(num_tracks)), kept_edges