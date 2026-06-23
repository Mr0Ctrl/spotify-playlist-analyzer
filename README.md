# Spotify Playlist Analyzer

Analyze Spotify playlists exported via Exportify. Generates PDF reports with statistics, audio features, genre distribution, and similarity networks.

## Requirements

- Python 3.12
- pip

## Installation

```bash
# Clone repository
git clone <repository-url>
cd spotify-playlist-analyzer

# Create virtual environment
python3 -m venv venv

source venv/bin/activate  # Linux/Ubuntu
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single playlist
```bash
python src/main.py <path_to_csv>
```

### Multiple playlists
```bash
python src/main.py playlist1.csv playlist2.csv ...
```

### Bulk processing
```bash
python scripts/bulk_process.py <directory>  # can be broken
```

### Export playlist data
1. Go to https://watsonbox.github.io/exportify/
2. Login with Spotify
3. Select playlist and enable all optional data
4. Export as CSV

## Output

Results are saved in `out/` folder with timestamp:
- `analysis_report.pdf`     - Complete report with visualizations
- `playlist_stats.csv`      - Summary statistics
- `track_data_processed.csv` - Enriched track data

## Project Structure

```
spotify-playlist-analyzer/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── data_loader.py       # CSV loading
│   ├── preprocessor.py      # Data processing
│   ├── visualization.py     # Plot generation
│   ├── report_generator.py  # PDF creation
│   └── utils/               # Utilities
├── scripts/
│   └── bulk_process.py      # Batch processing
├── requirements.txt
└── README.md
```

## License

MIT License