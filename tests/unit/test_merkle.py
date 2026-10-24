from chainbreaker.ingest.merkle import MerkleTree


def test_merkle_proof_verifies():
    tree = MerkleTree([{"row_id": "1"}, {"row_id": "2"}, {"row_id": "3"}])
    assert tree.verify(tree.proof(1))
