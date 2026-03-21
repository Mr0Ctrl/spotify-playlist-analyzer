import sys
import data_loader, preprocessor, visualization, report_generator
from utils import file_system
import config

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
        nodes, edges = preprocessor.get_track_similarity_network(df)

        # 3. Initialize Report
        report = report_generator.ReportGenerator(out_dir, playlist_name)
        
        # 4. Assemble PDF Pages

        print("Creating Cover Page...")
        report.add_title_page(playlist_name, len(df))

        index_pages = visualization.create_track_index_page(df, "Track Inventory")
        for p in index_pages: 
            report.add_visual_page(p)

        print("Creating Audio Profile Page...")
        radar_fig = visualization.create_radar_chart(averages, "Audio Features Profile")
        report.add_visual_page(radar_fig)

        print("Creating Genre Cloud Page...")
        wc_fig = visualization.create_wordcloud(genres, "Genre Distribution Cloud")
        report.add_visual_page(wc_fig)

        print("Creating Similarity Network Page...")
        network_fig = visualization.create_network_graph(nodes, edges, "Track Similarity Network")
        report.add_visual_page(network_fig)

        # --- GENERAL DISTRIBUTION PLOTS ---
        print("Creating Distribution Analysis...")

        # 2.1 Popularity
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.POPULARITY, "Popularity Distribution", 
            config.DataColors.POPULARITY, bins=20, x_label="Popularity (0-100)"
        ))

        # 2.2 Duration (Convert to minutes first, then plot)
        df_temp = df.copy()
        df_temp[config.Columns.DURATION] = df_temp[config.Columns.DURATION] / 60000
        report.add_visual_page(visualization.create_distribution_plot(
            df_temp, config.Columns.DURATION, "Track Duration Distribution", 
            config.DataColors.DURATION, bins=15, unit="min"
        ))

        # 2.3 Tempo (BPM)
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.TEMPO, "Tempo Distribution", 
            config.DataColors.TEMPO, bins=20, unit="BPM"
        ))

        # 2.4 Loudness (dB)
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.LOUDNESS, "Loudness Distribution", 
            config.DataColors.LOUDNESS, bins=15, unit="dB"
        ))

        # 2.5 Key (Notes)
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.KEY, "Key Distribution (0=C, 1=C#, etc.)", 
            config.DataColors.KEY, bins=12
        ))

        # 2.6 Mode (Major/Minor)
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.MODE, "Mode Distribution (1=Major, 0=Minor)", 
            config.DataColors.MODE, bins=2
        ))

        # 2.7 Time Signature
        report.add_visual_page(visualization.create_distribution_plot(
            df, config.Columns.TIME_SIGNATURE, "Time Signature Distribution", 
            config.DataColors.TIME_SIGNATURE, bins=5
        ))

        # 2.8 Audio Features (Percentage Data: Danceability, Energy, etc.)
        for col in config.PERCENTAGE_COLUMNS:
            color = getattr(config.DataColors, col.upper().replace(" ", "_"), "#333333")
            report.add_visual_page(visualization.create_distribution_plot(
                df, col, f"{col} Amount Distribution", 
                color, bins=20, x_label=f"{col} (0.0 - 1.0)"
            ))
        
        # Correlation Grid (should be outside the loop)
        print("Creating Correlation Grid...")
        corr_pages = visualization.create_correlation_grid(df, config.PERCENTAGE_COLUMNS)
        for p in corr_pages: 
            report.add_visual_page(p)

        # Top Energetic Tracks
        print("Creating Top Tracks Analysis...")
        top_energy = visualization.create_ranking_plot(df, config.Columns.ENERGY, "Top 15 Most Energetic Tracks", config.DataColors.ENERGY)
        report.add_visual_page(top_energy)
        
        # Additional rankings (optional)
        top_dance = visualization.create_ranking_plot(df, config.Columns.DANCEABILITY, "Top 15 Most Danceable Tracks", config.DataColors.DANCEABILITY)
        report.add_visual_page(top_dance)
        
        top_valence = visualization.create_ranking_plot(df, config.Columns.VALENCE, "Top 15 Most Positive Tracks", config.DataColors.VALENCE)
        report.add_visual_page(top_valence)

        # 5. Finalize
        report.close()
        
        print(f"\nReport successfully generated in: {out_dir}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()