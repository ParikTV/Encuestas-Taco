"""
Script para listar todos los modelos disponibles en Gemini API
"""
from google import genai
import json
import os

def list_available_models():
    print("\n" + "="*70)
    print("  MODELOS DISPONIBLES EN GEMINI API")
    print("="*70 + "\n")
    
    # Cargar config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_key = config.get('ai_config', {}).get('api_key')
    except Exception as e:
        print(f"❌ Error cargando config.json: {e}")
        return
    
    if not api_key or api_key == 'TU_API_KEY_AQUI':
        print("❌ No se encontró API key válida en config.json")
        return
    
    # Configurar cliente
    try:
        os.environ['GEMINI_API_KEY'] = api_key
        client = genai.Client(api_key=api_key)
        print("✓ Cliente inicializado correctamente\n")
    except Exception as e:
        print(f"❌ Error inicializando cliente: {e}")
        return
    
    # Listar modelos
    try:
        print("📋 Listando modelos disponibles...")
        print("-" * 70)
        
        models = client.models.list()
        
        print(f"\nTotal de modelos: {len(list(models))}\n")
        
        # Listar nuevamente para mostrar detalles
        models = client.models.list()
        
        for i, model in enumerate(models, 1):
            print(f"{i}. Nombre: {model.name}")
            if hasattr(model, 'display_name'):
                print(f"   Display Name: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"   Descripción: {model.description[:100] if model.description else 'N/A'}...")
            if hasattr(model, 'supported_generation_methods'):
                print(f"   Métodos: {model.supported_generation_methods}")
            print()
        
        print("="*70)
        print("MODELOS RECOMENDADOS PARA GENERAR TEXTO:")
        print("="*70)
        
        # Buscar modelos flash
        models = client.models.list()
        for model in models:
            if 'flash' in model.name.lower() and 'generateContent' in str(getattr(model, 'supported_generation_methods', [])):
                print(f"✓ {model.name}")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR listando modelos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_available_models()