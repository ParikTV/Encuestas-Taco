import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import datetime
import time
import os
from encuestas import EncuestaAutomatizador

# --- COLORES ---
COLOR_FONDO = "#f0f0f0"
COLOR_PRIMARIO = "#702082" 
COLOR_SECUNDARIO = "#4F4F4F"
COLOR_BLANCO = "#FFFFFF"

class EncuestasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TacoBot - Modo VPN Controlado")
        self.root.geometry("1100x750")
        self.root.configure(bg=COLOR_FONDO)
        
        self.codigos = []
        self.indice_actual = 0
        self.automatizador_actual = None 
        
        self.crear_interfaz()
        self.cargar_codigos_automatico()

    def crear_interfaz(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Primary.TButton", font=('Segoe UI', 10, 'bold'), background=COLOR_PRIMARIO, foreground=COLOR_BLANCO)
        style.configure("Success.TButton", font=('Segoe UI', 10, 'bold'), background="#28a745", foreground=COLOR_BLANCO)
        
        # Header
        header = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🌮 TACOBOT v3.2 - CON PAUSA PARA VPN", bg=COLOR_PRIMARIO, fg=COLOR_BLANCO, font=('Segoe UI', 16, 'bold')).pack(pady=15)

        # Contenedor
        main = tk.Frame(self.root, bg=COLOR_FONDO)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left = tk.Frame(main, bg=COLOR_FONDO); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        right = tk.Frame(main, bg=COLOR_FONDO); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,0))

        # --- IZQUIERDA: Generador ---
        gen_frame = tk.LabelFrame(left, text=" Generador ", bg=COLOR_BLANCO, font=('Segoe UI', 11, 'bold'))
        gen_frame.pack(fill=tk.X, pady=(0,15))
        
        inputs_frame = tk.Frame(gen_frame, bg=COLOR_BLANCO)
        inputs_frame.pack(fill=tk.X, pady=10, padx=10)

        tk.Label(inputs_frame, text="Iniciar en #:", bg=COLOR_BLANCO).pack(side=tk.LEFT)
        self.spin_inicio = ttk.Spinbox(inputs_frame, from_=1, to=999, width=5)
        self.spin_inicio.set(1)
        self.spin_inicio.pack(side=tk.LEFT, padx=(5, 15))

        tk.Label(inputs_frame, text="Cantidad:", bg=COLOR_BLANCO).pack(side=tk.LEFT)
        self.spin_cant = ttk.Spinbox(inputs_frame, from_=1, to=100, width=5)
        self.spin_cant.set(10)
        self.spin_cant.pack(side=tk.LEFT, padx=5)

        ttk.Button(inputs_frame, text="Generar", style="Primary.TButton", command=self.generar).pack(side=tk.LEFT, padx=15)

        # Lista
        list_frame = tk.LabelFrame(left, text=" Lista ", bg=COLOR_BLANCO)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.lista_box = tk.Listbox(list_frame, font=('Consolas', 10), bg="#F9F9F9", selectbackground=COLOR_PRIMARIO)
        self.lista_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- DERECHA: Control ---
        ctrl_frame = tk.LabelFrame(right, text=" Panel de Control ", bg=COLOR_BLANCO, font=('Segoe UI', 11, 'bold'))
        ctrl_frame.pack(fill=tk.X, pady=(0,15))
        
        # Info Estado
        self.lbl_estado = tk.Label(ctrl_frame, text="LISTO PARA INICIAR", bg=COLOR_BLANCO, fg=COLOR_SECUNDARIO, font=('Segoe UI', 12, 'bold'))
        self.lbl_estado.pack(pady=10)
        self.lbl_codigo = tk.Label(ctrl_frame, text="---", bg=COLOR_BLANCO, fg=COLOR_PRIMARIO, font=('Consolas', 16, 'bold'))
        self.lbl_codigo.pack(pady=5)
        
        # Botones Principales
        self.btn_iniciar = tk.Button(ctrl_frame, text="1. ABRIR NAVEGADOR (GOOGLE)", bg=COLOR_PRIMARIO, fg="white", font=('Segoe UI', 10, 'bold'), 
                                   command=self.paso_1_abrir, height=2)
        self.btn_iniciar.pack(fill=tk.X, padx=20, pady=5)
        
        self.btn_continuar = tk.Button(ctrl_frame, text="2. ✅ YA ACTIVÉ VPN - CONTINUAR", bg="#28a745", fg="white", font=('Segoe UI', 10, 'bold'),
                                     command=self.paso_2_encuesta, height=2, state='disabled')
        self.btn_continuar.pack(fill=tk.X, padx=20, pady=5)

        self.btn_siguiente = tk.Button(ctrl_frame, text="3. ⏭ CERRAR Y SIGUIENTE ENCUESTA", bg=COLOR_SECUNDARIO, fg="white", font=('Segoe UI', 10, 'bold'),
                                     command=self.siguiente_ciclo, height=2, state='disabled')
        self.btn_siguiente.pack(fill=tk.X, padx=20, pady=5)

        # Logs
        log_frame = tk.LabelFrame(right, text=" Logs ", bg=COLOR_BLANCO)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- GENERADOR ---
    def generar(self):
        try:
            cant = int(self.spin_cant.get())
            inicio = int(self.spin_inicio.get())
            tienda, fecha, relleno = "64", datetime.datetime.now().strftime("%d%m%y"), "0101"
            self.codigos = [f"{tienda}{fecha}{relleno}{i:02d}" for i in range(inicio, inicio + cant)]
            with open("codigos.txt", "w") as f: f.write("\n".join(self.codigos))
            self.actualizar_lista()
            self.log(f"Generados {cant} códigos (Inicia en {inicio}).", "success")
        except: pass

    def actualizar_lista(self):
        self.lista_box.delete(0, tk.END)
        for c in self.codigos: self.lista_box.insert(tk.END, c)

    def cargar_codigos_automatico(self):
        if os.path.exists("codigos.txt"):
            with open("codigos.txt", "r") as f: self.codigos = [l.strip() for l in f if l.strip()]
            self.actualizar_lista()

    def log(self, msg, tipo="info"):
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)

    # --- FLUJO DE CONTROL ---
    
    # PASO 1: Abrir navegador en Google
    def paso_1_abrir(self):
        if not self.codigos: return
        
        # Si ya terminamos la lista
        if self.indice_actual >= len(self.codigos):
            messagebox.showinfo("Fin", "No hay más códigos.")
            return

        codigo = self.codigos[self.indice_actual]
        self.lbl_codigo.config(text=codigo)
        self.lbl_estado.config(text="ABRIENDO NAVEGADOR...", fg="orange")
        self.btn_iniciar.config(state='disabled')
        
        # Visual
        self.lista_box.selection_clear(0, tk.END)
        self.lista_box.selection_set(self.indice_actual)
        self.lista_box.see(self.indice_actual)

        threading.Thread(target=self.hilo_abrir, args=(codigo,), daemon=True).start()

    def hilo_abrir(self, codigo):
        self.log(f"Iniciando: {codigo}")
        self.automatizador_actual = EncuestaAutomatizador(codigo)
        
        exito = self.automatizador_actual.abrir_navegador_en_google()
        
        if exito:
            self.root.after(0, self.ui_esperar_vpn)
        else:
            self.log("❌ Error al abrir navegador.", "error")
            self.root.after(0, lambda: self.btn_iniciar.config(state='normal'))

    def ui_esperar_vpn(self):
        self.lbl_estado.config(text="⚠️ ESPERANDO VPN ⚠️", fg="red")
        self.log("👉 Navegador abierto en Google. ACTIVA TU VPN AHORA.")
        self.log("👉 Cuando estés listo, presiona el botón verde.")
        self.btn_continuar.config(state='normal', bg="#28a745")

    # PASO 2: Ejecutar Encuesta
    def paso_2_encuesta(self):
        self.btn_continuar.config(state='disabled')
        self.lbl_estado.config(text="HACIENDO ENCUESTA...", fg="blue")
        threading.Thread(target=self.hilo_encuesta, daemon=True).start()

    def hilo_encuesta(self):
        self.log("Iniciando llenado de encuesta...")
        # Llama a la segunda parte del script
        res = self.automatizador_actual.ejecutar_logica_encuesta()
        
        if res:
            self.log("✅ Encuesta finalizada.", "success")
            self.root.after(0, lambda: self.ui_fin_encuesta(True))
        else:
            self.log("❌ Falló la encuesta.", "error")
            self.root.after(0, lambda: self.ui_fin_encuesta(False))

    def ui_fin_encuesta(self, exito):
        if exito:
            self.lbl_estado.config(text="VALIDAR CÓDIGO", fg="purple")
            self.log("👉 Valida el código en pantalla.")
        else:
            self.lbl_estado.config(text="ERROR - REVISAR", fg="red")
        
        self.btn_siguiente.config(state='normal')

    # PASO 3: Cerrar y Siguiente
    def siguiente_ciclo(self):
        # 1. Cerrar navegador viejo
        if self.automatizador_actual:
            self.log("Cerrando navegador anterior...", "info")
            self.automatizador_actual.cerrar_navegador()
            self.automatizador_actual = None
        
        # 2. Resetear botones
        self.btn_siguiente.config(state='disabled')
        self.btn_iniciar.config(state='normal')
        
        # 3. Mover índice
        self.indice_actual += 1
        
        # 4. Chequear fin
        if self.indice_actual >= len(self.codigos):
            self.lbl_estado.config(text="LISTA TERMINADA", fg="green")
            self.lbl_codigo.config(text="---")
            messagebox.showinfo("Listo", "Se completaron todos los códigos.")
        else:
            self.lbl_estado.config(text="LISTO PARA LA SIGUIENTE", fg=COLOR_SECUNDARIO)
            self.lbl_codigo.config(text="---")
            # Opcional: Auto-click en iniciar si quieres, pero mejor manual
            # self.paso_1_abrir() 

def main():
    root = tk.Tk()
    app = EncuestasGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()