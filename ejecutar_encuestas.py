"""
Script para ejecutar encuestas en lote desde un archivo de códigos
"""
from encuestas import EncuestaAutomatizador
import time
import random
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_encuestas.log'),
        logging.StreamHandler()
    ]
)

def cargar_codigos(archivo='codigos.txt'):
    """
    Carga los códigos de encuesta desde un archivo de texto
    
    Args:
        archivo: Ruta al archivo con los códigos (uno por línea)
    
    Returns:
        Lista de códigos
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            codigos = [linea.strip() for linea in f if linea.strip()]
        logging.info(f"Cargados {len(codigos)} códigos desde {archivo}")
        return codigos
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo {archivo}")
        return []

def ejecutar_lote(archivo_codigos='codigos.txt', config_file='config.json'):
    """
    Ejecuta encuestas en lote para todos los códigos en el archivo
    
    Args:
        archivo_codigos: Archivo con códigos de encuesta
        config_file: Archivo de configuración JSON
    """
    codigos = cargar_codigos(archivo_codigos)
    
    if not codigos:
        print("No hay códigos para procesar")
        return
    
    # Cargar configuración para obtener delays
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {
            "delay_entre_encuestas_min": 30,
            "delay_entre_encuestas_max": 60
        }
    
    resultados = {
        'exitosos': [],
        'fallidos': []
    }
    
    total = len(codigos)
    
    print(f"\n{'='*60}")
    print(f"  PROCESAMIENTO EN LOTE DE ENCUESTAS")
    print(f"  Total de encuestas: {total}")
    print(f"{'='*60}\n")
    
    for i, codigo in enumerate(codigos, 1):
        print(f"\n--- Encuesta {i}/{total} ---")
        print(f"Código: {codigo}")
        
        try:
            automatizador = EncuestaAutomatizador(codigo, config_file)
            resultado = automatizador.ejecutar()
            
            if resultado:
                resultados['exitosos'].append(codigo)
                print(f"✓ Completada exitosamente")
            else:
                resultados['fallidos'].append(codigo)
                print(f"✗ Falló")
            
        except Exception as e:
            logging.error(f"Error al procesar código {codigo}: {e}")
            resultados['fallidos'].append(codigo)
            print(f"✗ Error: {e}")
        
        # Esperar antes de la siguiente encuesta (excepto en la última)
        if i < total:
            delay = random.randint(
                config['delay_entre_encuestas_min'],
                config['delay_entre_encuestas_max']
            )
            print(f"\nEsperando {delay} segundos antes de la siguiente encuesta...")
            time.sleep(delay)
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"  RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Total procesadas: {total}")
    print(f"Exitosas: {len(resultados['exitosos'])} ({len(resultados['exitosos'])/total*100:.1f}%)")
    print(f"Fallidas: {len(resultados['fallidos'])} ({len(resultados['fallidos'])/total*100:.1f}%)")
    
    if resultados['fallidos']:
        print(f"\nCódigos fallidos:")
        for codigo in resultados['fallidos']:
            print(f"  - {codigo}")
    
    # Guardar resumen en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    resumen_file = f"resumen_{timestamp}.json"
    with open(resumen_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2)
    
    print(f"\nResumen guardado en: {resumen_file}")
    print(f"{'='*60}\n")
    
    return resultados

def main():
    """Función principal"""
    print("\n=== AUTOMATIZADOR DE ENCUESTAS EN LOTE ===\n")
    
    # Opción 1: Ejecutar desde archivo de códigos
    print("Leyendo códigos desde 'codigos.txt'...")
    ejecutar_lote()

if __name__ == "__main__":
    main()
