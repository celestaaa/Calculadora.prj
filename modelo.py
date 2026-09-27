"""Classes que representam um item pesado e o ticket da pesagem atual."""

from dataclasses import dataclass, asdict


@dataclass
class ItemPesagem:
    nome: str
    peso: float
    preco: float

    @property
    def valor(self) -> float:
        return self.peso * self.preco

    def to_dict(self) -> dict:
        d = asdict(self)
        d["valor"] = self.valor
        return d


class Ticket:
    """Agrupa os itens de uma pesagem em andamento."""

    def __init__(self):
        self.itens: list[ItemPesagem] = []

    def adicionar(self, nome: str, peso: float, preco: float) -> ItemPesagem:
        item = ItemPesagem(nome=nome, peso=peso, preco=preco)
        self.itens.append(item)
        return item

    def remover(self, indice: int):
        if 0 <= indice < len(self.itens):
            del self.itens[indice]

    def limpar(self):
        self.itens.clear()

    @property
    def total(self) -> float:
        return sum(item.valor for item in self.itens)

    def esta_vazio(self) -> bool:
        return len(self.itens) == 0

    def to_dict(self) -> dict:
        return {
            "itens": [item.to_dict() for item in self.itens],
            "total": self.total,
        }
