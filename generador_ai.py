from google import genai
import random
import logging
import time
import os

class GeneradorRespuestasIA:
    def __init__(self, config):
        self.config = config
        self.usar_ia = False
        self.empleados = config['respuestas'].get('nombres_empleados_posibles', ["Justin", "Danissa", "Allison"])
        
        # Configurar IA
        api_key = config.get('ai_config', {}).get('api_key')
        
        if api_key and api_key != 'TU_API_KEY_AQUI':
            try:
                # Establecer variable de entorno
                os.environ['GEMINI_API_KEY'] = api_key
                self.client = genai.Client(api_key=api_key)
                self.usar_ia = True
                logging.info("✓ IA DE GOOGLE GEMINI LISTA")
            except Exception as e:
                logging.error(f"✗ Error configurando IA: {e}")
                self.usar_ia = False
        else:
            logging.warning("⚠ No se encontró API Key válida")

        # RESPALDOS (Por si falla la IA)
        self.respaldos_satisfaccion = [
            "todo bien gracias",
            "comida rica y rapida",
            "me gusto todo bien",
            "buen servicio rapido",
            "tacos ricos todo bien",
            "todo limpio y rico",
            "atencion rapida gracias",
            "muy rico todo",
            "buena comida",
            "servicio rapido todo bien"
        ]
        
        self.respaldos_empleado = [
            "muy amable gracias",
            "buen servicio rapido",
            "me atendio super bien",
            "muy servicial gracias",
            "atento y rapido",
            "me ayudo con el pedido",
            "muy buena gente",
            "rapido y amable",
            "todo excelente gracias",
            "buena atencion"
        ]
        
        self.total_generados_ia = 0
        self.total_respaldos = 0
        self.cache_recientes = [] 

    def obtener_empleado_aleatorio(self):
        return random.choice(self.empleados)

    def generar_comentario_satisfaccion(self, intentos_max=3):
        """Genera comentario general: PASADO, CORTO, REALISTA."""
        if self.usar_ia:
            for intento in range(intentos_max):
                try:
                    # PROMPTS MEJORADOS: Enfocados en "YA COMÍ" (Pasado)
                    prompts = [
                        "Cliente que ya terminó de comer dice que estuvo rico. 4 palabras. Minúsculas. Sin signos. Ejemplo: todo estuvo muy rico",
                        "Di que el servicio fue rápido y la comida buena. Pasado simple. Muy corto. Ejemplo: me atendieron rapido y bien",
                        "Comentario breve de que la orden llegó bien. Informal. Ejemplo: me dieron todo lo que pedi",
                        "Di que la comida estaba caliente. Pasado. Ejemplo: la comida llego caliente",
                        "Opinión simple: lugar limpio y rico. Minúsculas. Ejemplo: lugar limpio y comida rica",
                        "Cliente satisfecho saliendo del restaurante. 5 palabras máximo. Ejemplo: buena comida y buen servicio",
                        "Di que las papas o tacos estaban buenos. Pasado. Ejemplo: los tacos estaban ricos"
                    ]
                    
                    prompt_seleccionado = random.choice(prompts)
                    
                    response = self.client.models.generate_content(
                        model="models/gemini-2.0-flash-lite-001",
                        contents=prompt_seleccionado,
                        config={
                            "temperature": 0.65,  # Más baja para evitar cosas raras
                            "top_p": 0.90,
                            "top_k": 40,
                            "max_output_tokens": 30, # Muy corto
                        }
                    )
                    
                    texto = self._extraer_texto(response)
                    
                    if texto:
                        # Limpieza total
                        texto = texto.lower().replace('.', '').replace(',', '').strip()
                        # Filtros de seguridad extra
                        if "necesito" in texto or "quiero" in texto or "volveré" in texto:
                            continue 
                            
                        if self._validar_y_guardar(texto):
                            return texto

                except Exception as e:
                    logging.warning(f"⚠ Fallo IA intento {intento + 1}: {e}")
                    time.sleep(0.5)
        
        self.total_respaldos += 1
        return random.choice(self.respaldos_satisfaccion)

    def generar_comentario_empleado(self, nombre, intentos_max=3):
        """Genera comentario empleado: PASADO, SERVICIO, AYUDA."""
        if self.usar_ia:
            for intento in range(intentos_max):
                try:
                    prompts = [
                        f"Di que {nombre} me atendió rápido. Pasado. Minúsculas. Ejemplo: {nombre} fue muy rapido",
                        f"Di que {nombre} fue amable conmigo. Breve. Ejemplo: {nombre} me trato muy bien",
                        f"Menciona que {nombre} me ayudó con la orden. Corto. Ejemplo: gracias {nombre} por la ayuda",
                        f"Comentario simple: {nombre} es servicial. Ejemplo: {nombre} es muy amable",
                        f"Di que {nombre} explicó bien. Pasado. Ejemplo: {nombre} me explico el menu",
                        f"Agradece a {nombre} por el servicio. Informal. Ejemplo: buen servicio de {nombre}",
                        f"Menciona que {nombre} siempre sonríe. Corto. Ejemplo: {nombre} muy buena gente"
                    ]
                    
                    prompt_seleccionado = random.choice(prompts)
                    
                    response = self.client.models.generate_content(
                        model="models/gemini-2.0-flash-lite-001",
                        contents=prompt_seleccionado,
                        config={
                            "temperature": 0.65,
                            "top_p": 0.90,
                            "top_k": 40,
                            "max_output_tokens": 30,
                        }
                    )
                    
                    texto = self._extraer_texto(response)
                    
                    if texto:
                        texto = texto.lower().replace('.', '').replace(',', '').strip()
                        
                        if "guapa" in texto or "linda" in texto or "guapo" in texto:
                            continue

                        if self._validar_y_guardar(texto):
                            return texto
                            
                except Exception as e:
                    logging.warning(f"⚠ Fallo IA empleado intento {intento + 1}: {e}")
                    time.sleep(0.5)
        
        self.total_respaldos += 1
        return random.choice(self.respaldos_empleado)

    def _extraer_texto(self, response):
        try:
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
        except:
            return None
        return None

    def _validar_y_guardar(self, texto):
        texto = texto.replace('"', '').replace("'", "").replace('*', '').replace('example:', '').replace('ejemplo:', '')
        
        if texto in self.cache_recientes:
            return False
            
        palabras = len(texto.split())
        if 2 <= palabras <= 12: # Máximo 12 palabras
            self.cache_recientes.append(texto)
            if len(self.cache_recientes) > 20:
                self.cache_recientes.pop(0)
            self.total_generados_ia += 1
            logging.info(f"🤖 [IA] Generado: {texto}")
            return True
        return False
    
    def obtener_estadisticas(self):
        total = self.total_generados_ia + self.total_respaldos
        if total == 0: return "Sin actividad"
        return f"IA: {self.total_generados_ia} ({(self.total_generados_ia/total)*100:.1f}%) | Respaldos: {self.total_respaldos}"