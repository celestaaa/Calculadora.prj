# Balança de Materiais

Sistema desktop (Python + Tkinter) para pesagem e cotação de materiais recicláveis,
com login por empresa, histórico de pesagens e geração de relatórios.

## Estrutura

- `main.py` — ponto de entrada (abre a tela de login)
- `tela_login.py` — tela de login e criação de conta
- `autenticacao.py` — cadastro/validação de usuários (senha protegida com hash + salt)
- `interface.py` — tela principal da balança (abas de Pesagem e Histórico)
- `modelo.py` — classes `ItemPesagem` e `Ticket`
- `armazenamento.py` — histórico em JSON e geração de relatórios em `.txt`
- `materiais.py` — lista de materiais, preços por kg e tema visual

## Como rodar

Requer apenas Python 3.10+ (Tkinter já vem incluso na instalação padrão).

```bash
python main.py
```

Na primeira execução, clique em **"Criar conta da empresa"** para cadastrar seu
usuário e senha. Nas próximas vezes, use a tela de login normalmente.

## Dados locais

A pasta `dados/` (usuários, histórico e relatórios) é gerada automaticamente ao
rodar o programa e **não é versionada** (veja `.gitignore`), pois contém
informações específicas de cada instalação/empresa.
