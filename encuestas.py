from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import logging
from datetime import datetime
from generador_ai import GeneradorRespuestasIA

# Configuración de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('encuestas.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EncuestaAutomatizador:
    def __init__(self, codigo_encuesta, config_file='config.json'):
        self.codigo_encuesta = codigo_encuesta
        self.config = self.cargar_configuracion(config_file)
        self.driver = None
        self.wait = None
        self.pregunta_actual = 0
        self.generador_ia = GeneradorRespuestasIA(self.config)
        logging.info("🤖 Generador de IA inicializado")
        
    def cargar_configuracion(self, config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.configuracion_por_defecto()
    
    def configuracion_por_defecto(self):
        # --- CONFIGURACIÓN "TURBO" ---
        return {
            "respuestas": {
                "tipo_pedido": "Comer en el restaurante",
                "satisfaccion_general": "Muy satisfecho",
                "aspectos_satisfactorios": ["Sabor de la comida", "Amabilidad del personal", "Rapidez del servicio"],
                "valor_precio": "Muy satisfecho",
                "reconocer_empleado": "Sí",
                "nombres_empleados_posibles": ["Justin", "Danissa", "Allison"],
                "compro_taco_crujiente": "Sí",
                "taco_lleno": "Sí"
            },
            "ai_config": {"api_key": "", "provider": "gemini"},
            # AQUÍ ESTÁ LA CLAVE DE LA VELOCIDAD:
            "delays": {"min": 0.5, "max": 1.5}, 
            "headless": False
        }
    
    def esperar_aleatorio(self):
        # Usa los tiempos reducidos del config
        tiempo = random.uniform(self.config['delays']['min'], self.config['delays']['max'])
        time.sleep(tiempo)
    
    # --- PASO 1: SOLO ABRIR NAVEGADOR ---
    def abrir_navegador_en_google(self):
        opciones = webdriver.ChromeOptions()
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--remote-allow-origins=*") 
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 15) # Timeout estándar
            
            self.driver.get("https://www.google.com")
            logging.info("Navegador listo. Esperando VPN...")
            return True
        except Exception as e:
            logging.error(f"Error al iniciar navegador: {e}")
            return False

    # --- PASO 2: IR A LA ENCUESTA Y RESPONDER ---
    def ejecutar_logica_encuesta(self):
        if not self.driver:
            logging.error("❌ El navegador no está abierto.")
            return False

        try:
            # Reconexión rápida
            try:
                handles = self.driver.window_handles
                if not handles: return False
                self.driver.switch_to.window(handles[0])
            except:
                return False

            time.sleep(1) # Pequeña pausa post-vpn (reducida)

            if not self.ir_a_sitio(): return False
            if not self.ingresar_codigo(): return False
            
            resultado = self.responder_encuesta()
            
            # Captura de pantalla solo si falla para ahorrar tiempo, o al final
            if not resultado:
                self.capturar_pantalla("error_final")
                
            return resultado
            
        except Exception as e:
            logging.error(f"Error CRÍTICO: {e}")
            return False

    def ir_a_sitio(self):
        try:
            url = "https://www.clientemania.com/Index.aspx?l=es-CR&c=tacobell&s=UGwE9AKe"
            self.driver.get(url)
            
            # Intento de clic ultra-rápido si aparece el botón
            try:
                boton_continuar = self.wait.until(EC.element_to_be_clickable((By.ID, "NextButton")))
                boton_continuar.click()
            except:
                pass
            return True
        except Exception as e:
            logging.error(f"Error navegación: {e}")
            return False
    
    def ingresar_codigo(self):
        try:
            campo_codigo = self.wait.until(EC.presence_of_element_located((By.ID, "InputCouponNum")))
            campo_codigo.clear()
            
            # Escritura TURBO (casi instantánea)
            for digito in self.codigo_encuesta:
                campo_codigo.send_keys(digito)
                time.sleep(0.01) # Antes era 0.15, ahora vuela
            
            # Clic rápido
            boton_start = self.driver.find_element(By.ID, "NextButton")
            boton_start.click()
            
            # Espera inteligente en lugar de sleep(3)
            try:
                # Esperamos a que desaparezca el botón o aparezca el body nuevo
                self.wait.until(EC.staleness_of(boton_start))
            except:
                pass
            
            return True
        except Exception as e:
            logging.error(f"Error código: {e}")
            return False

    # --- MÉTODOS DE RESPUESTA RÁPIDOS ---
    def seleccionar_radio_escala_satisfaccion(self, nivel_satisfaccion="Muy satisfecho"):
        try:
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            for radio in radios:
                val = (radio.get_attribute('value') or "").lower()
                target = nivel_satisfaccion.lower()
                if target in val:
                    self.driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.1) # Pausa mínima
                    return True
            # Fallback rápido al primero
            if radios:
                self.driver.execute_script("arguments[0].click();", radios[0])
                time.sleep(0.1)
                return True
            return False
        except: return False

    def seleccionar_radio_inteligente(self, texto_opcion, intentar_indice=1):
        try:
            # Intenta buscar por texto primero (más preciso)
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            for label in labels:
                if texto_opcion.lower() in label.text.lower():
                    self.driver.execute_script("arguments[0].click();", label)
                    time.sleep(0.1)
                    return True
            
            # Si no, usa el índice (más rápido)
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radios and len(radios) >= intentar_indice:
                self.driver.execute_script("arguments[0].click();", radios[intentar_indice-1])
                time.sleep(0.1)
                return True
            return False
        except: return False

    def seleccionar_checkboxes_multiples(self, opciones):
        try:
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            count = 0
            for label in labels:
                for op in opciones:
                    if op.lower() in label.text.lower():
                        self.driver.execute_script("arguments[0].click();", label)
                        count += 1
            time.sleep(0.1) # Solo una espera al final
            return count > 0
        except: return False

    def ingresar_texto(self, texto):
        try:
            campos = self.driver.find_elements(By.TAG_NAME, "textarea")
            if not campos: campos = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if campos:
                campos[0].clear()
                campos[0].send_keys(texto)
                return True
            return False
        except: return False
            
    def ingresar_texto_en_campo(self, campo, texto):
        try:
            campo.clear()
            campo.send_keys(texto)
            return True
        except: return False

    def siguiente_pagina(self):
        try:
            # Espera reducida antes de dar siguiente
            self.esperar_aleatorio() 
            btn = self.wait.until(EC.element_to_be_clickable((By.ID, "NextButton")))
            btn.click()
            return True
        except: return False

    def responder_encuesta(self):
        resp = self.config['respuestas']
        try:
            # FLUJO OPTIMIZADO
            # P1
            self.seleccionar_radio_inteligente(resp.get('tipo_pedido', 'Comer'), 3)
            self.siguiente_pagina()
            
            # P2
            self.seleccionar_radio_escala_satisfaccion(resp.get('satisfaccion_general', 'Muy satisfecho'))
            self.siguiente_pagina()
            
            # P3
            self.seleccionar_checkboxes_multiples(resp.get('aspectos_satisfactorios', []))
            self.siguiente_pagina()
            
            # P4
            self.seleccionar_radio_escala_satisfaccion(resp.get('valor_precio', 'Muy satisfecho'))
            self.siguiente_pagina()
            
            # P5 (Comentario IA)
            comentario = self.generador_ia.generar_comentario_satisfaccion()
            self.ingresar_texto(comentario)
            self.siguiente_pagina()
            
            # P6
            self.seleccionar_radio_inteligente(resp.get('reconocer_empleado', 'Sí'), 1)
            self.siguiente_pagina()
            
            # P7 (Empleado)
            nombre = self.generador_ia.obtener_empleado_aleatorio()
            comentario_emp = self.generador_ia.generar_comentario_empleado(nombre)
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
            visible_inputs = [i for i in inputs if i.is_displayed()]
            
            if len(visible_inputs) >= 1: self.ingresar_texto_en_campo(visible_inputs[0], nombre)
            if len(visible_inputs) >= 2: self.ingresar_texto_en_campo(visible_inputs[1], comentario_emp)
            self.siguiente_pagina()
            
            # P8
            self.seleccionar_radio_inteligente(resp.get('compro_taco_crujiente', 'Sí'), 1)
            self.siguiente_pagina()
            
            # P9
            self.seleccionar_radio_inteligente(resp.get('taco_lleno', 'Sí'), 1)
            self.siguiente_pagina()
            
            logging.info("⚡ ENCUESTA COMPLETADA (TURBO)")
            return True
        except Exception as e:
            logging.error(f"Error en flujo: {e}")
            return False

    def capturar_pantalla(self, nombre):
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"screenshot_{nombre}_{ts}.png")
        except: pass

    def cerrar_navegador(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except: pass