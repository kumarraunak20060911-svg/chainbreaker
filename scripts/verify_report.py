from chainbreaker.ingest.merkle import MerkleTree


def verify(rows):
    tree = MerkleTree(rows)
    return tree.root, tree.verify(tree.proof(0)) if rows else True


if __name__ == "__main__":
    root, valid = verify([{"row_id": "row-1", "event": "demo"}])
    print({"merkle_root": root, "first_row_verified": valid})
