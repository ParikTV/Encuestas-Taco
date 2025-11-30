# 🤖 Automatizador de Encuestas ClienteMania

Sistema de automatización para completar encuestas de ClienteMania (Taco Bell Survey) de forma eficiente.

## 📋 Requisitos

- Python 3.7 o superior
- Google Chrome instalado

## 🚀 Instalación

1. **Instalar las dependencias necesarias:**

```bash
pip install selenium webdriver-manager
```

## ⚙️ Configuración

### 1. Archivo `config.json`

Configura las respuestas de la encuesta editando `config.json`:

```json
{
  "respuestas_aleatorias": false,
  "respuestas": {
    "satisfaccion_general": 5,
    "velocidad_servicio": 5,
    "calidad_comida": 5,
    "limpieza": 5,
    "amabilidad_personal": 5,
    "probabilidad_recomendar": 5,
    "visita_previa": "Si",
    "proporcionar_contacto": false
  },
  "delays": {
    "min": 2,
    "max": 5
  },
  "headless": false
}
```

**Opciones:**
- `respuestas_aleatorias`: `true` para respuestas aleatorias (4-5), `false` para usar los valores fijos
- `respuestas`: Valores de 1-5 para cada pregunta de calificación
- `delays`: Tiempo de espera en segundos entre acciones (min-max)
- `headless`: `true` para ejecutar sin ventana visible, `false` para ver el navegador

### 2. Archivo `codigos.txt`

Agrega tus códigos de encuesta, uno por línea:

```
64261125010101
64261125020202
64261125030303
```

## 📝 Uso

### Opción 1: Encuesta Individual

Ejecuta una sola encuesta modificando el código en `encuestas.py`:

```bash
python encuestas.py
```

### Opción 2: Procesamiento en Lote

Ejecuta múltiples encuestas desde `codigos.txt`:

```bash
python ejecutar_encuestas.py
```

El script:
- ✅ Procesará cada código automáticamente
- ✅ Esperará entre 30-60 segundos entre encuestas (configurable)
- ✅ Generará un resumen al finalizar
- ✅ Guardará logs en `batch_encuestas.log`

## 📊 Logs y Capturas

El sistema genera:
- **`encuestas.log`**: Log detallado de cada encuesta
- **`batch_encuestas.log`**: Log del procesamiento en lote
- **`screenshot_*.png`**: Capturas de pantalla en caso de error o éxito
- **`resumen_*.json`**: Resumen de códigos exitosos y fallidos

## 🔍 Solución de Problemas

### Error: "No se encontró ChromeDriver"
```bash
pip install --upgrade webdriver-manager
```

### Error: "Elemento no encontrado"
- Verifica que el sitio web no haya cambiado
- Revisa las capturas de pantalla generadas
- Aumenta los delays en `config.json`

### La encuesta no se completa
- Revisa el archivo `encuestas.log` para detalles
- Ejecuta con `headless: false` para ver qué sucede
- Verifica que el código de encuesta sea válido

## 📁 Estructura de Archivos

```
ENCUESTAS/
├── encuestas.py              # Script principal
├── ejecutar_encuestas.py     # Script de procesamiento en lote
├── config.json               # Configuración
├── codigos.txt               # Lista de códigos
├── encuestas.log             # Logs individuales
├── batch_encuestas.log       # Logs en lote
└── README.md                 # Este archivo
```

## 💡 Consejos

1. **Modo Headless**: Una vez que confirmes que funciona, activa `"headless": true` para mayor velocidad
2. **Respuestas Aleatorias**: Usa `"respuestas_aleatorias": true` para variación
3. **Delays**: Ajusta los delays si el sitio es lento o para parecer más humano
4. **Lotes Pequeños**: Procesa códigos en grupos pequeños para evitar problemas

## ⚠️ Notas Importantes

- Los delays aleatorios ayudan a simular comportamiento humano
- Guarda tus códigos de respaldo en `codigos.txt`
- Revisa los logs regularmente para detectar problemas
- El sistema captura pantallas automáticamente en errores

## 🎯 Características

✨ **Automatización completa** de las 10 preguntas
✨ **Procesamiento en lote** de múltiples códigos
✨ **Configuración flexible** de respuestas
✨ **Logs detallados** para debugging
✨ **Capturas automáticas** en errores
✨ **Delays inteligentes** para parecer humano
✨ **Modo headless** para ejecución rápida

---

**¿Necesitas ayuda?** Revisa los archivos de log para más detalles sobre cualquier error.
