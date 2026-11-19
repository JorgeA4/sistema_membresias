import bcrypt


def hashear_contraseña(contraseña: str) -> str:
    return bcrypt.hashpw(
        contraseña.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verificar_contraseña(contraseña: str, hash_contraseña: str) -> bool:
    if not isinstance(contraseña, str) or not isinstance(hash_contraseña, str):
        return False

    try:
        return bcrypt.checkpw(
            contraseña.encode("utf-8"),
            hash_contraseña.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False
