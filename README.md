# BNB Aéreo

Projeto desenvolvido para a disciplina de **Engenharia de Software - XDES04**.  
Inspirado no Airbnb, o sistema permite cadastro e gerenciamento de usuários e imóveis, com funcionalidades automatizadas de teste via Selenium.

---

## ✅ Funcionalidades Implementadas

- **CRUD de Usuários** (RF1 a RF4)
- **CRUD de Imóveis** (RF5 a RF9)
- Filtros por cidade, estado e tipo de imóvel
- Validação para impedir remoção de proprietário com imóvel ativo
- Testes automatizados com **Selenium** e **Pytest**

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10 ou superior instalado
- Google Chrome
- ChromeDriver compatível (adicionado ao `PATH` do sistema)

### Instalar dependências
```bash
pip install flask selenium pytest
```

### Executar o servidor
```bash
python app.py
```

### Rodar testes automatizados (em outro terminal)
```bash
python -m pytest -q
```

---

## 👥 Integrantes
Grupo 07 – Engenharia de Software – XDES04

Lucas Baesso

Rafael Fernando

Lucas Arouca
