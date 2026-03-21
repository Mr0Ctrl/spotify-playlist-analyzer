import sys
import config, data_loader
from utils import file_system

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <csv_file>")
        return

    csv_path = sys.argv[1]
    
    try:
        # 1. Preparation
        playlist_name = file_system.get_safe_filename(csv_path)
        print(f"Processing: {playlist_name}")
        
        # 2. Data Loading
        df = data_loader.load_csv(csv_path)
        print(f"Successfully loaded: {len(df)} songs found.")
        
        # 3. Output Directory Creation
        out_dir = file_system.create_output_dir(playlist_name)
        print(f"Results will be saved to: {out_dir}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()