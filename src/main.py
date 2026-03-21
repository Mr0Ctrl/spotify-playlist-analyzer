import sys
import data_loader, preprocessor, visualization, report_generator
from utils import file_system
import config

def main():
    if len(sys.argv) < 2:
            print("Usage: python -m src.main <csv_file1> [csv_file2] ...")
            print("       python -m src.main <directory>")
            return

    # Support multiple CSV paths
    csv_paths = sys.argv[1:]
    
    try:
        # 1. Setup and Data Loading
        playlist_name = file_system.get_safe_filename(csv_paths)
        out_dir = file_system.create_output_dir(playlist_name)
        df = data_loader.load_csv(csv_paths)
        preprocessor.normalize_tempo_in_place(df)

        print(f"--- Generating Report for: {playlist_name} ---")

        # 2. Run Analysis
        averages = preprocessor.get_audio_averages(df)
        genres = preprocessor.get_genre_stats(df)
        nodes, edges = preprocessor.get_track_similarity_network(df)

        # 3. Initialize Report
        report = report_generator.ReportGenerator(out_dir, playlist_name)
        
        # 4. Assemble PDF Pages
        #region pages
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

        # --- PLAYLIST DNA (CATPLOT) ---
        print("Generating Playlist DNA (CatPlot)...")

        # config.PERCENTAGE_COLUMNS içindeki 8 parametreyi kullanır
        dna_fig = visualization.create_playlist_dna_catplot(
            df, 
            config.PERCENTAGE_COLUMNS, 
            title=f"Audio DNA: {playlist_name}"
        )
        report.add_visual_page(dna_fig)

        # Create correlation pages
        triplets = [
            ('Acousticness', 'Energy', 'Danceability'),
            ('Energy', 'Valence', 'Tempo'),
            ('Danceability', 'Energy', 'Valence'),
            ('Speechiness', 'Instrumentalness', 'Energy'),
            ('Acousticness', 'Loudness', 'Energy'),
            ('Tempo', 'Danceability', 'Energy'),
            ('Energy', 'Loudness', 'Valence'),
            ('Valence', 'Danceability', 'Energy'),
        ]

        corr_pages = visualization.create_correlation_grid(df, triplets, charts_per_page=8)
        for page in corr_pages:
            report.add_visual_page(page)

        # --- 2. AKIŞ ANALİZİ ---
        # window_size şarkı sayısına göre dinamik olabilir (örn: toplamın %5'i)
        flow_figs = visualization.create_flow_analysis_grid(df, config.PERCENTAGE_COLUMNS, window_size=7)
        for fig in flow_figs:
            report.add_visual_page(fig)

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