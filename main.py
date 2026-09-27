"""Balança de Materiais - ponto de entrada do programa."""

import tkinter as tk
from tela_login import TelaLogin
from interface import BalancaApp


def abrir_login():
    TelaLogin(ao_logar=abrir_app).mainloop()


def abrir_app(usuario_info):
    root = tk.Tk()
    BalancaApp(root, empresa=usuario_info["empresa"], ao_sair=abrir_login)
    root.mainloop()


if __name__ == "__main__":
    abrir_login()
