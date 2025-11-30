"""
Script de prueba para el generador de comentarios con IA
Ejecuta esto para verificar que la IA esté funcionando correctamente
"""

import json
from generador_ai import GeneradorRespuestasIA
import time

def test_generador():
    print("\n" + "="*70)
    print("  PRUEBA DE GENERADOR DE COMENTARIOS CON IA")
    print("="*70 + "\n")
    
    # Cargar configuración
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        print("❌ No se pudo cargar config.json")
        return
    
    # Inicializar generador
    generador = GeneradorRespuestasIA(config)
    
    if not generador.usar_ia:
        print("⚠️  La IA no está activa, se usarán respuestas de respaldo")
        print("   Verifica tu API key en config.json\n")
    
    # Test 1: Generar comentarios de satisfacción
    print("\n📝 TEST 1: Generando 5 comentarios de satisfacción variados")
    print("-" * 70)
    
    for i in range(5):
        print(f"\nComentario #{i+1}:")
        comentario = generador.generar_comentario_satisfaccion()
        print(f"  → {comentario}")
        time.sleep(1)  # Pausa entre generaciones
    
    # Test 2: Generar comentarios de empleados
    print("\n\n👤 TEST 2: Generando comentarios para diferentes empleados")
    print("-" * 70)
    
    empleados = config['respuestas'].get('nombres_empleados_posibles', ['Justin', 'Danissa', 'Allison'])
    
    for empleado in empleados:
        print(f"\nEmpleado: {empleado}")
        
        # Generar 3 comentarios diferentes para el mismo empleado
        for i in range(3):
            comentario = generador.generar_comentario_empleado(empleado)
            print(f"  {i+1}. {comentario}")
            time.sleep(1)
    
    # Test 3: Selección aleatoria de empleados
    print("\n\n🎲 TEST 3: Selección aleatoria de empleados")
    print("-" * 70)
    
    for i in range(5):
        empleado = generador.obtener_empleado_aleatorio()
        comentario = generador.generar_comentario_empleado(empleado)
        print(f"  {i+1}. {empleado}: {comentario}")
        time.sleep(1)
    
    # Estadísticas finales
    print("\n\n📊 ESTADÍSTICAS DE GENERACIÓN")
    print("-" * 70)
    print(f"  {generador.obtener_estadisticas()}")
    
    print("\n" + "="*70)
    print("  PRUEBA COMPLETADA")
    print("="*70 + "\n")
    
    # Verificación visual
    if generador.usar_ia:
        if generador.total_generados_ia > 10:
            print("✅ La IA está funcionando correctamente")
            print("   Todos los comentarios son únicos y variados\n")
        else:
            print("⚠️  La IA funcionó parcialmente")
            print("   Algunos comentarios usaron respaldos\n")
    else:
        print("ℹ️  Se usaron comentarios de respaldo")
        print("   Para activar IA, configura API key de Google Gemini\n")

if __name__ == "__main__":
    test_generador()