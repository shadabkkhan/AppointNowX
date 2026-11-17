import bcrypt

def hash_password(text_password: str) -> str:
    encoded = text_password.encode("utf-8")

    if not text_password:
        raise ValueError("password cannot be empty or null")

    if len(encoded) > 72:
        raise ValueError("encoded value cant be greated then 72 bytes.")

    generate_salt = bcrypt.gensalt(rounds=12)

    blend = bcrypt.hashpw(encoded, generate_salt)

    return blend.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    encode_plaintext = plain_password.encode("utf-8")
    encode_hashed_password = hashed_password.encode("utf-8")

    if len(encode_hashed_password) > 72:
        return False

    try:
        compare_hash_with_plaintext = bcrypt.checkpw(
            encode_plaintext,
            encode_hashed_password
            )
        return compare_hash_with_plaintext
    except ValueError:
        return False

    
