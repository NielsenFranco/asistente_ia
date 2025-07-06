import os
import sys
import tkinter as tk
from dotenv import load_dotenv
import google.generativeai as genai
import pyttsx3
from PIL import Image, ImageTk, ImageSequence
import threading
import speech_recognition as sr

# 🔐 Configuración de entorno
def ruta_relativa(ruta):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta)
    return os.path.join(os.path.abspath("."), ruta)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# 🎤 Voz
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("voice", "spanish")

# 🖼️ Avatar
class AvatarAnimado(tk.Label):
    def __init__(self, master, gif_path):
        self.img = Image.open(gif_path)
        self.frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(self.img)]
        super().__init__(master, image=self.frames[0], bg="#2e2e2e")
        self.index = 0
        self.animando = False

    def play(self):
        if self.animando:
            self.config(image=self.frames[self.index])
            self.index = (self.index + 1) % len(self.frames)
            self.after(100, self.play)

    def iniciar_animacion(self):
        if not self.animando:
            self.animando = True
            self.play()

    def detener_animacion(self):
        self.animando = False
        self.config(image=self.frames[0])

# 🎤 Micrófono
def escuchar_microfono():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        agregar_mensaje("🎤 Escuchando...", "sistema")
        try:
            audio = recognizer.listen(source, timeout=5)
            pregunta = recognizer.recognize_google(audio, language="es-ES")
            agregar_mensaje(pregunta, "usuario")
            threading.Thread(target=procesar_pregunta, args=(pregunta,)).start()
        except sr.UnknownValueError:
            agregar_mensaje("❌ No entendí lo que dijiste", "sistema")
        except sr.WaitTimeoutError:
            agregar_mensaje("⏳ Tiempo de espera agotado", "sistema")

# 🧠 Generar respuesta
def obtener_respuesta(pregunta):
    try:
        respuesta = model.generate_content(pregunta)
        return respuesta.text
    except Exception as e:
        return f"⚠️ Error al contactar Gemini: {e}"

# 💬 Añadir mensajes
def agregar_mensaje(texto_msg, tipo="usuario", respuesta_voz=None):
    burbuja = tk.Frame(cuerpo, bg="#1e1e1e", pady=5)
    color_fondo = "#4a90e2" if tipo == "usuario" else "#3c3c3c"
    color_texto = "#fff" if tipo == "usuario" else "#ddd"
    alineacion = tk.RIGHT if tipo == "usuario" else tk.LEFT

    texto = tk.Label(
        burbuja,
        text=texto_msg,
        wraplength=400,
        justify='left',
        font=("Arial", 11),
        bg=color_fondo,
        fg=color_texto,
        padx=10,
        pady=5
    )
    texto.pack(side=alineacion, padx=5)

    if tipo == "asistente" and respuesta_voz:
        icono_play = Image.open(ruta_relativa("assets/altavoz.png")).resize((20, 20), Image.LANCZOS)
        icono_pause = Image.open(ruta_relativa("assets/pause.png")).resize((20, 20), Image.LANCZOS)
        icono_play_tk = ImageTk.PhotoImage(icono_play)
        icono_pause_tk = ImageTk.PhotoImage(icono_pause)

        estado = {
            "hablando": False,
            "hilo": None,
            "interrumpido": False
        }

        def hablar():
            estado["hablando"] = True
            estado["interrumpido"] = False
            avatar.iniciar_animacion()
            btn_voz.config(image=icono_pause_tk)
            try:
                engine.say(respuesta_voz)
                engine.runAndWait()
            except:
                pass
            estado["hablando"] = False
            avatar.detener_animacion()
            btn_voz.config(image=icono_play_tk)

        def toggle_voz():
            if estado["hablando"]:
                # Si está hablando, se interrumpe
                estado["interrumpido"] = True
                engine.stop()
                avatar.detener_animacion()
                estado["hablando"] = False
                btn_voz.config(image=icono_play_tk)
            else:
                if estado["hilo"] and estado["hilo"].is_alive():
                    estado["interrumpido"] = True
                    engine.stop()
                    estado["hilo"].join(timeout=0.1)
                estado["hilo"] = threading.Thread(target=hablar)
                estado["hilo"].start()

        btn_voz = tk.Button(
            burbuja,
            image=icono_play_tk,
            command=toggle_voz,
            bg=color_fondo,
            activebackground=color_fondo,
            bd=0
        )
        btn_voz.image = icono_play_tk
        btn_voz.pack(side=tk.RIGHT, padx=5)

    burbuja.pack(anchor='e' if tipo == "usuario" else 'w', fill=tk.X, padx=10)
    canvas.yview_moveto(1)

# 🔁 Procesar pregunta
def procesar_pregunta(pregunta):
    respuesta = obtener_respuesta(pregunta)
    agregar_mensaje(respuesta, "asistente", respuesta)

# ⌨️ Enviar por texto
def enviar_texto(event=None):
    pregunta = entrada.get().strip()
    if pregunta:
        agregar_mensaje(pregunta, "usuario")
        entrada.delete(0, tk.END)
        threading.Thread(target=procesar_pregunta, args=(pregunta,)).start()

# 🎨 Interfaz general
ventana = tk.Tk()
ventana.title("CatMini")
ventana.geometry("600x760")
ventana.resizable(False, False)
ventana.configure(bg="#1e1e1e")
ventana.iconbitmap(ruta_relativa("assets/icono.ico"))

# Header
header = tk.Frame(ventana, bg="#2e2e2e")
header.pack(fill=tk.X)

logo_frame = tk.Frame(header, bg="#2e2e2e")
logo_frame.pack(pady=5)

icono_img = Image.open(ruta_relativa("assets/icono.ico")).resize((24, 24), Image.LANCZOS)
icono_tk = ImageTk.PhotoImage(icono_img)

logo_icon = tk.Label(logo_frame, image=icono_tk, bg="#2e2e2e")
logo_icon.image = icono_tk
logo_icon.pack(side=tk.LEFT, padx=5)

logo_text = tk.Label(logo_frame, text="CatMini", font=("Arial", 14, "bold"), fg="#fff", bg="#2e2e2e")
logo_text.pack(side=tk.LEFT)

avatar = AvatarAnimado(header, ruta_relativa("assets/avatar.gif"))
avatar.pack(pady=5)

# Cuerpo
cuerpo_frame = tk.Frame(ventana, bg="#1e1e1e")
cuerpo_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(cuerpo_frame, bg="#1e1e1e", bd=0, highlightthickness=0)
scroll = tk.Scrollbar(cuerpo_frame, command=canvas.yview)
cuerpo = tk.Frame(canvas, bg="#1e1e1e")

cuerpo.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=cuerpo, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

# Footer
footer = tk.Frame(ventana, bg="#2e2e2e", pady=5)
footer.pack(fill=tk.X)

entrada = tk.Entry(footer, font=("Arial", 12), bg="#3c3c3c", fg="#fff", insertbackground="#fff")
entrada.pack(side=tk.LEFT, padx=(10, 5), pady=10, fill=tk.X, expand=True)
entrada.bind("<Return>", enviar_texto)

btn_hablar = tk.Button(
    footer,
    text="🎤 Hablar",
    font=("Arial", 11),
    command=escuchar_microfono,
    bg="#4a90e2",
    fg="#fff",
    activebackground="#367bd4",
    relief=tk.FLAT,
    padx=10,
    pady=5
)
btn_hablar.pack(side=tk.RIGHT, padx=10)

ventana.mainloop()
