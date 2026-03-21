import sys
import config, data_loader, preprocessor
from utils import file_system

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <csv_file>")
        return

    csv_path = sys.argv[1]
    
    try:
        # 1. Preparation and Loading
        playlist_name = file_system.get_safe_filename(csv_path)
        out_dir = file_system.create_output_dir(playlist_name)
        df = data_loader.load_csv(csv_path)
        
        print(f"--- Analyzing {playlist_name} ---")

        # 2. Analysis: Average Values
        averages = preprocessor.get_audio_averages(df)
        print("\n[Musical Profile (Averages)]")
        for key, val in averages.items():
            print(f"- {key}: {val:.2f}")

        # 3. Analysis: Genre Statistics
        genres = preprocessor.get_genre_stats(df)
        print("\n[Top 5 Genres]")
        print(genres.head(5).to_string(index=False))

        print(f"\nAnalysis completed. Results will be prepared in '{out_dir}' folder.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()