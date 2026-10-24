from chainbreaker.ingest.merkle import MerkleProof, MerkleTree


def verify_row(tree: MerkleTree, proof: MerkleProof) -> bool:
    return tree.verify(proof)
