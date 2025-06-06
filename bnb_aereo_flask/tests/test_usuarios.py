# tests/test_usuarios.py
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    # Comente a linha abaixo para ver o Chrome “visível”
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

def test_criar_filtrar_editar_remover_usuario(driver):
    # 1) Acessar lista de usuários
    driver.get(f"{BASE_URL}/usuarios")
    time.sleep(1)

    assert "Usuários" in driver.page_source

    # 2) Clicar em “Novo Usuário”
    botao_novo = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Novo Usuário"))
    )
    botao_novo.click()
    time.sleep(1)

    # 3) Preencher formulário de cadastro
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "nome")))
    driver.find_element(By.ID, "nome").send_keys("Teste Automação")
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys("teste.aut@bnb.com")
    time.sleep(0.5)
    driver.find_element(By.ID, "senha").send_keys("Senha123")
    time.sleep(0.5)
    select = driver.find_element(By.ID, "tipo")
    select.find_element(By.XPATH, ".//option[@value='hospede']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "telefone").send_keys("(11) 91234-5678")
    time.sleep(0.5)
    driver.find_element(By.ID, "cpf").send_keys("12345678900")
    time.sleep(0.5)

    # 4) Enviar
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)

    # 5) Volta para a lista e verifica se o novo usuário aparece
    WebDriverWait(driver, 5).until(EC.url_contains("/usuarios"))
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "teste.aut@bnb.com" in tabela.text

    # 6) Filtrar pelo email
    driver.find_element(By.NAME, "email").send_keys("teste.aut@bnb.com")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "teste.aut@bnb.com" in tabela.text

    # 7) Clicar em editar o usuário
    linha = tabela.find_element(By.XPATH, f"//td[contains(text(),'teste.aut@bnb.com')]/..")
    link_editar = linha.find_element(By.LINK_TEXT, "Editar")
    link_editar.click()
    time.sleep(1)

    # 8) Atualizar campo telefone
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "telefone")))
    time.sleep(0.5)
    campo_tel = driver.find_element(By.ID, "telefone")
    campo_tel.clear()
    time.sleep(0.5)
    campo_tel.send_keys("(11) 99876-5432")
    time.sleep(0.5)
    # Deixe senha em branco (editar não obriga)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)

    # 9) Verificar se voltou à lista e mantém o usuário
    WebDriverWait(driver, 5).until(EC.url_contains("/usuarios"))
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "teste.aut@bnb.com" in tabela.text

    # 10) Tentar remover usuário (hóspede → pode remover)
    linha = tabela.find_element(By.XPATH, f"//td[contains(text(),'teste.aut@bnb.com')]/..")
    botao_remover = linha.find_element(By.XPATH, ".//button[contains(text(),'Remover')]")
    botao_remover.click()
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "teste.aut@bnb.com" not in tabela.text

def test_remover_proprietario_com_imovel_ativo(driver):
    # 1) Criar usuário PROPRIETÁRIO
    driver.get(f"{BASE_URL}/usuarios/novo")
    time.sleep(1)
    driver.find_element(By.ID, "nome").send_keys("Prop Test")
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys("prop.test@bnb.com")
    time.sleep(0.5)
    driver.find_element(By.ID, "senha").send_keys("senha123")
    time.sleep(0.5)
    select_tipo = driver.find_element(By.ID, "tipo")
    select_tipo.find_element(By.XPATH, ".//option[@value='proprietario']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "telefone").send_keys("(11) 90000-0000")
    time.sleep(0.5)
    driver.find_element(By.ID, "cpf").send_keys("11122233344")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/usuarios"))

    # 2) Ir para criar imóvel usando este proprietário
    driver.get(f"{BASE_URL}/imoveis/novo")
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "titulo")))
    time.sleep(0.5)
    driver.find_element(By.ID, "titulo").send_keys("Casa do Prop")
    time.sleep(0.5)
    driver.find_element(By.ID, "descricao").send_keys("Casa simples para teste.")
    time.sleep(0.5)
    driver.find_element(By.ID, "endereco").send_keys("Rua Teste, 100")
    time.sleep(0.5)
    driver.find_element(By.ID, "cidade").send_keys("São Paulo")
    time.sleep(0.5)
    driver.find_element(By.ID, "estado").send_keys("SP")
    time.sleep(0.5)
    driver.find_element(By.ID, "cep").send_keys("01001000")
    time.sleep(0.5)
    select_tipo_imov = driver.find_element(By.ID, "tipo_imovel")
    select_tipo_imov.find_element(By.XPATH, ".//option[@value='Casa']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "num_quartos").send_keys("2")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_banheiros").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_vagas").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "acomoda").send_keys("4")
    time.sleep(0.5)
    driver.find_element(By.ID, "preco").send_keys("100.00")
    time.sleep(0.5)
    select_prop = driver.find_element(By.ID, "proprietario_id")
    for opt in select_prop.find_elements(By.TAG_NAME, 'option'):
        if "Prop Test" in opt.text:
            opt.click()
            break
    time.sleep(0.5)
    # Enviar (sem upload de imagem, pois o campo file não existe)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/imoveis"))

    # 3) Tentar remover o usuário “Prop Test”
    driver.get(f"{BASE_URL}/usuarios")
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys("prop.test@bnb.com")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    linha = tabela.find_element(By.XPATH, f"//td[contains(text(),'prop.test@bnb.com')]/..")
    botao_remover = linha.find_element(By.XPATH, ".//button[contains(text(),'Remover')]")
    botao_remover.click()
    time.sleep(1)

    # 4) Verificar que aparece mensagem de erro e continua lá
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "alert-error")))
    time.sleep(1)
    msg = driver.find_element(By.CLASS_NAME, "alert-error").text
    assert "não é possível remover" in msg.lower()

    # 5) Confirmar que o usuário AINDA está listado
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "prop.test@bnb.com" in tabela.text
    time.sleep(1)
