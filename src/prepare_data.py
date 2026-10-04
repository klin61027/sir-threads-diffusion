"""
Merge raw tracker CSVs and build the SIR-ready dataset.

Input : data/threads_*.csv   (raw files from threads_tracker.py)
Output: data/threads_MASTER_dataset.csv
        data/threads_SIR_ready.csv  (Post_Label, Time, Hours_Elapsed, Views_Cleaned)
"""
import glob
import os

import pandas as pd

DATA_DIR = "data"
MASTER_PATH = os.path.join(DATA_DIR, "threads_MASTER_dataset.csv")
SIR_READY_PATH = os.path.join(DATA_DIR, "threads_SIR_ready.csv")


def clean_views(x):
    """Turn strings like '1.2K', '3M' or '12,345' into numbers."""
    x = str(x).replace(",", "")
    if "K" in x:
        return float(x.replace("K", "")) * 1_000
    if "M" in x:
        return float(x.replace("M", "")) * 1_000_000
    return float(x)


def merge_to_master():
    """Merge all threads_*.csv files into one dataset."""
    all_files = glob.glob(os.path.join(DATA_DIR, "threads_*.csv"))
    print(f"Found {len(all_files)} files to merge:")

    df_list = []
    for filename in all_files:
        if "MASTER" in filename or "SIR_ready" in filename:
            continue
        try:
            df = pd.read_csv(filename)
            df["Time"] = pd.to_datetime(df["Time"])
            df_list.append(df)
            print(f" - Added: {os.path.basename(filename)} ({len(df)} rows)")
        except Exception as e:
            print(f" - Skipped {os.path.basename(filename)}: {e}")

    if not df_list:
        print("No files to merge.")
        return None

    master_df = pd.concat(df_list, ignore_index=True)
    master_df = master_df.sort_values(by="Time").drop_duplicates()
    master_df.to_csv(MASTER_PATH, index=False)
    print(f"\nSaved {len(master_df)} rows to: {MASTER_PATH}")
    return master_df


def build_sir_ready(master_df):
    """Clean view counts and compute hours elapsed for each post."""
    master_df["Views_Cleaned"] = master_df["Views"].apply(clean_views)
    master_df["Time"] = pd.to_datetime(master_df["Time"])
    master_df = master_df.sort_values(by=["Post_Label", "Time"])

    master_df["Hours_Elapsed"] = master_df.groupby("Post_Label")["Time"].transform(
        lambda x: (x - x.min()).dt.total_seconds() / 3600
    )

    final_df = master_df[["Post_Label", "Time", "Hours_Elapsed", "Views_Cleaned"]]
    final_df.to_csv(SIR_READY_PATH, index=False)
    print(f"SIR-ready file saved with {len(final_df)} rows to: {SIR_READY_PATH}")


def main():
    master_df = merge_to_master()
    if master_df is not None:
        build_sir_ready(master_df)


if __name__ == "__main__":
    main()
