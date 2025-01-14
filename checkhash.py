import os
import hashlib


def calculate_sha256(file_path):
    """Calcula a hash SHA-256 de um arquivo."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (OSError, IOError) as e:
        return f"Erro ao calcular hash: {e}"


def print_file_hash(current_directory, item):
    """Exibe o nome do arquivo e o hash correspondente."""
    item_path = os.path.join(current_directory, item)
    if os.path.isfile(item_path):  # Verifica se é um arquivo
        sha256_hash = calculate_sha256(item_path)
        print(f"Arquivo: {item} - SHA-256: {sha256_hash}")


def main():
    """Percorre o diretório atual e calcula a hash dos arquivos."""
    current_directory = os.getcwd()

    for item in os.listdir(current_directory):
        print_file_hash(current_directory, item)


if __name__ == "__main__":
    main()
