import sys
import os
import matplotlib.pyplot as plt
import config, data_loader, preprocessor, visualization
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
        
        print(f"--- Visualizing {playlist_name} ---")

        # 2. Analysis
        averages = preprocessor.get_audio_averages(df)
        genres = preprocessor.get_genre_stats(df)

        # 3. Visualization (Generate figures)
        radar_fig = visualization.create_radar_chart(averages, "Playlist Audio Profile")
        wc_fig = visualization.create_wordcloud(genres, "Top Genres Cloud")

        # 4. Temporary Save (as PNG) - For Testing Purposes
        radar_fig.savefig(os.path.join(out_dir, "radar_profile.png"))
        wc_fig.savefig(os.path.join(out_dir, "genres_cloud.png"))
        
        # Clean up memory (Very important!)
        plt.close('all')

        print(f"Graphs created and saved as PNG in '{out_dir}' folder.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()