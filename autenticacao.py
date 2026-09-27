"""Gerencia contas de acesso (uma por empresa): cadastro, login e senha com hash."""

import json
import os
import hashlib
import secrets

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
ARQUIVO_USUARIOS = os.path.join(PASTA_DADOS, "usuarios.json")


def _garantir_pasta():
    os.makedirs(PASTA_DADOS, exist_ok=True)


def _hash_senha(senha: str, salt_hex: str = None) -> tuple[str, str]:
    """Gera (hash_hex, salt_hex). Se salt_hex não for passado, cria um novo salt."""
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 100_000)
    return hash_bytes.hex(), salt.hex()


class GerenciadorUsuarios:
    """Lê e grava as contas de acesso cadastradas (uma conta = uma empresa)."""

    def __init__(self):
        _garantir_pasta()
        self.usuarios = self._carregar()

    def _carregar(self) -> dict:
        if not os.path.exists(ARQUIVO_USUARIOS):
            return {}
        try:
            with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _salvar(self):
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(self.usuarios, f, ensure_ascii=False, indent=2)

    def usuario_existe(self, usuario: str) -> bool:
        return usuario.strip().lower() in self.usuarios

    def criar_usuario(self, empresa: str, usuario: str, senha: str):
        chave = usuario.strip().lower()
        if not empresa.strip() or not chave or not senha:
            raise ValueError("Preencha todos os campos.")
        if self.usuario_existe(chave):
            raise ValueError("Esse usuário já existe. Escolha outro nome de usuário.")
        if len(senha) < 4:
            raise ValueError("A senha precisa ter pelo menos 4 caracteres.")

        hash_hex, salt_hex = _hash_senha(senha)
        self.usuarios[chave] = {
            "empresa": empresa.strip(),
            "usuario": usuario.strip(),
            "hash": hash_hex,
            "salt": salt_hex,
        }
        self._salvar()

    def validar_login(self, usuario: str, senha: str) -> dict:
        """Retorna os dados do usuário se a senha for válida, ou None."""
        chave = usuario.strip().lower()
        registro = self.usuarios.get(chave)
        if not registro:
            return None
        hash_calculado, _ = _hash_senha(senha, registro["salt"])
        if hash_calculado == registro["hash"]:
            return registro
        return None
