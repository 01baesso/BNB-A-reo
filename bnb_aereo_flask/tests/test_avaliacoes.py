import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

def criar_usuario(driver, nome, email, tipo, cpf):
    driver.get(f"{BASE_URL}/usuarios/novo")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "nome")))
    time.sleep(0.5)
    driver.find_element(By.ID, "nome").send_keys(nome)
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys(email)
    time.sleep(0.5)
    driver.find_element(By.ID, "senha").send_keys("Senha123")
    time.sleep(0.5)
    sel = driver.find_element(By.ID, "tipo")
    sel.find_element(By.XPATH, f".//option[@value='{tipo}']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "telefone").send_keys("(11) 91111-1111")
    time.sleep(0.5)
    driver.find_element(By.ID, "cpf").send_keys(cpf)
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/usuarios"))
    time.sleep(1)

def criar_imovel(driver, titulo, proprietario_nome):
    driver.get(f"{BASE_URL}/imoveis/novo")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "titulo")))
    time.sleep(0.5)
    driver.find_element(By.ID, "titulo").send_keys(titulo)
    time.sleep(0.5)
    driver.find_element(By.ID, "descricao").send_keys("Descrição para avaliação")
    time.sleep(0.5)
    driver.find_element(By.ID, "endereco").send_keys("Rua das Flores, 100")
    time.sleep(0.5)
    driver.find_element(By.ID, "cidade").send_keys("CidadeY")
    time.sleep(0.5)
    driver.find_element(By.ID, "estado").send_keys("YY")
    time.sleep(0.5)
    driver.find_element(By.ID, "cep").send_keys("11122233")
    time.sleep(0.5)
    sel_tipo = driver.find_element(By.ID, "tipo_imovel")
    sel_tipo.find_element(By.XPATH, ".//option[@value='Apartamento']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "num_quartos").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_banheiros").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_vagas").send_keys("0")
    time.sleep(0.5)
    driver.find_element(By.ID, "acomoda").send_keys("2")
    time.sleep(0.5)
    driver.find_element(By.ID, "preco").send_keys("50.00")
    time.sleep(0.5)
    sel_prop = driver.find_element(By.ID, "proprietario_id")
    sel_prop.find_element(By.XPATH, f".//option[contains(text(),'{proprietario_nome}')]").click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/imoveis"))
    time.sleep(1)

def criar_reserva(driver, hospede_nome, imovel_titulo):
    driver.get(f"{BASE_URL}/reservas/novo")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "checkin")))
    time.sleep(0.5)
    driver.find_element(By.ID, "checkin").send_keys("06/01/2025")
    time.sleep(0.5)
    driver.find_element(By.ID, "checkout").send_keys("06/03/2025")
    time.sleep(0.5)
    driver.find_element(By.ID, "qtd_hospedes").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.XPATH,
        f"//select[@id='hospede_id']/option[contains(text(),'{hospede_nome}')]"
    ).click()
    time.sleep(0.5)
    driver.find_element(By.XPATH,
        f"//select[@id='imovel_id']/option[contains(text(),'{imovel_titulo}')]"
    ).click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/reservas"))
    time.sleep(1)

def test_criar_editar_filtrar_remover_avaliacao(driver):
    # 1) Criar proprietário e hóspede
    criar_usuario(driver, "PropEval", "prop.eval@bnb.com", "proprietario", "44455566677")
    criar_usuario(driver, "HospEval", "hosp.eval@bnb.com", "hospede", "55566677788")

    # 2) Criar imóvel e reserva concluída
    criar_imovel(driver, "Ap Eval", "PropEval")
    criar_reserva(driver, "HospEval", "Ap Eval")

    # 3) Acessar criação de avaliação
    driver.get(f"{BASE_URL}/avaliacoes/novo")
    time.sleep(1)
    select = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "reserva_id"))
    )
    time.sleep(0.5)
    select.find_element(By.XPATH, "./option[normalize-space(@value)!=''][1]").click()
    time.sleep(0.5)

    # 4) Cadastrar avaliação
    driver.find_element(By.ID, "nota").send_keys("5")
    time.sleep(0.5)
    driver.find_element(By.ID, "comentario").send_keys("Excelente!")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/avaliacoes"))
    time.sleep(1)

    # 5) Verificar se aparece na listagem
    tabela = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table"))
    )
    time.sleep(0.5)
    assert "Excelente!" in tabela.text

    # 6) Filtrar por nota mínima = 5
    driver.find_element(By.NAME, "nota_min").send_keys("5")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    tabela = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table"))
    )
    time.sleep(0.5)
    assert "Excelente!" in tabela.text

    # 7) Editar avaliação
    linha = tabela.find_element(By.XPATH, "//td[contains(text(),'Excelente!')]/..")
    link_editar = linha.find_element(By.LINK_TEXT, "Editar")
    link_editar.click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "comentario")))
    time.sleep(0.5)
    campo = driver.find_element(By.ID, "comentario")
    campo.clear()
    time.sleep(0.5)
    campo.send_keys("Muito bom!")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/avaliacoes"))
    time.sleep(1)
    assert "Muito bom!" in driver.find_element(By.CLASS_NAME, "table").text

    # 8) Remover avaliação
    tabela = driver.find_element(By.CLASS_NAME, "table")
    linha = tabela.find_element(By.XPATH, "//td[contains(text(),'Muito bom!')]/..")
    botao_remover = linha.find_element(By.XPATH,
        ".//button[contains(normalize-space(.),'Remover')]"
    )
    botao_remover.click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.XPATH, "//td[contains(text(),'Muito bom!')]"))
    )
    time.sleep(1)
    assert not driver.find_elements(By.XPATH, "//td[contains(text(),'Muito bom!')]")