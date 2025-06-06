# tests/test_imoveis.py
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

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

def test_criar_filtrar_editar_remover_imovel(driver):
    # 1) Criar um proprietário, caso não exista
    driver.get(f"{BASE_URL}/usuarios/novo")
    time.sleep(1)
    driver.find_element(By.ID, "nome").send_keys("Prop Imov")
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys("prop.imov@bnb.com")
    time.sleep(0.5)
    driver.find_element(By.ID, "senha").send_keys("senha123")
    time.sleep(0.5)
    tipo_select = driver.find_element(By.ID, "tipo")
    tipo_select.find_element(By.XPATH, ".//option[@value='proprietario']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "telefone").send_keys("(11) 95555-5555")
    time.sleep(0.5)
    driver.find_element(By.ID, "cpf").send_keys("99988877766")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/usuarios"))
    time.sleep(1)

    # 2) Acessar lista de imóveis
    driver.get(f"{BASE_URL}/imoveis")
    time.sleep(1)
    assert "Imóveis" in driver.page_source

    # 3) Clicar em “Novo Imóvel”
    botao_novo = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Novo Imóvel"))
    )
    botao_novo.click()
    time.sleep(1)

    # 4) Preencher formulário
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "titulo")))
    time.sleep(0.5)
    driver.find_element(By.ID, "titulo").send_keys("Apartamento Teste")
    time.sleep(0.5)
    driver.find_element(By.ID, "descricao").send_keys("Apartamento de teste automático.")
    time.sleep(0.5)
    driver.find_element(By.ID, "endereco").send_keys("Rua Automação, 50")
    time.sleep(0.5)
    driver.find_element(By.ID, "cidade").send_keys("Rio de Janeiro")
    time.sleep(0.5)
    driver.find_element(By.ID, "estado").send_keys("RJ")
    time.sleep(0.5)
    driver.find_element(By.ID, "cep").send_keys("20040002")
    time.sleep(0.5)
    tipo_imov = driver.find_element(By.ID, "tipo_imovel")
    tipo_imov.find_element(By.XPATH, ".//option[@value='Apartamento']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "num_quartos").send_keys("3")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_banheiros").send_keys("2")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_vagas").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "acomoda").send_keys("5")
    time.sleep(0.5)
    driver.find_element(By.ID, "preco").send_keys("200.00")
    time.sleep(0.5)
    select_prop = driver.find_element(By.ID, "proprietario_id")
    for opt in select_prop.find_elements(By.TAG_NAME, 'option'):
        if "Prop Imov" in opt.text:
            opt.click()
            break
    time.sleep(0.5)

    # 5) Enviar
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/imoveis"))
    time.sleep(1)

    # 6) Verificar se o imóvel aparece na listagem
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "Apartamento Teste" in tabela.text
    time.sleep(1)

    # 7) Filtrar por cidade
    driver.find_element(By.NAME, "cidade").send_keys("Rio de Janeiro")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "Apartamento Teste" in tabela.text
    time.sleep(1)

    # 8) Clicar em editar
    linha = tabela.find_element(By.XPATH, f"//td[contains(text(),'Apartamento Teste')]/..")
    link_editar = linha.find_element(By.LINK_TEXT, "Editar")
    link_editar.click()
    time.sleep(1)

    # 9) Alterar preço para 250
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "preco")))
    time.sleep(0.5)
    campo_preco = driver.find_element(By.ID, "preco")
    campo_preco.clear()
    time.sleep(0.5)
    campo_preco.send_keys("250.00")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/imoveis"))
    time.sleep(1)

    # 10) Verificar se o preço foi atualizado
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "250.00" in tabela.text or "250,00" in tabela.text
    time.sleep(1)

    # 11) Remover o imóvel
    linha = tabela.find_element(By.XPATH, f"//td[contains(text(),'Apartamento Teste')]/..")
    botao_remover = linha.find_element(By.XPATH, ".//button[contains(text(),'Remover')]")
    botao_remover.click()
    time.sleep(1)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    assert "Apartamento Teste" not in tabela.text
    time.sleep(1)
