"""
SciCalc Pro — Demo de Automatización con Selenium
==================================================
Ejecutar con:
    cd SciCalcPro/backend
    python tests/e2e/selenium_main.py

Prerequisitos:
    1. PostgreSQL corriendo → docker-compose up -d postgres
    2. Backend corriendo    → python run.py   (en otra terminal)
    3. Chrome instalado en el sistema
    4. Dependencias dev instaladas → pip install -e ".[dev]"

Referencia de pruebas cubiertas:
    RF-001 – Aritmética básica (2+3*4 = 14)
    RF-002 – Trigonometría con toggle DEG/RAD
    RF-003 – Historial de operaciones
    RF-004 – Funciones de memoria M+, MR, MC
    RF-005 – Convertidor de unidades (1000 m → km)
    RF-007 – Cambio de tema oscuro/claro
    RF-008 – Notación científica (1.5e3 * 2)
    RNF-006 – Registro y login con JWT
"""

import sys
import time
import urllib.request
import urllib.error

# ── Windows: asyncpg requiere SelectorEventLoop ──────────────────────────────
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support.ui import Select

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_URL     = "http://localhost:8001"
EMAIL        = "selenium_demo@scicalc.test"
PASSWORD     = "SeleniumDemo1!"
DISPLAY_NAME = "Selenium Demo"
WAIT_SEC     = 10   # timeout máximo para esperas explícitas
PAUSE_SEC    = 1.5  # pausa visual entre pasos


def pause(secs=PAUSE_SEC):
    """Pausa visual para que el navegador sea observable."""
    time.sleep(secs)


