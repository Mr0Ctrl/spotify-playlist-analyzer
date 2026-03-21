import pandas as pd
import config

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