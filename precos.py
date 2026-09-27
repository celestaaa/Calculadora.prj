"""Gerencia os preços por kg dos materiais, permitindo edição pela interface.

Os preços começam com os valores padrão (materiais.MATERIAIS) e, se o usuário
já tiver salvado alterações antes, são sobrescritos pelo que estiver em
dados/precos.json.
"""

import json
import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
ARQUIVO_PRECOS = os.path.join(PASTA_DADOS, "precos.json")


def _garantir_pasta():
    os.makedirs(PASTA_DADOS, exist_ok=True)


class GerenciadorPrecos:
    def __init__(self, materiais_padrao: list):
        # cópia própria, pra não mexer na lista padrão importada
        self.materiais = [dict(m) for m in materiais_padrao]
        self._aplicar_precos_salvos()

    def _aplicar_precos_salvos(self):
        _garantir_pasta()
        if not os.path.exists(ARQUIVO_PRECOS):
            return
        try:
            with open(ARQUIVO_PRECOS, "r", encoding="utf-8") as f:
                precos_salvos = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        for material in self.materiais:
            if material["nome"] in precos_salvos:
                material["preco"] = precos_salvos[material["nome"]]

    def listar(self) -> list:
        return self.materiais

    def atualizar_precos(self, novos_precos: dict):
        """novos_precos: {"Cobre": 26.5, "Metal": 14.0, ...}"""
        for material in self.materiais:
            if material["nome"] in novos_precos:
                material["preco"] = novos_precos[material["nome"]]

        _garantir_pasta()
        mapa = {m["nome"]: m["preco"] for m in self.materiais}
        with open(ARQUIVO_PRECOS, "w", encoding="utf-8") as f:
            json.dump(mapa, f, ensure_ascii=False, indent=2)
