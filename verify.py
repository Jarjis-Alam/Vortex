import hashlib

def verify_piece(
    piece_data,
    expected_hash
):

    actual_hash = hashlib.sha1(
        piece_data
    ).digest()

    return (
        actual_hash
        == expected_hash
    )