import os
import pandas as pd
from typing import Union, List, Optional
import config


def validate_csv_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validates that DataFrame contains all required columns."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing required columns: {missing_columns}")
        return False
    return True


def add_source_column(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Adds source filename column to DataFrame."""
    df = df.copy()
    df['source_file'] = source_name
    return df


def load_single_csv(csv_path: str, add_source: bool = True, 
                    source_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Loads and validates a single CSV file.
    
    Returns:
        DataFrame if successful, None if validation fails
    """
    required_columns = [config.Columns.TRACK_NAME, config.Columns.ARTIST_NAMES]
    
    try:
        df = pd.read_csv(csv_path)
        
        if not validate_csv_columns(df, required_columns):
            return None
        
        if add_source:
            if source_name is None:
                source_name = os.path.splitext(os.path.basename(csv_path))[0]
            df = add_source_column(df, source_name)
        
        print(f"Loaded: {csv_path} ({len(df)} tracks)")
        return df
        
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return None


def get_csv_files_from_directory(directory_path: str) -> List[str]:
    """Returns list of CSV files in a directory."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"Not a directory: {directory_path}")
    
    return [f for f in os.listdir(directory_path) if f.lower().endswith('.csv')]


def load_csv_files_from_directory(directory_path: str, add_source: bool = True) -> List[pd.DataFrame]:
    """Loads all valid CSV files from a directory."""
    csv_files = get_csv_files_from_directory(directory_path)
    
    if not csv_files:
        raise ValueError(f"No CSV files found in directory: {directory_path}")
    
    loaded_dfs = []
    for csv_file in csv_files:
        csv_path = os.path.join(directory_path, csv_file)
        source_name = os.path.splitext(csv_file)[0]
        df = load_single_csv(csv_path, add_source, source_name)
        if df is not None:
            loaded_dfs.append(df)
    
    if not loaded_dfs:
        raise ValueError(f"No valid CSV files found in directory: {directory_path}")
    
    return loaded_dfs


def combine_dataframes(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Combines multiple DataFrames into one with source tracking."""
    if not dfs:
        return pd.DataFrame()
    
    if len(dfs) == 1:
        return dfs[0]
    
    # Add index within each source file before combining
    for i, df in enumerate(dfs):
        # Add source file index (optional)
        if 'source_index' not in df.columns:
            df['source_index'] = range(len(df))
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Create a summary column showing source distribution
    source_counts = combined_df['source_file'].value_counts()
    source_summary = ", ".join([f"{src}({cnt})" for src, cnt in source_counts.items()])
    
    print(f"Combined {len(dfs)} CSV files into {len(combined_df)} total tracks")
    print(f"Source distribution: {source_summary}")
    
    return combined_df

def load_csv(file_path: Union[str, List[str]], add_source_column: bool = True, combine: bool = True) -> pd.DataFrame:
    """
    Loads CSV file(s) from given path(s).
    
    Args:
        file_path: Single path (file/dir) OR list of paths
        add_source_column: Whether to add source filename column
        combine: If True, combine all into single DataFrame
        
    Returns:
        Combined DataFrame (always returns DataFrame, never List)
    """
    # Convert single path to list for uniform processing
    if isinstance(file_path, str):
        paths = [file_path]
    else:
        paths = file_path
    
    all_dfs = []
    
    for path in paths:
        if not os.path.exists(path):
            print(f"Warning: Path not found, skipping: {path}")
            continue
        
        # Single file
        if os.path.isfile(path):
            if not path.lower().endswith('.csv'):
                print(f"Warning: Not a CSV file, skipping: {path}")
                continue
            
            df = load_single_csv(path, add_source_column)
            if df is not None:
                all_dfs.append(df)
        
        # Directory
        elif os.path.isdir(path):
            dfs = load_csv_files_from_directory(path, add_source_column)
            all_dfs.extend(dfs)
    
    if not all_dfs:
        raise ValueError("No valid CSV files found in any path")
    
    # Combine all DataFrames
    if combine or len(all_dfs) == 1:
        return combine_dataframes(all_dfs)
    else:
        # If combine=False but multiple files, still return combined (consistency)
        print("Warning: combine=False ignored for multiple sources, returning combined DataFrame")
        return combine_dataframes(all_dfs)