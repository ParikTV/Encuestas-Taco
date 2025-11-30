"""
Script de diagnóstico para ver la estructura de respuesta de Gemini API
"""
from google import genai
import json
import os

def test_api_structure():
    print("\n" + "="*70)
    print("  DIAGNÓSTICO DE API GEMINI")
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
    
    print(f"✓ API Key encontrada: {api_key[:10]}...")
    
    # Configurar cliente
    try:
        os.environ['GEMINI_API_KEY'] = api_key
        client = genai.Client(api_key=api_key)
        print("✓ Cliente inicializado correctamente\n")
    except Exception as e:
        print(f"❌ Error inicializando cliente: {e}")
        return
    
    # Hacer una llamada de prueba
    print("Haciendo llamada de prueba a la API...")
    print("-" * 70)
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-001",
            contents="Di solo: hola mundo",
            config={
                "temperature": 1.0,
                "max_output_tokens": 200,
            }
        )
        
        print("\n📦 ESTRUCTURA DE RESPUESTA:")
        print("-" * 70)
        print(f"Tipo de objeto: {type(response)}")
        print(f"\nAtributos disponibles:")
        for attr in dir(response):
            if not attr.startswith('_'):
                print(f"  - {attr}")
        
        print("\n" + "="*70)
        print("📝 CONTENIDO DE LA RESPUESTA:")
        print("="*70)
        
        # Intentar diferentes formas de acceder al texto
        print("\n1. Intentando response.text:")
        try:
            if hasattr(response, 'text'):
                print(f"   ✓ Existe: {response.text}")
            else:
                print("   ❌ No existe este atributo")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n2. Intentando response.candidates:")
        try:
            if hasattr(response, 'candidates'):
                print(f"   ✓ Existe, cantidad: {len(response.candidates)}")
                if response.candidates:
                    candidate = response.candidates[0]
                    print(f"   Tipo de candidate: {type(candidate)}")
                    print(f"   Atributos de candidate:")
                    for attr in dir(candidate):
                        if not attr.startswith('_'):
                            print(f"     - {attr}")
                    
                    if hasattr(candidate, 'content'):
                        print(f"\n   ✓ candidate.content existe")
                        content = candidate.content
                        print(f"   Tipo de content: {type(content)}")
                        
                        if hasattr(content, 'parts'):
                            print(f"   ✓ content.parts existe, cantidad: {len(content.parts)}")
                            if content.parts:
                                part = content.parts[0]
                                print(f"   Tipo de part: {type(part)}")
                                print(f"   Atributos de part:")
                                for attr in dir(part):
                                    if not attr.startswith('_'):
                                        print(f"     - {attr}")
                                
                                if hasattr(part, 'text'):
                                    print(f"\n   ✓✓✓ TEXTO ENCONTRADO: {part.text}")
            else:
                print("   ❌ No existe este atributo")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n3. Representación completa del objeto:")
        try:
            print(f"{response}")
        except:
            print("   No se puede representar")
        
        print("\n" + "="*70)
        print("  DIAGNÓSTICO COMPLETADO")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR en llamada a API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_structure()