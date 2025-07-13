import secrets
import string

alphabet = string.ascii_letters + string.digits


def random_string(letters: int = 32) -> str:
    return ''.join(secrets.choice(alphabet) for i in range(letters))


def get_file_path(rand:str,ext: str) -> str:
    letter = rand[0]
    return f"{letter}/{rand}{ext}"
