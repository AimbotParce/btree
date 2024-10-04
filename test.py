from btree import BTree
from btree.plots import plotBTree

if __name__ == "__main__":
    import argparse

    import pandas as pd

    parser = argparse.ArgumentParser(description="Construct a B-Tree")
    parser.add_argument("table", help="Path to the .csv file containing the table")
    parser.add_argument("--index", "-i", help="Which row to use to construct the index", default="id")
    parser.add_argument("--order", "-o", help="Order of the B-tree", type=int, default=1)
    parser.add_argument("--load", "-l", help="Load of the nodes", type=float, default=0.66)
    args = parser.parse_args()

    df = pd.read_csv(args.table)
    indexed_list = list((row[args.index], row) for _, row in df.iterrows())
    tree = BTree.build(indexed_list, order=args.order, load=args.load)

    img = plotBTree(tree)
    img.show()
