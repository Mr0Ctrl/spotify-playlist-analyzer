import pandas as pd
import os

def load_csv(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV bulunamadı: {file_path}")
    
    df = pd.read_csv(file_path)

    if "Track Name" not in df.columns:
        raise ValueError("Bu dosya geçerli bir Spotify Exportify CSV'si değil.")
    
    return df