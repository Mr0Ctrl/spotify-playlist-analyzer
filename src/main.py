import sys
import data_loader, preprocessor, visualization, report_generator
from utils import file_system

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <csv_file>")
        return

    csv_path = sys.argv[1]
    
    try:
        # 1. Setup and Data Loading
        playlist_name = file_system.get_safe_filename(csv_path)
        out_dir = file_system.create_output_dir(playlist_name)
        df = data_loader.load_csv(csv_path)
        
        print(f"--- Generating Report for: {playlist_name} ---")

        # 2. Run Analysis
        averages = preprocessor.get_audio_averages(df)
        genres = preprocessor.get_genre_stats(df)

        # 3. Initialize Report
        report = report_generator.ReportGenerator(out_dir, playlist_name)
        
        # 4. Assemble PDF Pages
        print("Creating Cover Page...")
        report.add_title_page(playlist_name, len(df))

        print("Creating Audio Profile Page...")
        radar_fig = visualization.create_radar_chart(averages, "Audio Features Profile")
        report.add_visual_page(radar_fig)

        print("Creating Genre Cloud Page...")
        wc_fig = visualization.create_wordcloud(genres, "Genre Distribution Cloud")
        report.add_visual_page(wc_fig)

        # 5. Finalize
        report.close()

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()