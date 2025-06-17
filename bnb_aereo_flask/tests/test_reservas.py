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
    driver.find_element(By.ID, "telefone").send_keys("(11) 90000-0000")
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
    driver.find_element(By.ID, "descricao").send_keys("Descrição teste")
    time.sleep(0.5)
    driver.find_element(By.ID, "endereco").send_keys("Rua Teste, 1")
    time.sleep(0.5)
    driver.find_element(By.ID, "cidade").send_keys("CidadeX")
    time.sleep(0.5)
    driver.find_element(By.ID, "estado").send_keys("ST")
    time.sleep(0.5)
    driver.find_element(By.ID, "cep").send_keys("00000000")
    time.sleep(0.5)
    sel_tipo = driver.find_element(By.ID, "tipo_imovel")
    sel_tipo.find_element(By.XPATH, ".//option[@value='Casa']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "num_quartos").send_keys("2")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_banheiros").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "num_vagas").send_keys("1")
    time.sleep(0.5)
    driver.find_element(By.ID, "acomoda").send_keys("3")
    time.sleep(0.5)
    driver.find_element(By.ID, "preco").send_keys("100.00")
    time.sleep(0.5)
    sel_prop = driver.find_element(By.ID, "proprietario_id")
    sel_prop.find_element(By.XPATH, f".//option[contains(text(),'{proprietario_nome}')]").click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/imoveis"))
    time.sleep(1)

def criar_reserva(driver, hospede_nome, imovel_titulo, checkin_iso, checkout_iso):
    driver.get(f"{BASE_URL}/reservas/novo")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "checkin")))
    time.sleep(0.5)
    driver.find_element(By.ID, "checkin").send_keys(checkin_iso)
    time.sleep(0.5)
    driver.find_element(By.ID, "checkout").send_keys(checkout_iso)
    time.sleep(0.5)
    driver.find_element(By.ID, "qtd_hospedes").send_keys("2")
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

def test_criar_editar_filtrar_remover_reserva(driver):
    # 1) Criar proprietário e hóspede
    criar_usuario(driver, "PropReserva", "prop.res@bnb.com", "proprietario", "22233344455")
    criar_usuario(driver, "HospReserva", "hosp.res@bnb.com", "hospede", "33344455566")

    # 2) Criar imóvel
    criar_imovel(driver, "Casa Reserva", "PropReserva")

    # 3) Reserva passada (para outro teste)
    criar_reserva(driver, "HospReserva", "Casa Reserva", "06/10/2025", "06/12/2025")

    # 4) Reserva futura (para permitir edição)
    criar_reserva(driver, "HospReserva", "Casa Reserva", "07/20/2025", "07/22/2025")

    # 5) Listar reservas
    driver.get(f"{BASE_URL}/reservas")
    time.sleep(1)
    tabela = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table"))
    )
    time.sleep(0.5)
    assert "HospReserva" in tabela.text

    # 6) Filtrar por hóspede
    driver.find_element(By.NAME, "hospede").send_keys("HospReserva")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    tabela = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table"))
    )
    time.sleep(0.5)
    assert "HospReserva" in tabela.text

    # 7) Editar a reserva futura (Check-in 2025-07-20 → checkout 2025-07-23)
    linha = tabela.find_element(By.XPATH, "//td[contains(text(),'07/20/2025')]/..")
    link_editar = linha.find_element(By.LINK_TEXT, "Editar")
    link_editar.click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "checkout")))
    time.sleep(0.5)
    campo = driver.find_element(By.ID, "checkout")
    campo.clear()
    time.sleep(0.5)
    campo.send_keys("07/23/2025")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(EC.url_contains("/reservas"))
    time.sleep(1)
    assert "07/23/2025" in driver.find_element(By.CLASS_NAME, "table").text

    # 8) Remover essa reserva (pela data editada)
    tabela = driver.find_element(By.CLASS_NAME, "table")
    linha = tabela.find_element(By.XPATH, "//td[contains(text(),'07/23/2025')]/..")
    botao_remover = linha.find_element(By.XPATH, ".//button[contains(normalize-space(.),'Remover')]")
    botao_remover.click()
    time.sleep(1)
    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.XPATH, "//td[contains(text(),'07/23/2025')]"))
    )
    time.sleep(1)
    assert not driver.find_elements(By.XPATH, "//td[contains(text(),'07/23/2025')]")