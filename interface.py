"""Interface Tkinter da Balança de Materiais, organizada em abas."""

import tkinter as tk
from tkinter import ttk, messagebox

from materiais import MATERIAIS, TEMA
from modelo import Ticket
from armazenamento import GerenciadorHistorico, gerar_relatorio


class BalancaApp:
    def __init__(self, root: tk.Tk, empresa: str = "", ao_sair=None):
        self.root = root
        self.empresa = empresa
        self.ao_sair = ao_sair
        self.root.title(f"Balança de Materiais — {empresa}" if empresa else "Balança de Materiais")
        self.root.configure(bg=TEMA["fundo"])
        self.root.geometry("880x560")
        self.root.minsize(760, 480)

        self.ticket = Ticket()
        self.historico = GerenciadorHistorico()
        self.material_selecionado = None

        self._montar_estilo()
        self._montar_abas()

    # ---------- Estilo ----------
    def _montar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=TEMA["fundo"])
        style.configure("Painel.TFrame", background=TEMA["painel"])
        style.configure("TLabel", background=TEMA["fundo"], foreground=TEMA["texto"], font=("Segoe UI", 10))
        style.configure("Painel.TLabel", background=TEMA["painel"], foreground=TEMA["texto"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=TEMA["fundo"], foreground=TEMA["muted"], font=("Segoe UI", 9))
        style.configure("Titulo.TLabel", background=TEMA["fundo"], foreground=TEMA["texto"], font=("Segoe UI", 16, "bold"))

    # ---------- Estrutura em abas ----------
    def _montar_abas(self):
        cabecalho = ttk.Frame(self.root, padding=(20, 16, 20, 0))
        cabecalho.pack(fill="x")

        linha_topo = ttk.Frame(cabecalho)
        linha_topo.pack(fill="x")
        titulo_box = ttk.Frame(linha_topo)
        titulo_box.pack(side="left")
        ttk.Label(titulo_box, text="Balança de Materiais", style="Titulo.TLabel").pack(anchor="w")
        subtitulo = f"Empresa: {self.empresa}" if self.empresa else "Pese, calcule e acompanhe o histórico das suas pesagens."
        ttk.Label(titulo_box, text=subtitulo, style="Muted.TLabel").pack(anchor="w", pady=(2, 10))

        if self.ao_sair:
            tk.Button(
                linha_topo, text="Sair", font=("Segoe UI", 9),
                bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=10, pady=6,
                command=self._sair
            ).pack(side="right")

        self.abas_nomes = ["Pesagem", "Histórico"]
        self.aba_atual = 0
        self.animando = False

        barra_abas = tk.Frame(self.root, bg=TEMA["fundo"])
        barra_abas.pack(fill="x", padx=20, pady=(4, 0))

        self.botoes_aba = []
        for i, nome in enumerate(self.abas_nomes):
            btn = tk.Button(
                barra_abas, text=nome, font=("Segoe UI", 10),
                bg=TEMA["fundo"], fg=TEMA["texto"] if i == 0 else TEMA["muted"],
                activebackground=TEMA["fundo"], activeforeground=TEMA["texto"],
                relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
                command=lambda idx=i: self._trocar_aba(idx),
            )
            btn.pack(side="left")
            self.botoes_aba.append(btn)

        self.linha_indicador = tk.Frame(barra_abas, bg=TEMA["cobre"], height=2)
        self.linha_indicador.place(x=0, y=34, width=90, height=2)

        # Área de conteúdo: dois painéis sobrepostos, deslizam ao trocar de aba
        self.area_conteudo = tk.Frame(self.root, bg=TEMA["fundo"])
        self.area_conteudo.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        aba_pesagem = ttk.Frame(self.area_conteudo, style="TFrame")
        aba_historico = ttk.Frame(self.area_conteudo, style="TFrame")
        self.paineis_aba = [aba_pesagem, aba_historico]
        aba_pesagem.place(relx=0, rely=0, relwidth=1, relheight=1)
        aba_historico.place(relx=1, rely=0, relwidth=1, relheight=1)

        self._montar_aba_pesagem(aba_pesagem)
        self._montar_aba_historico(aba_historico)

        # Posiciona a linha indicadora certinho embaixo do 1º botão assim que a janela desenhar
        self.root.after(50, self._posicionar_indicador_inicial)

    def _posicionar_indicador_inicial(self):
        btn = self.botoes_aba[self.aba_atual]
        self.linha_indicador.place(x=btn.winfo_x(), y=btn.winfo_y() + btn.winfo_height() - 2,
                                    width=btn.winfo_width(), height=2)

    def _trocar_aba(self, indice):
        if indice == self.aba_atual or self.animando:
            return

        direcao = 1 if indice > self.aba_atual else -1
        origem = self.paineis_aba[self.aba_atual]
        destino = self.paineis_aba[indice]

        destino.place(relx=direcao, rely=0, relwidth=1, relheight=1)
        destino.lift()

        btn_novo = self.botoes_aba[indice]
        btn_antigo = self.botoes_aba[self.aba_atual]
        btn_novo.configure(fg=TEMA["texto"])
        btn_antigo.configure(fg=TEMA["muted"])

        x_origem = self.botoes_aba[self.aba_atual].winfo_x()
        largura_origem = self.botoes_aba[self.aba_atual].winfo_width()
        x_destino = btn_novo.winfo_x()
        largura_destino = btn_novo.winfo_width()
        y_indicador = btn_novo.winfo_y() + btn_novo.winfo_height() - 2

        self.aba_atual = indice
        self.animando = True
        self._animar_transicao(
            origem, destino, direcao,
            x_origem, largura_origem, x_destino, largura_destino, y_indicador,
            passo=0, total_passos=14
        )

    def _animar_transicao(self, origem, destino, direcao, x_a, larg_a, x_b, larg_b, y_indicador, passo, total_passos):
        t = passo / total_passos
        t_suave = 1 - (1 - t) ** 3  # ease-out: começa rápido, termina suave

        origem.place(relx=-direcao * t_suave, rely=0, relwidth=1, relheight=1)
        destino.place(relx=direcao * (1 - t_suave), rely=0, relwidth=1, relheight=1)

        x_atual = x_a + (x_b - x_a) * t_suave
        largura_atual = larg_a + (larg_b - larg_a) * t_suave
        self.linha_indicador.place(x=x_atual, y=y_indicador, width=largura_atual, height=2)

        if passo >= total_passos:
            self.animando = False
            return

        self.root.after(
            12, lambda: self._animar_transicao(
                origem, destino, direcao, x_a, larg_a, x_b, larg_b, y_indicador, passo + 1, total_passos
            )
        )

    # ---------- Aba Pesagem ----------
    def _montar_aba_pesagem(self, pai):
        pai.columnconfigure(0, weight=1)
        pai.columnconfigure(1, weight=1)
        pai.columnconfigure(2, weight=1)
        pai.rowconfigure(0, weight=1)

        self._montar_lista_materiais(pai)
        self._montar_painel_visor(pai)
        self._montar_ticket(pai)

    def _montar_lista_materiais(self, pai):
        frame = ttk.Frame(pai, padding=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=10)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Materiais", style="Muted.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Área rolável: um Canvas com uma Frame dentro, mais a Scrollbar
        canvas = tk.Canvas(frame, bg=TEMA["fundo"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        area_interna = tk.Frame(canvas, bg=TEMA["fundo"])

        area_interna.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        janela_id = canvas.create_window((0, 0), window=area_interna, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(janela_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        def _rolar_com_mouse(event):
            # Windows/Mac usam event.delta; Linux usa Button-4/5
            delta = -1 * (event.delta // 120) if event.delta else (-1 if event.num == 4 else 1)
            canvas.yview_scroll(delta, "units")

        for alvo in (canvas, area_interna):
            alvo.bind("<MouseWheel>", _rolar_com_mouse)   # Windows / macOS
            alvo.bind("<Button-4>", _rolar_com_mouse)      # Linux (scroll up)
            alvo.bind("<Button-5>", _rolar_com_mouse)      # Linux (scroll down)

        self.botoes_material = {}
        for m in MATERIAIS:
            btn = tk.Button(
                area_interna, text=f"{m['nome']}\nR$ {m['preco']:.2f}/kg",
                font=("Segoe UI", 10), bg=TEMA["painel"], fg=TEMA["texto"],
                activebackground=TEMA["painel_ativo"], activeforeground=TEMA["texto"],
                relief="flat", bd=0, justify="left", anchor="w", padx=12, pady=10,
                command=lambda mat=m: self.selecionar_material(mat),
            )
            btn.pack(fill="x", pady=3)
            btn.bind("<MouseWheel>", _rolar_com_mouse)
            btn.bind("<Button-4>", _rolar_com_mouse)
            btn.bind("<Button-5>", _rolar_com_mouse)
            self.botoes_material[m["nome"]] = btn

    def _montar_painel_visor(self, pai):
        frame = ttk.Frame(pai, style="Painel.TFrame", padding=20)
        frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=10)

        self.lbl_material = tk.Label(
            frame, text="Selecione um material", bg=TEMA["painel"], fg=TEMA["muted"], font=("Segoe UI", 10)
        )
        self.lbl_material.pack(pady=(10, 6))

        self.lbl_peso_visor = tk.Label(
            frame, text="0.00 kg", bg=TEMA["painel"], fg=TEMA["cobre"], font=("Consolas", 32, "bold")
        )
        self.lbl_peso_visor.pack(pady=(0, 16))

        self.entry_peso = tk.Entry(
            frame, font=("Consolas", 14), justify="center",
            bg=TEMA["fundo"], fg=TEMA["texto"], insertbackground=TEMA["texto"], relief="flat"
        )
        self.entry_peso.pack(fill="x", ipady=8, pady=(0, 4))
        self.entry_peso.bind("<KeyRelease>", lambda e: self.atualizar_calculo())

        ttk.Label(frame, text="Peso em kg", style="Painel.TLabel").pack(pady=(0, 14))

        self.lbl_valor = tk.Label(
            frame, text="Valor: R$ 0,00", bg=TEMA["painel"], fg=TEMA["total"], font=("Consolas", 13, "bold")
        )
        self.lbl_valor.pack(pady=(0, 18))

        self.btn_adicionar = tk.Button(
            frame, text="Adicionar à pesagem", font=("Segoe UI", 11, "bold"),
            bg=TEMA["cobre"], fg="#1a1300", relief="flat", padx=10, pady=10,
            state="disabled", command=self.adicionar_item
        )
        self.btn_adicionar.pack(fill="x")

    def _montar_ticket(self, pai):
        frame = ttk.Frame(pai, padding=10)
        frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=10)

        ttk.Label(frame, text="Pesagem atual", style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

        self.lista_ticket = tk.Listbox(
            frame, bg=TEMA["fundo"], fg=TEMA["texto"], relief="flat",
            font=("Consolas", 10), highlightthickness=0, selectbackground=TEMA["painel"]
        )
        self.lista_ticket.pack(fill="both", expand=True)

        linha_total = tk.Frame(frame, bg=TEMA["fundo"])
        linha_total.pack(fill="x", pady=(10, 6))
        tk.Label(linha_total, text="Total", bg=TEMA["fundo"], fg=TEMA["muted"], font=("Segoe UI", 10)).pack(side="left")
        self.lbl_total = tk.Label(
            linha_total, text="R$ 0,00", bg=TEMA["fundo"], fg=TEMA["total"], font=("Consolas", 16, "bold")
        )
        self.lbl_total.pack(side="right")

        tk.Button(
            frame, text="Remover selecionado", font=("Segoe UI", 9),
            bg=TEMA["painel"], fg=TEMA["texto"], relief="flat", padx=6, pady=6,
            command=self.remover_item
        ).pack(fill="x", pady=(4, 4))

        tk.Button(
            frame, text="Finalizar e salvar no histórico", font=("Segoe UI", 9, "bold"),
            bg=TEMA["total"], fg="#122016", relief="flat", padx=6, pady=8,
            command=self.finalizar_pesagem
        ).pack(fill="x", pady=(0, 4))

        tk.Button(
            frame, text="Gerar relatório (.txt)", font=("Segoe UI", 9),
            bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=6, pady=6,
            highlightbackground=TEMA["linha"], command=self.gerar_relatorio_atual
        ).pack(fill="x", pady=(0, 4))

        tk.Button(
            frame, text="Limpar pesagem", font=("Segoe UI", 9),
            bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=6, pady=6,
            highlightbackground=TEMA["linha"], command=self.limpar_pesagem
        ).pack(fill="x")

    # ---------- Aba Histórico ----------
    def _montar_aba_historico(self, pai):
        frame = ttk.Frame(pai, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Pesagens finalizadas", style="Muted.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(frame, text="Itens da pesagem selecionada", style="Muted.TLabel").grid(row=0, column=1, sticky="w", padx=(16, 0), pady=(0, 8))

        self.lista_historico = tk.Listbox(
            frame, bg=TEMA["painel"], fg=TEMA["texto"], relief="flat",
            font=("Consolas", 10), highlightthickness=0, selectbackground=TEMA["painel_ativo"]
        )
        self.lista_historico.grid(row=1, column=0, sticky="nsew")
        self.lista_historico.bind("<<ListboxSelect>>", self._mostrar_detalhe_historico)

        self.detalhe_historico = tk.Listbox(
            frame, bg=TEMA["painel"], fg=TEMA["texto"], relief="flat",
            font=("Consolas", 10), highlightthickness=0, selectbackground=TEMA["painel"], activestyle="none"
        )
        self.detalhe_historico.grid(row=1, column=1, sticky="nsew", padx=(16, 0))

        tk.Button(
            frame, text="Atualizar lista", font=("Segoe UI", 9),
            bg=TEMA["fundo"], fg=TEMA["muted"], relief="flat", padx=6, pady=6,
            command=self.atualizar_historico
        ).grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self._registros_historico = []
        self.atualizar_historico()

    def atualizar_historico(self):
        self.lista_historico.delete(0, "end")
        self.detalhe_historico.delete(0, "end")
        registros = self.historico.listar()
        self._registros_historico = registros
        if not registros:
            self.lista_historico.insert("end", "Nenhuma pesagem finalizada ainda.")
            return
        for reg in registros:
            qtd_itens = len(reg["itens"])
            self.lista_historico.insert(
                "end", f"{reg['data']}  —  {qtd_itens} item(ns)  —  R$ {reg['total']:.2f}"
            )

    def _mostrar_detalhe_historico(self, event=None):
        self.detalhe_historico.delete(0, "end")
        selecao = self.lista_historico.curselection()
        if not selecao or not self._registros_historico:
            return
        idx = selecao[0]
        if idx >= len(self._registros_historico):
            return
        registro = self._registros_historico[idx]
        for item in registro["itens"]:
            linha = f"{item['nome']:<10} {item['peso']:>7.2f} kg   R$ {item['valor']:>8.2f}"
            self.detalhe_historico.insert("end", linha)

    # ---------- Lógica da pesagem ----------
    def selecionar_material(self, material):
        self.material_selecionado = material
        for nome, btn in self.botoes_material.items():
            btn.configure(bg=TEMA["painel"] if nome != material["nome"] else TEMA["painel_ativo"])
        self.lbl_material.configure(text=f"{material['nome']} — R$ {material['preco']:.2f}/kg")
        self.atualizar_calculo()

    def atualizar_calculo(self):
        texto = self.entry_peso.get().replace(",", ".")
        try:
            peso = float(texto) if texto else 0.0
        except ValueError:
            peso = 0.0

        self.lbl_peso_visor.configure(text=f"{peso:.2f} kg")

        if self.material_selecionado and peso > 0:
            valor = peso * self.material_selecionado["preco"]
            self.lbl_valor.configure(text=f"Valor: R$ {valor:.2f}")
            self.btn_adicionar.configure(state="normal")
        else:
            self.lbl_valor.configure(text="Valor: R$ 0,00")
            self.btn_adicionar.configure(state="disabled")

    def adicionar_item(self):
        texto = self.entry_peso.get().replace(",", ".")
        try:
            peso = float(texto)
        except ValueError:
            return
        if not self.material_selecionado or peso <= 0:
            return

        item = self.ticket.adicionar(
            nome=self.material_selecionado["nome"], peso=peso, preco=self.material_selecionado["preco"]
        )
        linha = f"{item.nome:<10} {item.peso:>6.2f} kg   R$ {item.valor:>8.2f}"
        self.lista_ticket.insert("end", linha)

        self.entry_peso.delete(0, "end")
        self.atualizar_calculo()
        self._atualizar_total_visor()

    def remover_item(self):
        selecao = self.lista_ticket.curselection()
        if not selecao:
            messagebox.showinfo("Remover item", "Selecione um item da lista para remover.")
            return
        idx = selecao[0]
        self.lista_ticket.delete(idx)
        self.ticket.remover(idx)
        self._atualizar_total_visor()

    def limpar_pesagem(self):
        self.ticket.limpar()
        self.lista_ticket.delete(0, "end")
        self._atualizar_total_visor()

    def _atualizar_total_visor(self):
        self.lbl_total.configure(text=f"R$ {self.ticket.total:.2f}")

    def finalizar_pesagem(self):
        if self.ticket.esta_vazio():
            messagebox.showinfo("Finalizar pesagem", "Adicione ao menos um item antes de finalizar.")
            return
        registro = self.historico.registrar(self.ticket)
        self.atualizar_historico()
        messagebox.showinfo(
            "Pesagem salva", f"Pesagem de R$ {registro['total']:.2f} salva no histórico."
        )
        self.limpar_pesagem()

    def gerar_relatorio_atual(self):
        if self.ticket.esta_vazio():
            messagebox.showinfo("Gerar relatório", "Adicione ao menos um item antes de gerar o relatório.")
            return
        caminho = gerar_relatorio(self.ticket)
        messagebox.showinfo("Relatório gerado", f"Relatório salvo em:\n{caminho}")

    def _sair(self):
        self.root.destroy()
        if self.ao_sair:
            self.ao_sair()
