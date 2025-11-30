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
        
        # Configurar IA con tu clave
        api_key = config.get('ai_config', {}).get('api_key')
        
        if api_key and api_key != 'TU_API_KEY_AQUI':
            try:
                # Establecer API key como variable de entorno (requerido por nuevo SDK)
                os.environ['GEMINI_API_KEY'] = api_key
                
                # Crear cliente con nueva API
                self.client = genai.Client(api_key=api_key)
                
                self.usar_ia = True
                logging.info("✓ IA DE GOOGLE GEMINI FLASH-LITE ACTIVADA CORRECTAMENTE")
                logging.info("✓ Modo: Generación de comentarios únicos y variados")
            except Exception as e:
                logging.error(f"✗ Error configurando IA: {e}")
                self.usar_ia = False
        else:
            logging.warning("⚠ No se encontró API Key, usando modo de respaldo")

        # RESPALDOS mejorados (Por si falla la IA)
        self.respaldos_satisfaccion = [
            "todo muy rico la verdad",
            "me gustó mucho todo bien",
            "excelente comida muy fresca",
            "todo perfecto muy satisfecho",
            "servicio rápido y comida buena",
            "todo limpio y muy rico",
            "la comida llegó caliente todo bien",
            "muy buena atención y comida",
            "todo correcto muy contento",
            "experiencia muy buena volveré",
            "comida deliciosa todo excelente",
            "servicio impecable muy bien todo",
            "muy buena experiencia todo limpio",
            "todo perfecto desde que llegué",
            "comida fresca servicio rápido todo bien"
        ]
        
        self.respaldos_empleado = [
            "muy amable y atento gracias",
            "excelente actitud muy profesional",
            "me atendió muy bien gracias",
            "gran servicio muy paciente",
            "súper amable muy buena atención",
            "muy atento a todo gracias",
            "servicio de calidad muy rápido",
            "me ayudó mucho muy servicial",
            "actitud positiva servicio impecable",
            "muy profesional y simpático",
            "gran atención muy recomendado",
            "hizo todo bien muchas gracias",
            "muy eficiente buena actitud",
            "servicio excepcional muy bien",
            "muy amable de verdad gracias"
        ]
        
        # Variables para tracking de uso
        self.total_generados_ia = 0
        self.total_respaldos = 0
        self.cache_recientes = []  # Para evitar repeticiones

    def obtener_empleado_aleatorio(self):
        """Devuelve uno de los nombres configurados al azar"""
        seleccionado = random.choice(self.empleados)
        logging.info(f"👤 Empleado seleccionado: {seleccionado}")
        return seleccionado

    def generar_comentario_satisfaccion(self, intentos_max=3):
        """
        Genera comentario general con IA
        Usa múltiples estilos y contextos para máxima variación
        """
        if self.usar_ia:
            for intento in range(intentos_max):
                try:
                    # Seleccionar prompt aleatorio para mayor variación
                    prompts = [
                        "Cliente de restaurante comenta sobre su comida. 8-12 palabras casual. Sin puntos. Ejemplo: los tacos estaban muy buenos todo fresco",
                        "Persona habla de lo que comió. 7-10 palabras simple. Sin puntuación. Ejemplo: me gustó la comida estaba rica",
                        "Comentario rápido sobre la experiencia comiendo. 8-11 palabras. Sin signos. Ejemplo: todo muy rico el servicio rápido",
                        "Cliente satisfecho con su pedido de comida. 7-10 palabras. Sin puntos ni comas. Ejemplo: la comida llegó caliente todo bien",
                        "Opinión sobre la comida que ordenó. 8-12 palabras casual. Sin puntuación. Ejemplo: pedí tacos estaban deliciosos muy buena experiencia",
                        "Comentario sobre cómo estuvo todo en el restaurante. 7-11 palabras. Sin signos. Ejemplo: comida rica lugar limpio todo perfecto",
                        "Cliente habla de su visita al lugar. 8-10 palabras simple. Sin puntos. Ejemplo: todo bien la comida fresca y rica",
                        "Opinión rápida sobre lo que comió. 7-12 palabras. Sin puntuación. Ejemplo: me encantó todo estaba muy bueno",
                        "Persona satisfecha comenta sobre su comida. 8-11 palabras casual. Sin signos. Ejemplo: muy rica la comida volvería otra vez",
                        "Cliente feliz con lo que ordenó. 7-10 palabras. Sin puntos. Ejemplo: pedido correcto comida caliente todo excelente"
                    ]
                    
                    prompt_seleccionado = random.choice(prompts)
                    
                    # Llamar a la API Gemini Flash-Lite (sin thinking mode)
                    response = self.client.models.generate_content(
                        model="models/gemini-2.0-flash-lite-001",
                        contents=prompt_seleccionado,
                        config={
                            "temperature": 1.8,  # Muy alta temperatura para máxima variación
                            "top_p": 0.98,
                            "top_k": 64,
                            "max_output_tokens": 50,  # Reducido para forzar respuestas cortas
                        }
                    )
                    
                    # Extraer texto
                    texto = None
                    
                    if hasattr(response, 'text') and response.text:
                        texto = response.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content:
                            content = candidate.content
                            if hasattr(content, 'parts') and content.parts:
                                if hasattr(content.parts[0], 'text'):
                                    texto = content.parts[0].text
                    
                    if not texto:
                        raise Exception(f"Respuesta vacía (finish_reason: {response.candidates[0].finish_reason if response.candidates else 'unknown'})")
                    
                    texto = texto.strip()
                    
                    # Limpieza agresiva del texto
                    texto = texto.replace('"', '').replace("'", "").replace('*', '').replace('`', '')
                    texto = texto.replace('Reseña:', '').replace('Comentario:', '').replace('Opinión:', '')
                    texto = texto.replace('**', '').replace('__', '').replace('~~', '')
                    texto = texto.replace('Ejemplo:', '').replace('ejemplo:', '')
                    
                    # REMOVER TODA LA PUNTUACIÓN para que sea más casual
                    texto = texto.replace('.', '').replace(',', '').replace(';', '').replace(':', '')
                    texto = texto.replace('!', '').replace('¡', '').replace('?', '').replace('¿', '')
                    
                    # Tomar solo la primera línea
                    if '\n' in texto:
                        texto = texto.split('\n')[0]
                    
                    texto = texto.strip()
                    
                    # Verificar que no sea repetido
                    if texto in self.cache_recientes:
                        logging.warning(f"⚠ Comentario duplicado detectado, regenerando...")
                        continue
                    
                    # Validar longitud
                    palabras = len(texto.split())
                    if 5 <= palabras <= 20:
                        # Agregar al cache (mantener últimos 20)
                        self.cache_recientes.append(texto)
                        if len(self.cache_recientes) > 20:
                            self.cache_recientes.pop(0)
                        
                        self.total_generados_ia += 1
                        logging.info(f"🤖 [IA] Comentario único generado ({palabras} palabras)")
                        return texto
                    else:
                        logging.warning(f"⚠ Respuesta IA muy larga/corta ({palabras} palabras), reintentando...")
                        
                except Exception as e:
                    logging.warning(f"⚠ Fallo IA intento {intento + 1}/{intentos_max}: {e}")
                    time.sleep(0.5)
        
        # Si llegamos aquí, usar respaldo aleatorio
        self.total_respaldos += 1
        texto_respaldo = random.choice(self.respaldos_satisfaccion)
        logging.info(f"📋 [Respaldo] Usando comentario predefinido")
        return texto_respaldo

    def generar_comentario_empleado(self, nombre, intentos_max=3):
        """
        Genera comentario específico para el empleado con IA
        Personalizado con el nombre del empleado
        """
        if self.usar_ia:
            for intento in range(intentos_max):
                try:
                    # Múltiples variaciones de prompt
                    prompts = [
                        f"Cliente de restaurante agradece a {nombre} que lo atendió. 7-10 palabras casual. Sin puntos. Ejemplo: {nombre} muy amable me atendió súper bien",
                        f"Persona reconoce al mesero {nombre} por buen servicio. 8-11 palabras simple. Sin puntuación. Ejemplo: {nombre} me atendió muy rápido gracias",
                        f"Comentario sobre {nombre} que atendió la mesa. 7-10 palabras. Sin signos. Ejemplo: {nombre} fue muy atento y amable gracias",
                        f"Cliente satisfecho con la atención de {nombre}. 8-12 palabras. Sin puntos. Ejemplo: {nombre} me ayudó con el pedido muy bien",
                        f"Opinión sobre cómo {nombre} atendió. 7-10 palabras casual. Sin puntuación. Ejemplo: {nombre} súper amable todo muy bien",
                        f"Reconocimiento a {nombre} por su servicio. 8-11 palabras. Sin signos. Ejemplo: gracias {nombre} muy buena atención de tu parte",
                        f"Cliente habla bien de {nombre} que lo sirvió. 7-10 palabras simple. Sin puntos. Ejemplo: {nombre} excelente servicio muy amable",
                        f"Comentario positivo sobre la atención de {nombre}. 8-12 palabras. Sin puntuación. Ejemplo: {nombre} me atendió muy bien gracias por todo",
                        f"Persona agradece a {nombre} del restaurante. 7-9 palabras casual. Sin signos. Ejemplo: {nombre} muy atento muchas gracias",
                        f"Cliente contento con {nombre} que lo atendió. 8-11 palabras. Sin puntos. Ejemplo: {nombre} fue muy servicial todo bien gracias"
                    ]
                    
                    prompt_seleccionado = random.choice(prompts)
                    
                    # Llamar a la API Gemini Flash-Lite
                    response = self.client.models.generate_content(
                        model="models/gemini-2.0-flash-lite-001",
                        contents=prompt_seleccionado,
                        config={
                            "temperature": 1.8,
                            "top_p": 0.98,
                            "top_k": 64,
                            "max_output_tokens": 50,
                        }
                    )
                    
                    # Extraer texto
                    texto = None
                    
                    if hasattr(response, 'text') and response.text:
                        texto = response.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content:
                            content = candidate.content
                            if hasattr(content, 'parts') and content.parts:
                                if hasattr(content.parts[0], 'text'):
                                    texto = content.parts[0].text
                    
                    if not texto:
                        raise Exception(f"Respuesta vacía")
                    
                    texto = texto.strip()
                    
                    # Limpieza
                    texto = texto.replace('"', '').replace("'", "").replace('*', '').replace('`', '')
                    texto = texto.replace('Comentario:', '').replace('Elogio:', '').replace('Agradecimiento:', '')
                    texto = texto.replace('**', '').replace('__', '')
                    texto = texto.replace('Ejemplo:', '').replace('ejemplo:', '')
                    
                    # REMOVER TODA LA PUNTUACIÓN para que sea más casual
                    texto = texto.replace('.', '').replace(',', '').replace(';', '').replace(':', '')
                    texto = texto.replace('!', '').replace('¡', '').replace('?', '').replace('¿', '')
                    
                    # Tomar solo la primera línea
                    if '\n' in texto:
                        texto = texto.split('\n')[0]
                    
                    texto = texto.strip()
                    
                    # Verificar que no sea repetido
                    if texto in self.cache_recientes:
                        logging.warning(f"⚠ Comentario empleado duplicado, regenerando...")
                        continue
                    
                    # Validar longitud
                    palabras = len(texto.split())
                    if 4 <= palabras <= 18:
                        # Agregar al cache
                        self.cache_recientes.append(texto)
                        if len(self.cache_recientes) > 20:
                            self.cache_recientes.pop(0)
                        
                        self.total_generados_ia += 1
                        logging.info(f"🤖 [IA] Comentario empleado único generado ({palabras} palabras)")
                        return texto
                    else:
                        logging.warning(f"⚠ Respuesta IA empleado muy larga/corta, reintentando...")
                        
                except Exception as e:
                    logging.warning(f"⚠ Fallo IA empleado intento {intento + 1}/{intentos_max}: {e}")
                    time.sleep(0.5)
        
        # Respaldo
        self.total_respaldos += 1
        texto_respaldo = random.choice(self.respaldos_empleado)
        logging.info(f"📋 [Respaldo] Usando comentario empleado predefinido")
        return texto_respaldo
    
    def obtener_estadisticas(self):
        """Devuelve estadísticas de uso de IA"""
        total = self.total_generados_ia + self.total_respaldos
        if total == 0:
            return "No se han generado comentarios aún"
        
        porcentaje_ia = (self.total_generados_ia / total) * 100
        return f"IA: {self.total_generados_ia} ({porcentaje_ia:.1f}%) | Respaldos: {self.total_respaldos} | Cache: {len(self.cache_recientes)} únicos"