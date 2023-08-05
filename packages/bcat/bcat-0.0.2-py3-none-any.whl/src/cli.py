import pyarrow.parquet as pq
import sys


def get_df(src, rows):
    pf = pq.ParquetFile(src)
    return next(pf.iter_batches(batch_size=rows)).to_pandas()


def main():
    args = sys.argv

    if len(args) < 2:
        print('Source missing')

    src = args[1]

    try:
        rows = int(args[2]) if len(args) > 2 else 10
    except ValueError as e:
        print("ERROR: Invalid count parameter")
        raise e


    df = get_df(src, rows)

    for row in df.to_dict("records"):
      print(row)

