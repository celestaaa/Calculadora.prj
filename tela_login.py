"""Janela inicial: login e criação de conta da empresa."""

import tkinter as tk
from tkinter import ttk

from materiais import TEMA
from autenticacao import GerenciadorUsuarios


class TelaLogin(tk.Tk):
    def __init__(self, ao_logar):
        """ao_logar: função chamada com os dados do usuário quando o login der certo."""
        super().__init__()
        self.ao_logar = ao_logar
        self.usuarios = GerenciadorUsuarios()
        self.modo = "login"  # ou "cadastro"

        self.title("Balança de Materiais — Acesso")
        self.configure(bg=TEMA["fundo"])
        self.geometry("380x460")
        self.resizable(False, False)

        self._montar_estilo()
        self._montar_layout()

    def _montar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=TEMA["fundo"])
        style.configure("TLabel", background=TEMA["fundo"], foreground=TEMA["texto"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=TEMA["fundo"], foreground=TEMA["muted"], font=("Segoe UI", 9))
        style.configure("Titulo.TLabel", background=TEMA["fundo"], foreground=TEMA["texto"], font=("Segoe UI", 16, "bold"))
        style.configure("Erro.TLabel", background=TEMA["fundo"], foreground="#c96b5c", font=("Segoe UI", 9))

    def _montar_layout(self):
        self.container = ttk.Frame(self, padding=28)
        self.container.pack(fill="both", expand=True)
        self._renderizar()

    def _limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _campo(self, label_texto, mostrar=None):
        ttk.Label(self.container, text=label_texto, style="Muted.TLabel").pack(anchor="w", pady=(10, 4))
        entrada = tk.Entry(
            self.container, font=("Segoe UI", 11), bg=TEMA["painel"], fg=TEMA["texto"],
            insertbackground=TEMA["texto"], relief="flat", show=mostrar or ""
        )
        entrada.pack(fill="x", ipady=7)
        return entrada

    # ---------- Modo login ----------
    def _renderizar(self):
        self._limpar_container()
        if self.modo == "login":
            self._renderizar_login()
        else:
            self._renderizar_cadastro()

    def _renderizar_login(self):
        ttk.Label(self.container, text="Balança de Materiais", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self.container, text="Entre com a conta da sua empresa.", style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        self.entry_usuario = self._campo("Usuário")
        self.entry_senha = self._campo("Senha", mostrar="*")

        self.lbl_erro = ttk.Label(self.container, text="", style="Erro.TLabel")
        self.lbl_erro.pack(anchor="w", pady=(8, 0))

        tk.Button(
            self.container, text="Entrar", font=("Segoe UI", 11, "bold"),
            bg=TEMA["cobre"], fg="#1a1300", relief="flat", padx=10, pady=10,
            command=self._tentar_login
        ).pack(fill="x", pady=(16, 6))

        tk.Button(
            self.container, text="Criar conta da empresa", font=("Segoe UI", 9),
            bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=6, pady=6,
            command=self._ir_para_cadastro
        ).pack(fill="x")

        self.entry_usuario.focus_set()
        self.bind("<Return>", lambda e: self._tentar_login())

    def _tentar_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        dados = self.usuarios.validar_login(usuario, senha)
        if dados:
            self.destroy()
            self.ao_logar(dados)
        else:
            self.lbl_erro.configure(text="Usuário ou senha inválidos.")

    def _ir_para_cadastro(self):
        self.modo = "cadastro"
        self.unbind("<Return>")
        self._renderizar()

    # ---------- Modo cadastro ----------
    def _renderizar_cadastro(self):
        ttk.Label(self.container, text="Criar conta", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self.container, text="Cadastre o acesso da sua empresa.", style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        self.entry_empresa = self._campo("Nome da empresa")
        self.entry_novo_usuario = self._campo("Usuário")
        self.entry_nova_senha = self._campo("Senha", mostrar="*")
        self.entry_confirmar_senha = self._campo("Confirmar senha", mostrar="*")

        self.lbl_erro = ttk.Label(self.container, text="", style="Erro.TLabel")
        self.lbl_erro.pack(anchor="w", pady=(8, 0))

        tk.Button(
            self.container, text="Criar conta", font=("Segoe UI", 11, "bold"),
            bg=TEMA["total"], fg="#122016", relief="flat", padx=10, pady=10,
            command=self._tentar_cadastrar
        ).pack(fill="x", pady=(16, 6))

        tk.Button(
            self.container, text="Já tenho conta — Entrar", font=("Segoe UI", 9),
            bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=6, pady=6,
            command=self._ir_para_login
        ).pack(fill="x")

        self.bind("<Return>", lambda e: self._tentar_cadastrar())

    def _ir_para_login(self):
        self.modo = "login"
        self.unbind("<Return>")
        self._renderizar()

    def _tentar_cadastrar(self):
        empresa = self.entry_empresa.get()
        usuario = self.entry_novo_usuario.get()
        senha = self.entry_nova_senha.get()
        confirmar = self.entry_confirmar_senha.get()

        if senha != confirmar:
            self.lbl_erro.configure(text="As senhas não coincidem.")
            return

        try:
            self.usuarios.criar_usuario(empresa, usuario, senha)
        except ValueError as e:
            self.lbl_erro.configure(text=str(e))
            return

        self._ir_para_login()
        self.lbl_erro.configure(text="Conta criada! Faça login para continuar.")
        self.lbl_erro.configure(foreground=TEMA["total"])
