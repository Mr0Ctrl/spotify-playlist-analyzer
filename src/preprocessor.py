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

def normalize_tempo_in_place(df: pd.DataFrame, min_reference: int = 50, max_reference: int = 200):
    """
    Tempo (BPM) değerini referans aralığa göre 0-1 arasına normalize eder.
    Referans tipli işlem yaparak DataFrame'i doğrudan günceller.
    
    Neden 50-200? 
    Genelde müzikal tempo bu aralıktadır. 50 altı veya 200 üstü değerler 
    uç değer (outlier) kabul edilerek sınırlara çekilir (clamping).
    """
    tempo_col = config.Columns.TEMPO
    
    if tempo_col not in df.columns:
        return

    # 1. Adım: Clamping (Sınırlandırma)
    # Değerleri min_reference ve max_reference arasına hapseder.
    # Örneğin: 220 BPM olan bir şarkı 200 kabul edilir, 40 olan 50 kabul edilir.
    df[tempo_col] = df[tempo_col].clip(lower=min_reference, upper=max_reference)
    
    # 2. Adım: Min-Max Scaling
    # Formül: (x - min) / (max - min)
    # Bu sayede 50 BPM -> 0.0, 200 BPM -> 1.0, 125 BPM -> 0.5 olur.
    df[tempo_col] = (df[tempo_col] - min_reference) / (max_reference - min_reference)
    
    print(f"Tempo normalized in-place using range [{min_reference}-{max_reference}].")


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