def wait_for_server(url, timeout=30):
    """
    Espera a que el backend esté disponible antes de abrir Chrome.
    Lanza SystemExit con mensaje claro si el servidor no responde.
    """
    health = url.rstrip("/") + "/health"
    print(f"  Verificando servidor en {health} ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(health, timeout=2)
            print(f"  ✓  Servidor disponible\n")
            return
        except Exception:
            time.sleep(1)
    print(
        "\n"
        "  ✗  ERROR: el backend no está corriendo en " + url + "\n"
        "\n"
        "  Abre UNA TERMINAL SEPARADA y ejecuta:\n"
        "      cd SciCalcPro/backend\n"
        "      python run.py\n"
        "\n"
        "  Luego vuelve a ejecutar este script.\n"
    )
    sys.exit(1)


def ok(msg):
    print(f"  ✓  {msg}")


def step(n, msg):
    print(f"\n[Paso {n}] {msg}")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── VERIFICAR QUE EL BACKEND ESTÁ CORRIENDO ──────────────────────────────
    wait_for_server(BASE_URL)

    # ── CONFIGURACIÓN DEL NAVEGADOR ──────────────────────────────────────────
    # Selenium Manager descarga automáticamente el ChromeDriver compatible
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,820")
    # Para depuración: quitar la siguiente línea abre el navegador en modo visual
    # options.add_argument("--headless=new")
    driver = Chrome(options=options)

    try:
        # ════════════════════════════════════════════════════════════════════
        # PASO 1 — Registro de usuario (RNF-006)
        # ════════════════════════════════════════════════════════════════════
        step(1, "Registro de nuevo usuario")
        driver.get(f"{BASE_URL}/web/register")
        pause(2)

        driver.find_element(By.ID,   "username").send_keys(DISPLAY_NAME)
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        pause()

        driver.find_element(By.ID, "btn-register").click()

        # Esperar a que aparezca texto en #result
        Wait(driver, WAIT_SEC).until(
            lambda d: d.find_element(By.ID, "result").text.strip() != ""
        )
        reg_result = driver.find_element(By.ID, "result").text
        ok(f"Resultado registro: {reg_result}")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 2 — Login y obtención de JWT (RNF-006)
        # ════════════════════════════════════════════════════════════════════
        step(2, "Inicio de sesión")
        driver.get(f"{BASE_URL}/web/login")
        pause(2)

        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        pause()

        driver.find_element(By.ID, "btn-login").click()

        Wait(driver, WAIT_SEC).until(
            EC.text_to_be_present_in_element((By.ID, "result"), "exitoso")
        )
        ok("Login exitoso")

        # Recuperar token de sessionStorage
        token = driver.execute_script("return sessionStorage.getItem('access_token')")
        ok(f"Token JWT obtenido: {'Sí' if token else 'NO (error)'}")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # Navegar a la calculadora e inyectar el token
        # ════════════════════════════════════════════════════════════════════
        driver.get(f"{BASE_URL}/web/calculator")
        driver.execute_script(f"sessionStorage.setItem('access_token', '{token}')")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 3 — RF-001: Aritmética básica  2 + 3 * 4 = 14
        # ════════════════════════════════════════════════════════════════════
        step(3, "RF-001 — Aritmética: 2 + 3 * 4")
        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        expr.send_keys("2 + 3 * 4")
        driver.find_element(By.ID, "btn-calculate").click()

        Wait(driver, WAIT_SEC).until(
            EC.text_to_be_present_in_element((By.ID, "result"), "14")
        )
        resultado = driver.find_element(By.ID, "result").text
        ok(f"Resultado: {resultado}  (esperado: 14)")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 4 — RF-002: Trigonometría en modo DEG  sin(90) = 1
        # ════════════════════════════════════════════════════════════════════
        step(4, "RF-002 — Trigonometría DEG: sin(90)")
        modo_btn = driver.find_element(By.ID, "angle-mode")
        modo_actual = modo_btn.get_attribute("data-mode")
        ok(f"Modo angular actual: {modo_actual}")

        # Asegurar que estamos en DEG
        if modo_actual != "DEG":
            modo_btn.click()
            pause()

        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        expr.send_keys("sin(90)")
        driver.find_element(By.ID, "btn-calculate").click()

        Wait(driver, WAIT_SEC).until(
            lambda d: d.find_element(By.ID, "result").text.strip() != ""
        )
        resultado = driver.find_element(By.ID, "result").text
        ok(f"sin(90°) = {resultado}  (esperado: 1 o 1.0)")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 5 — RF-002: Cambiar a RAD  →  cos(0) = 1
        # ════════════════════════════════════════════════════════════════════
        step(5, "RF-002 — Cambiar a RAD y calcular cos(0)")
        driver.find_element(By.ID, "angle-mode").click()
        pause()

        modo_nuevo = driver.find_element(By.ID, "angle-mode").get_attribute("data-mode")
        ok(f"Modo angular cambiado a: {modo_nuevo}")

        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        expr.send_keys("cos(0)")
        driver.find_element(By.ID, "btn-calculate").click()

        Wait(driver, WAIT_SEC).until(
            lambda d: d.find_element(By.ID, "result").text.strip() != ""
        )
        resultado = driver.find_element(By.ID, "result").text
        ok(f"cos(0 rad) = {resultado}  (esperado: 1 o 1.0)")
        pause(2)

        # Volver a DEG para los siguientes pasos
        if driver.find_element(By.ID, "angle-mode").get_attribute("data-mode") != "DEG":
            driver.find_element(By.ID, "angle-mode").click()
            pause()

        # ════════════════════════════════════════════════════════════════════
        # PASO 6 — RF-008: Notación científica  1.5e3 * 2 = 3000
        # ════════════════════════════════════════════════════════════════════
        step(6, "RF-008 — Notación científica: 1.5e3 * 2")
        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        expr.send_keys("1.5e3 * 2")
        driver.find_element(By.ID, "btn-calculate").click()

        Wait(driver, WAIT_SEC).until(
            lambda d: d.find_element(By.ID, "result").text.strip() != ""
        )
        resultado = driver.find_element(By.ID, "result").text
        ok(f"1.5e3 * 2 = {resultado}  (esperado: 3000)")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 7 — RF-004: Memoria  M+ → MR → MC
        # ════════════════════════════════════════════════════════════════════
        step(7, "RF-004 — Funciones de memoria: M+, MR, MC")

        # Calcular 250 + 750 = 1000
        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        expr.send_keys("250 + 750")
        driver.find_element(By.ID, "btn-calculate").click()

        Wait(driver, WAIT_SEC).until(
            EC.text_to_be_present_in_element((By.ID, "result"), "1000")
        )
        ok("Calculado 250 + 750 = 1000")

        # M+ — guardar en memoria
        driver.find_element(By.ID, "btn-memory-plus").click()
        pause()

        indicador = driver.find_element(By.ID, "memory-indicator").text
        memoria   = driver.find_element(By.ID, "memory-display").text
        ok(f"Memoria: indicador='{indicador}', valor='{memoria}'")

        # Limpiar la expresión
        expr = driver.find_element(By.ID, "expression")
        expr.clear()
        pause()

        # MR — recuperar en el campo de expresión
        driver.find_element(By.ID, "btn-memory-recall").click()
        pause()

        expr_val = driver.find_element(By.ID, "expression").get_attribute("value")
        ok(f"MR recuperó: {expr_val}  (esperado: 1000)")

        # MC — limpiar memoria
        driver.find_element(By.ID, "btn-memory-clear").click()
        pause()

        indicador = driver.find_element(By.ID, "memory-indicator").text
        ok(f"Tras MC, indicador: '{indicador}'  (esperado: vacío)")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 8 — RF-005: Convertidor de unidades  1000 m → km
        # ════════════════════════════════════════════════════════════════════
        step(8, "RF-005 — Convertidor de unidades: 1000 m → km")

        # Seleccionar categoría LENGTH (ya es default)
        Select(driver.find_element(By.ID, "converter-category")).select_by_value("LENGTH")
        pause(0.5)

        # Valor: 1000
        conv_input = driver.find_element(By.ID, "converter-value")
        conv_input.clear()
        conv_input.send_keys("1000")

        Select(driver.find_element(By.ID, "converter-from")).select_by_value("m")
        Select(driver.find_element(By.ID, "converter-to")).select_by_value("km")
        pause(0.5)

        driver.find_element(By.ID, "btn-convert").click()
        pause()

        conv_result = driver.find_element(By.ID, "converter-result").text
        ok(f"1000 m = {conv_result}  (esperado: 1 km)")

        # Temperatura: 0 °C → 32 °F
        step(8, "RF-005 — Temperatura: 0 °C → 32 °F")
        Select(driver.find_element(By.ID, "converter-category")).select_by_value("TEMP")
        pause(0.5)

        conv_input = driver.find_element(By.ID, "converter-value")
        conv_input.clear()
        conv_input.send_keys("0")

        Select(driver.find_element(By.ID, "converter-from")).select_by_value("C")
        Select(driver.find_element(By.ID, "converter-to")).select_by_value("F")
        pause(0.5)

        driver.find_element(By.ID, "btn-convert").click()
        pause()

        conv_result = driver.find_element(By.ID, "converter-result").text
        ok(f"0 °C = {conv_result}  (esperado: 32 °F)")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 9 — RF-003: Historial de operaciones
        # ════════════════════════════════════════════════════════════════════
        step(9, "RF-003 — Verificar historial de operaciones")

        entradas = driver.find_element(By.ID, "history-list").find_elements(
            By.CSS_SELECTOR, "div[data-id]"
        )
        ok(f"Entradas en historial: {len(entradas)}")

        if entradas:
            primera = entradas[0]
            eid     = primera.get_attribute("data-id")
            texto   = primera.find_element(By.TAG_NAME, "span").text
            ok(f"Primera entrada: {texto}  (id={eid})")
        pause(2)

        # ════════════════════════════════════════════════════════════════════
        # PASO 10 — RF-007: Toggle modo oscuro
        # ════════════════════════════════════════════════════════════════════
        step(10, "RF-007 — Cambio de tema oscuro/claro")

        btn_tema = driver.find_element(By.ID, "theme-toggle-btn")
        texto_antes = btn_tema.text
        ok(f"Botón de tema: '{texto_antes}'")

        btn_tema.click()
        pause(1.5)

        tema_activo = driver.execute_script(
            "return document.documentElement.getAttribute('data-theme')"
        )
        texto_despues = driver.find_element(By.ID, "theme-toggle-btn").text
        ok(f"Tema activado: '{tema_activo}', botón: '{texto_despues}'")

        # Volver al modo claro
        driver.find_element(By.ID, "theme-toggle-btn").click()
        pause(1.5)
        ok("Regresado a modo claro")

        # ════════════════════════════════════════════════════════════════════
        # PASO 11 — Validar credenciales incorrectas (RNF-006)
        # ════════════════════════════════════════════════════════════════════
        step(11, "RNF-006 — Login con contraseña incorrecta debe fallar")
        driver.get(f"{BASE_URL}/web/login")
        pause(2)

        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys("ContraseñaMal123!")
        driver.find_element(By.ID, "btn-login").click()

        Wait(driver, WAIT_SEC).until(
            lambda d: d.find_element(By.ID, "result").text.strip() != ""
        )
        resultado = driver.find_element(By.ID, "result").text
        token_malo = driver.execute_script("return sessionStorage.getItem('access_token')")
        ok(f"Respuesta: '{resultado}'")
        ok(f"Token guardado (debe ser None): {token_malo}")
        pause(3)

        # ════════════════════════════════════════════════════════════════════
        print("\n" + "═" * 60)
        print("  Demo completado — todos los flujos ejecutados con éxito")
        print("═" * 60)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
