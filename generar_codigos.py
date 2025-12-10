import datetime
import os

def generar_codigos_automaticos():
    print("\n" + "="*60)
    print("  GENERADOR DE CÓDIGOS TACO BELL (Simplificado)")
    print("="*60 + "\n")

    # 1. PARTE FIJA
    TIENDA = "64"
    RELLENO_ORDEN = "0101" # Según tu instrucción, esto va antes de los últimos 2 números
    
    # 2. FECHA AUTOMÁTICA
    ahora = datetime.datetime.now()
    dia = ahora.strftime("%d")
    mes = ahora.strftime("%m")
    anio = ahora.strftime("%y")
    fecha_formato = f"{dia}{mes}{anio}"
    
    # Base del código hasta el momento
    codigo_base = f"{TIENDA}{fecha_formato}{RELLENO_ORDEN}"
    
    print(f"📅 Fecha de hoy: {dia}/{mes}/20{anio}")
    print(f"🔒 Estructura fija: {codigo_base}XX")
    print("(Donde XX empieza en 01 y aumenta)")
    print("-" * 60)

    # 3. PEDIR CANTIDAD
    while True:
        try:
            cantidad = int(input("\n📊 ¿Cuántos códigos quieres generar?: "))
            if cantidad > 0:
                break
            print("❌ Debe ser mayor a 0.")
        except ValueError:
            print("❌ Error: Ingresa un número entero.")

    # 4. GENERAR LISTA
    lista_codigos = []
    print(f"\nGenerando {cantidad} códigos comenzando desde el 01...")
    
    for i in range(1, cantidad + 1):
        # El contador 'i' empieza en 1, 2, 3...
        # Lo formateamos a 2 dígitos: '01', '02', '10', '99'
        contador = f"{i:02d}"
        
        # Unimos todo
        codigo_final = f"{codigo_base}{contador}"
        lista_codigos.append(codigo_final)

    # 5. GUARDAR
    nombre_archivo = "codigos.txt"
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            for codigo in lista_codigos:
                f.write(codigo + "\n")
        
        print("\n" + "="*60)
        print("✅ ¡LISTO!")
        print(f"Se generaron {len(lista_codigos)} códigos en '{nombre_archivo}'.")
        print(f"Primero: {lista_codigos[0]}")
        print(f"Último:  {lista_codigos[-1]}")
        print("="*60)
        print("👉 Ahora ejecuta tu programa de encuestas y carga el archivo.")
        
    except Exception as e:
        print(f"\n❌ Error al guardar: {e}")

if __name__ == "__main__":
    generar_codigos_automaticos()