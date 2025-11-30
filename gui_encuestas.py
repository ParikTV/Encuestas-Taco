import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from encuestas import EncuestaAutomatizador
import time

class EncuestasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizador de Encuestas Taco Bell")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.codigos = []
        self.indice_actual = 0
        self.encuesta_en_proceso = False
        self.automatizador_actual = None
        
        self.crear_interfaz()
        self.cargar_codigos_automatico()
    
    def crear_interfaz(self):
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🌮 AUTOMATIZADOR DE ENCUESTAS TACO BELL", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)
        
        # Archivo de códigos
        ttk.Label(config_frame, text="Archivo de códigos:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.archivo_entry = ttk.Entry(config_frame, width=40)
        self.archivo_entry.insert(0, "codigos.txt")
        self.archivo_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(config_frame, text="Examinar", command=self.seleccionar_archivo).grid(row=0, column=2, padx=5)
        ttk.Button(config_frame, text="Cargar", command=self.cargar_codigos).grid(row=0, column=3, padx=5)
        
        # Códigos cargados
        ttk.Label(config_frame, text="Códigos cargados:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.codigos_label = ttk.Label(config_frame, text="0 códigos", foreground="gray")
        self.codigos_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Seleccionar código de inicio
        ttk.Label(config_frame, text="Comenzar desde:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.inicio_combo = ttk.Combobox(config_frame, state="readonly", width=37)
        self.inicio_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Frame de progreso
        progreso_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progreso_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        progreso_frame.columnconfigure(1, weight=1)
        
        # Estado actual
        ttk.Label(progreso_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.estado_label = ttk.Label(progreso_frame, text="Esperando inicio", foreground="blue", font=('Arial', 10, 'bold'))
        self.estado_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Código actual
        ttk.Label(progreso_frame, text="Código actual:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.codigo_actual_label = ttk.Label(progreso_frame, text="---", font=('Courier', 12, 'bold'))
        self.codigo_actual_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Progreso
        ttk.Label(progreso_frame, text="Progreso:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.progreso_label = ttk.Label(progreso_frame, text="0 / 0")
        self.progreso_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progreso_frame, mode='determinate')
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Botones
        self.btn_iniciar = ttk.Button(controles_frame, text="▶ Iniciar Encuesta", 
                                      command=self.iniciar_encuesta, width=20)
        self.btn_iniciar.grid(row=0, column=0, padx=5)
        
        self.btn_siguiente = ttk.Button(controles_frame, text="⏭ Siguiente Encuesta", 
                                       command=self.siguiente_encuesta, state='disabled', width=20)
        self.btn_siguiente.grid(row=0, column=1, padx=5)
        
        self.btn_detener = ttk.Button(controles_frame, text="⏹ Detener", 
                                      command=self.detener, state='disabled', width=20)
        self.btn_detener.grid(row=0, column=2, padx=5)
        
        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="Registro de Actividad", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de texto para log
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, 
                                                  font=('Courier', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón limpiar log
        ttk.Button(log_frame, text="Limpiar Log", command=self.limpiar_log).grid(row=1, column=0, pady=5)
        
        # Footer
        footer = ttk.Label(main_frame, text="Desarrollado para automatización de encuestas • v2.0", 
                          foreground="gray", font=('Arial', 8))
        footer.grid(row=5, column=0, columnspan=3, pady=5)
    
    def log(self, mensaje, tipo="info"):
        """Agregar mensaje al log con timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        
        if tipo == "error":
            prefijo = "[ERROR]"
            color = "red"
        elif tipo == "success":
            prefijo = "[OK]"
            color = "green"
        elif tipo == "warning":
            prefijo = "[ADVERTENCIA]"
            color = "orange"
        else:
            prefijo = "[INFO]"
            color = "black"
        
        mensaje_completo = f"[{timestamp}] {prefijo} {mensaje}\n"
        
        self.log_text.insert(tk.END, mensaje_completo)
        self.log_text.see(tk.END)
        
        # Aplicar color (solo en GUI)
        if tipo != "info":
            start_idx = self.log_text.index("end-2c linestart")
            end_idx = self.log_text.index("end-1c")
            self.log_text.tag_add(tipo, start_idx, end_idx)
            self.log_text.tag_config(tipo, foreground=color)
    
    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de códigos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.archivo_entry.delete(0, tk.END)
            self.archivo_entry.insert(0, archivo)
    
    def cargar_codigos_automatico(self):
        """Intenta cargar códigos automáticamente al inicio"""
        try:
            with open("codigos.txt", 'r', encoding='utf-8') as f:
                self.codigos = [linea.strip() for linea in f if linea.strip()]
            
            if self.codigos:
                self.actualizar_lista_codigos()
                self.log(f"Cargados {len(self.codigos)} códigos desde codigos.txt", "success")
        except FileNotFoundError:
            self.log("No se encontró codigos.txt - use el botón Cargar", "warning")
    
    def cargar_codigos(self):
        archivo = self.archivo_entry.get()
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                self.codigos = [linea.strip() for linea in f if linea.strip()]
            
            if not self.codigos:
                messagebox.showwarning("Sin códigos", "El archivo no contiene códigos válidos")
                return
            
            self.actualizar_lista_codigos()
            self.log(f"Cargados {len(self.codigos)} códigos desde {archivo}", "success")
            messagebox.showinfo("Éxito", f"Se cargaron {len(self.codigos)} códigos correctamente")
            
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo: {archivo}")
            self.log(f"Error: archivo no encontrado - {archivo}", "error")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar códigos: {e}")
            self.log(f"Error al cargar códigos: {e}", "error")
    
    def actualizar_lista_codigos(self):
        self.codigos_label.config(text=f"{len(self.codigos)} códigos", foreground="green")
        
        # Actualizar combobox con opciones
        opciones = [f"{i+1}. {codigo}" for i, codigo in enumerate(self.codigos)]
        self.inicio_combo['values'] = opciones
        if opciones:
            self.inicio_combo.current(0)
    
    def iniciar_encuesta(self):
        if not self.codigos:
            messagebox.showwarning("Sin códigos", "Primero debe cargar códigos desde un archivo")
            return
        
        # Obtener índice seleccionado
        seleccion = self.inicio_combo.current()
        if seleccion == -1:
            messagebox.showwarning("Selección requerida", "Seleccione desde qué código iniciar")
            return
        
        self.indice_actual = seleccion
        self.encuesta_en_proceso = True
        
        # Actualizar UI
        self.btn_iniciar.config(state='disabled')
        self.btn_siguiente.config(state='disabled')
        self.btn_detener.config(state='normal')
        self.inicio_combo.config(state='disabled')
        
        # Ejecutar en thread separado
        threading.Thread(target=self.ejecutar_encuesta_actual, daemon=True).start()
    
    def ejecutar_encuesta_actual(self):
        if self.indice_actual >= len(self.codigos):
            self.root.after(0, self.encuestas_completadas)
            return
        
        codigo = self.codigos[self.indice_actual]
        
        # Actualizar UI
        self.root.after(0, lambda: self.actualizar_progreso(codigo))
        
        try:
            self.log(f"Iniciando encuesta para código: {codigo}", "info")
            
            automatizador = EncuestaAutomatizador(codigo)
            resultado = automatizador.ejecutar()
            
            if resultado:
                self.log(f"Encuesta {codigo} completada exitosamente", "success")
                self.root.after(0, self.encuesta_completada)
            else:
                self.log(f"Error en encuesta {codigo}", "error")
                self.root.after(0, self.encuesta_con_error)
                
        except Exception as e:
            self.log(f"Error crítico: {e}", "error")
            self.root.after(0, self.encuesta_con_error)
    
    def actualizar_progreso(self, codigo):
        self.codigo_actual_label.config(text=codigo)
        self.progreso_label.config(text=f"{self.indice_actual + 1} / {len(self.codigos)}")
        
        progreso_porcentaje = ((self.indice_actual + 1) / len(self.codigos)) * 100
        self.progress_bar['value'] = progreso_porcentaje
        
        self.estado_label.config(text="Procesando encuesta...", foreground="orange")
    
    def encuesta_completada(self):
        self.estado_label.config(text="Encuesta completada - Presione 'Siguiente'", foreground="green")
        self.btn_siguiente.config(state='normal')
        self.btn_detener.config(state='disabled')
    
    def encuesta_con_error(self):
        self.estado_label.config(text="Error en encuesta - Presione 'Siguiente'", foreground="red")
        self.btn_siguiente.config(state='normal')
        self.btn_detener.config(state='disabled')
    
    def siguiente_encuesta(self):
        self.indice_actual += 1
        
        if self.indice_actual >= len(self.codigos):
            self.encuestas_completadas()
            return
        
        # Deshabilitar botón y ejecutar siguiente
        self.btn_siguiente.config(state='disabled')
        self.btn_detener.config(state='normal')
        
        threading.Thread(target=self.ejecutar_encuesta_actual, daemon=True).start()
    
    def encuestas_completadas(self):
        self.log("Todas las encuestas han sido completadas", "success")
        self.estado_label.config(text="Todas las encuestas completadas", foreground="blue")
        
        self.btn_iniciar.config(state='normal')
        self.btn_siguiente.config(state='disabled')
        self.btn_detener.config(state='disabled')
        self.inicio_combo.config(state='readonly')
        
        self.progress_bar['value'] = 100
        
        messagebox.showinfo("Completado", 
                          f"Se completaron todas las encuestas!\n\n"
                          f"Total procesadas: {len(self.codigos)}")
    
    def detener(self):
        respuesta = messagebox.askyesno("Confirmar", 
                                       "¿Está seguro de detener el proceso?\n\n"
                                       "La encuesta actual se perderá.")
        if respuesta:
            self.encuesta_en_proceso = False
            self.log("Proceso detenido por el usuario", "warning")
            
            self.btn_iniciar.config(state='normal')
            self.btn_siguiente.config(state='disabled')
            self.btn_detener.config(state='disabled')
            self.inicio_combo.config(state='readonly')
            
            self.estado_label.config(text="Detenido", foreground="red")


def main():
    root = tk.Tk()
    app = EncuestasGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()