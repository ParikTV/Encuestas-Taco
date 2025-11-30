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

# Configurar encoding UTF-8 para Windows
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
        self.pregunta_actual = 0
        
        # NUEVO: Inicializar generador de IA
        self.generador_ia = GeneradorRespuestasIA(self.config)
        logging.info("🤖 Generador de IA inicializado")
        
    def cargar_configuracion(self, config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"No se encontró {config_file}, usando configuración por defecto")
            return self.configuracion_por_defecto()
    
    def configuracion_por_defecto(self):
        return {
            "respuestas": {
                "tipo_pedido": "Comer en el restaurante",
                "satisfaccion_general": "Muy satisfecho",
                "aspectos_satisfactorios": [
                    "Sabor de la comida",
                    "Amabilidad del personal",
                    "Rapidez del servicio",
                    "Limpieza del restaurante",
                    "Precisión del pedido"
                ],
                "valor_precio": "Muy satisfecho",
                "reconocer_empleado": "Sí",
                "nombres_empleados_posibles": ["Justin", "Danissa", "Allison"],
                "compro_taco_crujiente": "Sí",
                "taco_lleno": "Sí"
            },
            "ai_config": {
                "api_key": "",
                "provider": "gemini"
            },
            "delays": {
                "min": 2,
                "max": 4
            },
            "headless": False
        }
    
    def esperar_aleatorio(self):
        tiempo = random.uniform(
            self.config['delays']['min'],
            self.config['delays']['max']
        )
        time.sleep(tiempo)
    
    def iniciar_navegador(self):
        opciones = webdriver.ChromeOptions()
        if self.config.get('headless', False):
            opciones.add_argument("--headless=new")
        
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.add_argument("--no-sandbox")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opciones
            )
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 15)
            logging.info("Navegador iniciado exitosamente")
            return True
        except Exception as e:
            logging.error(f"Error al iniciar navegador: {e}")
            return False
    
    def ir_a_sitio(self):
        try:
            url = "https://www.clientemania.com/Index.aspx?l=es-CR&c=tacobell&s=UGwE9AKe"
            self.driver.get(url)
            logging.info(f"Navegando a {url}")
            self.esperar_aleatorio()
            
            try:
                boton_continuar = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "NextButton"))
                )
                boton_continuar.click()
                logging.info("Clic en boton 'Continuar' (terminos y condiciones)")
                self.esperar_aleatorio()
            except Exception as e:
                logging.warning(f"No se encontro boton Continuar o ya esta en pagina de codigo: {e}")
            
            return True
        except Exception as e:
            logging.error(f"Error al navegar al sitio: {e}")
            return False
    
    def ingresar_codigo(self):
        try:
            campo_codigo = self.wait.until(
                EC.presence_of_element_located((By.ID, "InputCouponNum"))
            )
            campo_codigo.clear()
            
            for digito in self.codigo_encuesta:
                campo_codigo.send_keys(digito)
                time.sleep(random.uniform(0.05, 0.15))
            
            logging.info(f"Codigo '{self.codigo_encuesta}' ingresado")
            self.esperar_aleatorio()
            
            boton_start = self.driver.find_element(By.ID, "NextButton")
            boton_start.click()
            logging.info("Clic en boton 'Comenzar'")
            self.esperar_aleatorio()
            
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "label")))
                logging.info("Codigo aceptado, iniciando encuesta...")
                return True
            except:
                logging.error(f"El codigo '{self.codigo_encuesta}' parece ser INVALIDO, EXPIRADO o YA USADO")
                return False
            
        except Exception as e:
            logging.error(f"Error al ingresar codigo: {e}")
            self.capturar_pantalla("error_codigo")
            return False
    
    def verificar_radio_seleccionado(self):
        """Verifica que al menos un radio button este seleccionado"""
        try:
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            for radio in radios:
                if radio.is_selected():
                    return True
            return False
        except:
            return False
    
    def seleccionar_radio_escala_satisfaccion(self, nivel_satisfaccion="Muy satisfecho", max_intentos=3):
        """
        Metodo especializado para preguntas de escala de satisfaccion
        Estas preguntas tienen un formato de tabla/matriz diferente
        """
        logging.info(f"Usando metodo especializado para escala de satisfaccion: {nivel_satisfaccion}")
        
        for intento in range(max_intentos):
            if intento > 0:
                logging.warning(f"Reintentando seleccion de escala... Intento {intento + 1}/{max_intentos}")
                time.sleep(1)
            
            # ESTRATEGIA PRINCIPAL: Buscar tabla con radios y headers
            try:
                tablas = self.driver.find_elements(By.TAG_NAME, "table")
                logging.info(f"Tablas encontradas: {len(tablas)}")
                
                for tabla in tablas:
                    headers = tabla.find_elements(By.TAG_NAME, "th")
                    
                    if not headers:
                        headers = tabla.find_elements(By.CSS_SELECTOR, "tr:first-child td")
                    
                    logging.info(f"Headers en tabla: {[h.text.strip() for h in headers if h.text.strip()]}")
                    
                    indice_columna = -1
                    nivel_buscar = nivel_satisfaccion.lower().strip()
                    
                    for i, header in enumerate(headers):
                        header_texto = header.text.strip().lower()
                        if nivel_buscar in header_texto or header_texto in nivel_buscar:
                            indice_columna = i
                            logging.info(f"Columna encontrada en indice {i}: {header.text}")
                            break
                    
                    if indice_columna >= 0:
                        radios_tabla = tabla.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                        logging.info(f"Radios en tabla: {len(radios_tabla)}")
                        
                        if 0 <= indice_columna < len(radios_tabla):
                            radio = radios_tabla[indice_columna]
                            
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                            time.sleep(0.5)
                            
                            self.driver.execute_script("arguments[0].checked = true;", radio)
                            time.sleep(0.2)
                            self.driver.execute_script("arguments[0].click();", radio)
                            time.sleep(0.3)
                            self.driver.execute_script("arguments[0].dispatchEvent(new Event('click', {bubbles: true}));", radio)
                            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", radio)
                            time.sleep(0.5)
                            
                            if radio.is_selected():
                                logging.info(f"[OK] VERIFICADO - Radio de tabla seleccionado (columna {indice_columna})")
                                return True
                            else:
                                logging.warning(f"Radio en columna {indice_columna} NO quedo seleccionado")
                
            except Exception as e:
                logging.warning(f"Estrategia tabla fallo: {e}")
            
            # Estrategia 2: Buscar por atributo value o title
            try:
                radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                logging.info(f"Total radios en pagina: {len(radios)}")
                
                for idx, radio in enumerate(radios):
                    try:
                        value = radio.get_attribute('value') or ""
                        title = radio.get_attribute('title') or ""
                        aria_label = radio.get_attribute('aria-label') or ""
                        id_attr = radio.get_attribute('id') or ""
                        
                        logging.info(f"Radio {idx}: value='{value}', title='{title}', aria='{aria_label}', id='{id_attr}'")
                        
                        textos_buscar = [value, title, aria_label, id_attr]
                        nivel_buscar = nivel_satisfaccion.lower().strip()
                        
                        for texto in textos_buscar:
                            if texto and nivel_buscar in texto.lower():
                                logging.info(f"Coincidencia encontrada en radio {idx}: {texto}")
                                
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                                time.sleep(0.3)
                                
                                self.driver.execute_script("arguments[0].checked = true;", radio)
                                self.driver.execute_script("arguments[0].click();", radio)
                                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", radio)
                                time.sleep(0.5)
                                
                                if radio.is_selected():
                                    logging.info(f"[OK] VERIFICADO - Radio {idx} seleccionado por atributo")
                                    return True
                                break
                    except Exception as e2:
                        logging.warning(f"Error procesando radio {idx}: {e2}")
                        continue
                        
            except Exception as e:
                logging.warning(f"Estrategia atributos fallo: {e}")
            
            # Estrategia 3: Seleccionar primer radio visible (fallback)
            try:
                radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                
                for idx, radio in enumerate(radios):
                    if radio.is_displayed() and radio.is_enabled():
                        logging.info(f"Intentando primer radio visible (indice {idx})")
                        
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                        time.sleep(0.5)
                        
                        try:
                            radio.click()
                        except:
                            pass
                        
                        self.driver.execute_script("arguments[0].checked = true;", radio)
                        self.driver.execute_script("arguments[0].click();", radio)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", radio)
                        time.sleep(0.5)
                        
                        if radio.is_selected():
                            logging.info(f"[OK] VERIFICADO - Primer radio visible seleccionado")
                            return True
                        
                        break
                        
            except Exception as e:
                logging.warning(f"Estrategia primer radio fallo: {e}")
        
        logging.error(f"[ERROR] No se pudo seleccionar escala de satisfaccion despues de {max_intentos} intentos")
        self.capturar_pantalla("error_escala_satisfaccion")
        return False
    
    def seleccionar_radio_inteligente(self, texto_opcion, intentar_indice=1, max_intentos=3):
        """Metodo mejorado para seleccionar radio buttons con verificacion"""
        
        for intento in range(max_intentos):
            if intento > 0:
                logging.warning(f"Reintentando seleccion... Intento {intento + 1}/{max_intentos}")
                time.sleep(1)
            
            # Estrategia 1: Buscar por label con texto
            try:
                labels = self.driver.find_elements(By.TAG_NAME, "label")
                texto_buscar = texto_opcion.lower().strip()
                
                for label in labels:
                    label_texto = label.text.lower().strip()
                    if texto_buscar == label_texto or texto_buscar in label_texto:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                        time.sleep(0.3)
                        
                        self.driver.execute_script("arguments[0].click();", label)
                        time.sleep(0.5)
                        
                        if self.verificar_radio_seleccionado():
                            logging.info(f"[OK] VERIFICADO - Opcion seleccionada (por texto): {label.text}")
                            return True
                        else:
                            logging.warning(f"Click realizado pero radio NO seleccionado (texto)")
                            continue
            except Exception as e:
                logging.warning(f"Estrategia 1 (por texto) fallo: {e}")
            
            # Estrategia 2: Buscar radio buttons directamente por indice
            try:
                radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radios and 0 <= intentar_indice - 1 < len(radios):
                    radio = radios[intentar_indice - 1]
                    
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                    time.sleep(0.3)
                    
                    self.driver.execute_script("arguments[0].checked = true; arguments[0].click();", radio)
                    time.sleep(0.5)
                    
                    if radio.is_selected():
                        logging.info(f"[OK] VERIFICADO - Radio button #{intentar_indice} seleccionado")
                        return True
                    else:
                        logging.warning(f"Radio #{intentar_indice} NO quedo seleccionado")
                        continue
            except Exception as e:
                logging.warning(f"Estrategia 2 (por indice) fallo: {e}")
            
            # Estrategia 3: Click directo y verificacion
            try:
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                for i, input_elem in enumerate(inputs, 1):
                    if i == intentar_indice:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                        time.sleep(0.3)
                        
                        try:
                            input_elem.click()
                        except:
                            self.driver.execute_script("arguments[0].checked = true;", input_elem)
                            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", input_elem)
                        
                        time.sleep(0.5)
                        
                        if input_elem.is_selected():
                            logging.info(f"[OK] VERIFICADO - Input radio #{i} seleccionado")
                            return True
                        else:
                            logging.warning(f"Input #{i} NO quedo seleccionado")
                            continue
            except Exception as e:
                logging.warning(f"Estrategia 3 (inputs) fallo: {e}")
        
        logging.error(f"[ERROR] No se pudo seleccionar ninguna opcion para: {texto_opcion} despues de {max_intentos} intentos")
        self.capturar_pantalla(f"error_radio_no_seleccionado_{texto_opcion}")
        return False
    
    def seleccionar_checkboxes_multiples(self, textos_opciones, max_intentos_por_checkbox=3):
        """Selecciona checkboxes con verificacion"""
        try:
            seleccionados = 0
            
            for texto in textos_opciones:
                texto_buscar = texto.lower().strip()
                checkbox_marcado = False
                
                for intento in range(max_intentos_por_checkbox):
                    if intento > 0:
                        logging.warning(f"Reintentando checkbox '{texto}'... Intento {intento + 1}/{max_intentos_por_checkbox}")
                        time.sleep(0.5)
                    
                    labels = self.driver.find_elements(By.TAG_NAME, "label")
                    
                    for label in labels:
                        label_texto = label.text.lower().strip()
                        if texto_buscar in label_texto:
                            try:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                                time.sleep(0.2)
                                
                                self.driver.execute_script("arguments[0].click();", label)
                                time.sleep(0.4)
                                
                                try:
                                    checkbox_input = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                except:
                                    label_for = label.get_attribute('for')
                                    if label_for:
                                        checkbox_input = self.driver.find_element(By.ID, label_for)
                                    else:
                                        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                                        checkbox_input = checkboxes[0] if checkboxes else None
                                
                                if checkbox_input and checkbox_input.is_selected():
                                    logging.info(f"[OK] VERIFICADO - Checkbox marcado: {label.text}")
                                    seleccionados += 1
                                    checkbox_marcado = True
                                    break
                                else:
                                    logging.warning(f"Checkbox '{texto}' NO quedo marcado en intento {intento + 1}")
                                    
                            except Exception as e:
                                logging.warning(f"Error al marcar checkbox '{texto}': {e}")
                    
                    if checkbox_marcado:
                        break
                
                if not checkbox_marcado:
                    logging.error(f"[ERROR] No se pudo marcar checkbox: {texto}")
                    self.capturar_pantalla(f"error_checkbox_{texto.replace(' ', '_')}")
            
            if seleccionados > 0:
                logging.info(f"Total checkboxes marcados y verificados: {seleccionados}/{len(textos_opciones)}")
            
            return seleccionados > 0
            
        except Exception as e:
            logging.error(f"Error al seleccionar checkboxes: {e}")
            return False
    
    def ingresar_texto_en_campo(self, campo, texto, max_chars=1200, max_intentos=3):
        """Metodo auxiliar para ingresar texto en un campo con verificacion"""
        texto_ajustado = texto[:max_chars] if len(texto) > max_chars else texto
        
        for intento in range(max_intentos):
            if intento > 0:
                logging.warning(f"Reintentando ingresar texto... Intento {intento + 1}/{max_intentos}")
                time.sleep(0.5)
            
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
                time.sleep(0.3)
                
                if not campo.is_displayed():
                    self.driver.execute_script("arguments[0].style.display = 'block';", campo)
                
                campo.clear()
                time.sleep(0.2)
                
                if campo.get_attribute('value'):
                    logging.warning("Campo no se limpio completamente, limpiando con JavaScript")
                    self.driver.execute_script("arguments[0].value = '';", campo)
                    time.sleep(0.2)
                
                for char in texto_ajustado:
                    campo.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                time.sleep(0.3)
                
                valor_actual = campo.get_attribute('value')
                if valor_actual and len(valor_actual) >= len(texto_ajustado) * 0.9:
                    logging.info(f"[OK] VERIFICADO - Texto ingresado correctamente ({len(valor_actual)} caracteres)")
                    return True
                else:
                    logging.warning(f"Texto NO ingresado correctamente. Esperado: {len(texto_ajustado)}, Actual: {len(valor_actual) if valor_actual else 0}")
                    
            except Exception as e:
                logging.error(f"Error al ingresar texto en campo (intento {intento + 1}): {e}")
        
        logging.error(f"[ERROR] No se pudo ingresar texto despues de {max_intentos} intentos")
        self.capturar_pantalla("error_texto_no_ingresado")
        return False
    
    def ingresar_texto(self, texto, max_chars=1200):
        """Busca y llena el primer campo de texto disponible"""
        try:
            campos = self.driver.find_elements(By.TAG_NAME, "textarea")
            if not campos:
                campos = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            
            if campos:
                resultado = self.ingresar_texto_en_campo(campos[0], texto, max_chars)
                if resultado:
                    logging.info(f"Texto ingresado: {texto[:50]}...")
                return resultado
            else:
                logging.warning("No se encontro campo de texto")
                return False
                
        except Exception as e:
            logging.error(f"Error al ingresar texto: {e}")
            return False
    
    def verificar_pagina_respondida(self):
        """Verifica que la pagina actual tenga al menos una respuesta seleccionada"""
        try:
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            radio_seleccionado = any(r.is_selected() for r in radios)
            
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            checkbox_seleccionado = any(c.is_selected() for c in checkboxes)
            
            text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            texto_ingresado = any(t.get_attribute('value') for t in text_inputs + textareas)
            
            if radio_seleccionado or checkbox_seleccionado or texto_ingresado:
                logging.info("[OK] Pagina verificada - Respuesta detectada")
                return True
            else:
                logging.warning("[ADVERTENCIA] No se detectaron respuestas en la pagina actual")
                return False
                
        except Exception as e:
            logging.warning(f"Error al verificar pagina: {e}")
            return True
    
    def siguiente_pagina(self):
        try:
            if not self.verificar_pagina_respondida():
                logging.error("[ERROR CRITICO] No hay respuestas seleccionadas en esta pagina")
                self.capturar_pantalla(f"pagina_sin_responder_{self.pregunta_actual}")
                
                respuesta = input("\n[!] No se detectaron respuestas. Continuar de todas formas? (s/n): ")
                if respuesta.lower() != 's':
                    logging.error("Proceso cancelado por el usuario")
                    return False
            
            self.esperar_aleatorio()
            
            boton = self.wait.until(
                EC.element_to_be_clickable((By.ID, "NextButton"))
            )
            boton.click()
            logging.info(f"Clic en boton 'Siguiente' (Pregunta {self.pregunta_actual})")
            self.pregunta_actual += 1
            self.esperar_aleatorio()
            return True
            
        except Exception as e:
            logging.error(f"Error al hacer clic en Siguiente: {e}")
            self.capturar_pantalla(f"error_siguiente_pregunta_{self.pregunta_actual}")
            return False
    
    def responder_encuesta(self):
        respuestas = self.config['respuestas']
        
        try:
            # PREGUNTA 1: Tipo de Pedido
            self.pregunta_actual = 1
            logging.info("=== PREGUNTA 1: Tipo de Pedido ===")
            if self.seleccionar_radio_inteligente(respuestas.get('tipo_pedido', 'Comer en el restaurante'), 3):
                self.siguiente_pagina()
            else:
                logging.error("No se pudo responder pregunta 1")
                return False
            
            # PREGUNTA 2: Satisfaccion General (ESCALA)
            self.pregunta_actual = 2
            logging.info("=== PREGUNTA 2: Satisfaccion General (ESCALA) ===")
            
            if self.seleccionar_radio_escala_satisfaccion(respuestas.get('satisfaccion_general', 'Muy satisfecho')):
                self.siguiente_pagina()
            else:
                logging.warning("Metodo de escala fallo, intentando metodo normal...")
                if self.seleccionar_radio_inteligente(respuestas.get('satisfaccion_general', 'Muy satisfecho'), 1):
                    self.siguiente_pagina()
                else:
                    logging.error("No se pudo responder pregunta 2")
                    return False
            
            # PREGUNTA 3: Aspectos Satisfactorios (Checkboxes)
            self.pregunta_actual = 3
            logging.info("=== PREGUNTA 3: Aspectos Satisfactorios ===")
            if self.seleccionar_checkboxes_multiples(respuestas.get('aspectos_satisfactorios', [])):
                self.siguiente_pagina()
            else:
                logging.error("No se pudo responder pregunta 3")
                return False
            
            # PREGUNTA 4: Valor por Precio (ESCALA)
            self.pregunta_actual = 4
            logging.info("=== PREGUNTA 4: Valor por Precio (ESCALA) ===")
            
            if self.seleccionar_radio_escala_satisfaccion(respuestas.get('valor_precio', 'Muy satisfecho')):
                self.siguiente_pagina()
            else:
                logging.warning("Metodo de escala fallo, intentando metodo normal...")
                if self.seleccionar_radio_inteligente(respuestas.get('valor_precio', 'Muy satisfecho'), 1):
                    self.siguiente_pagina()
                else:
                    logging.error("No se pudo responder pregunta 4")
                    return False
            
            # PREGUNTA 5: Comentario sobre satisfaccion (CON IA)
            self.pregunta_actual = 5
            logging.info("=== PREGUNTA 5: Comentario sobre satisfaccion (IA) ===")
            
            # Generar comentario con IA
            comentario_ia = self.generador_ia.generar_comentario_satisfaccion()
            logging.info(f"💬 Comentario generado: {comentario_ia}")
            
            if self.ingresar_texto(comentario_ia):
                self.siguiente_pagina()
            else:
                logging.warning("No se pudo ingresar comentario, continuando...")
                self.siguiente_pagina()
            
            # PREGUNTA 6: Desearía expresar reconocimiento?
            self.pregunta_actual = 6
            logging.info("=== PREGUNTA 6: Desearía expresar reconocimiento? ===")
            if self.seleccionar_radio_inteligente(respuestas.get('reconocer_empleado', 'Sí'), 1):
                self.siguiente_pagina()
            else:
                logging.warning("No se pudo responder pregunta 6, continuando...")
                self.siguiente_pagina()
            
            # PREGUNTA 7: Nombre del empleado y comentario (CON IA)
            self.pregunta_actual = 7
            logging.info("=== PREGUNTA 7: Informacion del empleado (IA) ===")
            try:
                time.sleep(2)
                
                # Obtener empleado aleatorio
                nombre_empleado = self.generador_ia.obtener_empleado_aleatorio()
                
                # Generar comentario personalizado con IA
                comentario_empleado = self.generador_ia.generar_comentario_empleado(nombre_empleado)
                logging.info(f"💬 Comentario empleado: {comentario_empleado}")
                
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                logging.info(f"Total inputs en pagina: {len(all_inputs)}")
                logging.info(f"Total textareas en pagina: {len(all_textareas)}")
                
                campos_texto = []
                for inp in all_inputs:
                    tipo = inp.get_attribute('type')
                    if tipo == 'text' and inp.is_displayed() and inp.is_enabled():
                        campos_texto.append(inp)
                        logging.info(f"Campo texto encontrado: type={tipo}")
                
                for ta in all_textareas:
                    if ta.is_displayed() and ta.is_enabled():
                        campos_texto.append(ta)
                        logging.info(f"Textarea encontrado y visible")
                
                logging.info(f"Campos editables encontrados: {len(campos_texto)}")
                
                if len(campos_texto) >= 2:
                    # Campo 1: Nombre
                    if self.ingresar_texto_en_campo(campos_texto[0], nombre_empleado):
                        logging.info(f"[OK] VERIFICADO - Nombre empleado: {nombre_empleado}")
                    else:
                        logging.error("[ERROR] No se pudo verificar nombre del empleado")
                    
                    # Campo 2: Comentario generado por IA
                    time.sleep(0.5)
                    if self.ingresar_texto_en_campo(campos_texto[1], comentario_empleado):
                        logging.info(f"[OK] VERIFICADO - Comentario IA empleado ingresado")
                    else:
                        logging.error("[ERROR] No se pudo verificar comentario del empleado")
                    
                elif len(campos_texto) == 1:
                    if self.ingresar_texto_en_campo(campos_texto[0], nombre_empleado):
                        logging.info(f"[OK] VERIFICADO - Nombre en campo unico: {nombre_empleado}")
                    else:
                        logging.error("[ERROR] No se pudo verificar nombre en campo unico")
                else:
                    logging.warning("[ADVERTENCIA] No se encontraron campos de texto visibles")
                    self.capturar_pantalla("pregunta_7_sin_campos")
                    
            except Exception as e:
                logging.error(f"Error en pregunta 7: {e}")
                self.capturar_pantalla("error_pregunta_7")
            
            self.siguiente_pagina()
            
            # PREGUNTA 8: Compro taco crujiente
            self.pregunta_actual = 8
            logging.info("=== PREGUNTA 8: Compro taco crujiente? ===")
            if self.seleccionar_radio_inteligente(respuestas.get('compro_taco_crujiente', 'Sí'), 1):
                self.siguiente_pagina()
            else:
                logging.warning("No se pudo responder pregunta 8, continuando...")
                self.siguiente_pagina()
            
            # PREGUNTA 9: Taco se veia lleno
            self.pregunta_actual = 9
            logging.info("=== PREGUNTA 9: Taco se veia lleno? ===")
            
            time.sleep(2)
            
            pregunta_9_respondida = False
            
            if self.seleccionar_radio_inteligente(respuestas.get('taco_lleno', 'Sí'), 1):
                pregunta_9_respondida = True
            
            if not pregunta_9_respondida:
                try:
                    all_radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    logging.info(f"Total radio buttons: {len(all_radios)}")
                    
                    for i, radio in enumerate(all_radios):
                        if radio.is_displayed() and radio.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                            time.sleep(0.3)
                            self.driver.execute_script("arguments[0].checked = true; arguments[0].click();", radio)
                            logging.info(f"[OK] Seleccionado radio visible #{i+1}")
                            pregunta_9_respondida = True
                            break
                except Exception as e:
                    logging.warning(f"Error buscando radios: {e}")
            
            if pregunta_9_respondida:
                self.siguiente_pagina()
            else:
                logging.warning("[ADVERTENCIA] No se pudo responder pregunta 9")
                self.capturar_pantalla("pregunta_9_sin_responder")
                try:
                    self.siguiente_pagina()
                except:
                    logging.error("No se pudo continuar")
            
            time.sleep(3)
            
            logging.info("\n" + "="*60)
            logging.info("ENCUESTA COMPLETADA!")
            logging.info("="*60 + "\n")
            return True
            
        except Exception as e:
            logging.error(f"Error general al responder encuesta: {e}")
            self.capturar_pantalla(f"error_pregunta_{self.pregunta_actual}")
            return False
    
    def capturar_pantalla(self, nombre):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{nombre}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logging.info(f"Captura de pantalla: {filename}")
        except Exception as e:
            logging.error(f"Error al capturar pantalla: {e}")
    
    def ejecutar(self):
        try:
            logging.info(f"\n{'='*60}")
            logging.info(f"=== Iniciando encuesta {self.codigo_encuesta} ===")
            logging.info(f"{'='*60}\n")
            
            if not self.iniciar_navegador():
                return False
            
            if not self.ir_a_sitio():
                return False
            
            if not self.ingresar_codigo():
                return False
            
            resultado = self.responder_encuesta()
            
            # Mostrar estadísticas de uso de IA
            estadisticas = self.generador_ia.obtener_estadisticas()
            logging.info(f"\n📊 Estadísticas IA: {estadisticas}\n")
            
            if resultado:
                self.capturar_pantalla("exito_final")
            else:
                self.capturar_pantalla("error_final")
            
            time.sleep(3)
            return resultado
            
        except Exception as e:
            logging.error(f"Error general en la ejecucion: {e}")
            self.capturar_pantalla("error_general")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Navegador cerrado\n")


def main():
    print("\n" + "="*60)
    print("  AUTOMATIZADOR DE ENCUESTAS TACO BELL")
    print("="*60 + "\n")
    
    codigo = "64261125010101"
    print(f"Procesando encuesta con codigo: {codigo}\n")
    
    automatizador = EncuestaAutomatizador(codigo)
    resultado = automatizador.ejecutar()
    
    if resultado:
        print("\n[OK] Encuesta completada exitosamente!")
    else:
        print("\n[ERROR] Hubo un error al completar la encuesta.")


if __name__ == "__main__":
    main()