import pandas as pd
import config
from itertools import product
import numpy as np
from sklearn.neighbors import NearestNeighbors

from datetime import timedelta

def get_track_duration_summary(df):
    """Track sürelerinin özetini döndürür."""
    total_ms = int(df[config.Columns.DURATION].sum())
    total_duration = timedelta(milliseconds=total_ms)
    
    return {
        'total_tracks': len(df),
        'total_duration': total_duration,
        'total_ms': total_ms
    }

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

def get_track_similarity_network(df: pd.DataFrame, feature_weights: dict = None) -> tuple:
    """Connects tracks with weighted feature importance."""
    
    # Extract feature matrix
    feature_cols = config.PERCENTAGE_COLUMNS
    feature_matrix = df[feature_cols].values.copy()
    
    # Apply feature weights if provided
    if config.feature_weights:
        for i, col in enumerate(feature_cols):
            weight = config.feature_weights.get(col, 1.0)
            feature_matrix[:, i] = feature_matrix[:, i] * weight
    
    num_tracks = len(df)
    
    nbrs = NearestNeighbors(n_neighbors=config.MAX_EDGES_PER_NODE + 1, metric='euclidean')
    nbrs.fit(feature_matrix)
    distances, indices = nbrs.kneighbors(feature_matrix)
    
    kept_edges = []
    edge_counts = np.zeros(num_tracks)
    
    for i in range(num_tracks):
        for j_idx in range(1, len(indices[i])):
            j = indices[i][j_idx]
            dist = distances[i][j_idx]
            
            if dist < config.SIMILARITY_THRESHOLD:
                if i < j and edge_counts[i] < config.MAX_EDGES_PER_NODE and edge_counts[j] < config.MAX_EDGES_PER_NODE:
                    kept_edges.append((i, j, dist))
                    edge_counts[i] += 1
                    edge_counts[j] += 1
    
    return list(range(num_tracks)), kept_edges

def normalize_column_in_place(df: pd.DataFrame, column_name: str, min_reference: float = None, max_reference: float = None, 
                              use_data_bounds: bool = False, clip_values: bool = True):
    # Sütunun varlığını kontrol et
    if column_name not in df.columns:
        print(f"Warning: Column '{column_name}' not found in DataFrame.")
        return False
    
    # Referans değerlerini belirle
    if use_data_bounds:
        min_reference = df[column_name].min()
        max_reference = df[column_name].max()
        clip_values = False  # Veri sınırları kullanılıyorsa clamping'e gerek yok
    elif min_reference is None or max_reference is None:
        print(f"Error: Both min_reference and max_reference must be specified when use_data_bounds=False.")
        return False
    
    # Aynı değer kontrolü (division by zero)
    if min_reference == max_reference:
        print(f"Warning: min_reference ({min_reference}) equals max_reference ({max_reference}). Setting column to 0.5.")
        df[column_name] = 0.5
        return True
    
    # 1. Adım: Clamping (Sınırlandırma) - opsiyonel
    if clip_values:
        df[column_name] = df[column_name].clip(lower=min_reference, upper=max_reference)
    
    # 2. Adım: Min-Max Scaling
    # Formül: (x - min) / (max - min)
    df[column_name] = (df[column_name] - min_reference) / (max_reference - min_reference)
    
    print(f"Column '{column_name}' normalized in-place using range [{min_reference:.2f}-{max_reference:.2f}].")
    return True


def detect_outliers_statistical(df):
    """
    Yüzde vermek yerine, listenin ortalama ruh haline 
    istatistiksel olarak 'çok uzak' olanları bulur.
    """
    features = config.PERCENTAGE_COLUMNS
    # Listenin 'ortalama' profili (Centroid)
    centroid = df[features].mean()
    
    # Her şarkının bu merkeze olan Öklid uzaklığı
    distances = np.linalg.norm(df[features] - centroid, axis=1)
    df['distance_from_center'] = distances
    
    # Eşik Değer: Ortalama Uzaklık + 2 * Standart Sapma
    # (İstatistikte verinin %95'i bu sınırın içindedir, dışındakiler 'gerçek' outlierdır)
    threshold = distances.mean() + (2 * distances.std())
    
    outliers = df[df['distance_from_center'] > threshold].sort_values('distance_from_center', ascending=False)
    return outliers