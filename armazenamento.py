"""Salva o histórico de pesagens finalizadas e gera relatórios em texto."""

import json
import os
from datetime import datetime

from modelo import Ticket

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico.json")
PASTA_RELATORIOS = os.path.join(PASTA_DADOS, "relatorios")


def _garantir_pastas():
    os.makedirs(PASTA_DADOS, exist_ok=True)
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)


class GerenciadorHistorico:
    """Lê e grava os registros de pesagens já finalizadas."""

    def __init__(self):
        _garantir_pastas()
        self.registros = self._carregar()

    def _carregar(self) -> list:
        if not os.path.exists(ARQUIVO_HISTORICO):
            return []
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _salvar(self):
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(self.registros, f, ensure_ascii=False, indent=2)

    def registrar(self, ticket: Ticket) -> dict:
        registro = ticket.to_dict()
        registro["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.registros.insert(0, registro)
        self._salvar()
        return registro

    def listar(self) -> list:
        return self.registros


def gerar_relatorio(ticket: Ticket) -> str:
    """Gera um arquivo .txt com o detalhamento do ticket e retorna o caminho."""
    _garantir_pastas()
    agora = datetime.now()
    nome_arquivo = f"relatorio_{agora.strftime('%Y%m%d_%H%M%S')}.txt"
    caminho = os.path.join(PASTA_RELATORIOS, nome_arquivo)

    linhas = []
    linhas.append("BALANÇA DE MATERIAIS - RELATÓRIO DE PESAGEM")
    linhas.append(f"Data/hora: {agora.strftime('%d/%m/%Y %H:%M')}")
    linhas.append("-" * 44)
    for item in ticket.itens:
        linhas.append(
            f"{item.nome:<10} {item.peso:>7.2f} kg  x R$ {item.preco:>6.2f}  = R$ {item.valor:>8.2f}"
        )
    linhas.append("-" * 44)
    linhas.append(f"TOTAL: R$ {ticket.total:.2f}")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return caminho
