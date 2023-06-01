from collections import Counter
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
import pdfplumber

def analizador_de_texto(texto):
    stop_words = set(stopwords.words('spanish')) 
    palabras = word_tokenize(texto.lower())
    palabras = [palabra for palabra in palabras if palabra.isalnum() and palabra not in stop_words]
    frecuencia_de_palabras = Counter(palabras)
    return len(palabras), frecuencia_de_palabras

def encontrar_sinonimos(palabra):
    sinonimos = []
    for syn in wordnet.synsets(palabra):
        for lemma in syn.lemmas():
            sinonimos.append(lemma.name())
    return sinonimos

def resaltar_palabras(texto, palabras_resaltar):
    palabras = word_tokenize(texto)
    texto_resaltado = ""
    for palabra in palabras:
        if palabra.lower() in palabras_resaltar:
            texto_resaltado += f'<mark>{palabra}</mark> '
        else:
            texto_resaltado += f'{palabra} '
    return texto_resaltado

# Solicitar al usuario el nombre del archivo a analizar
nombre_archivo = input("Por favor, introduce el nombre del archivo PDF a analizar: ")

try:
    # Leer el PDF
    with pdfplumber.open(nombre_archivo) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text()
except:
    print("Hubo un problema al abrir o leer el archivo. Por favor, asegúrate de que es un archivo PDF válido y que está en el mismo directorio que este script.")
    exit()

cantidad_de_palabras, frecuencia_de_palabras = analizador_de_texto(texto)

# Solicitar al usuario cuántas palabras más comunes resaltar
num_palabras_resaltar = int(input("¿Cuántas de las palabras más comunes te gustaría resaltar? "))

# Resaltar las palabras más comunes
texto_resaltado = resaltar_palabras(texto, [palabra for palabra, _ in frecuencia_de_palabras.most_common(num_palabras_resaltar)])

# Crear un archivo HTML con el texto resaltado y la frecuencia de las palabras
with open('resultado.html', 'w', encoding='utf-8') as f:
    f.write(f'''
    <html>
    <head>
        <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h1, h2 {{
            color: navy;
        }}
        mark {{
            background-color: yellow;
            color: black;
        }}
        .scrollable-table {{
            height: 300px;
            overflow-y: auto;
            display: block;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .progress-bar {{
            background-color: #f2f2f2;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-bar div {{
            background-color: #4CAF50;
            height: 20px;
        }}
        .resaltado {{
            background-color: #F0F8FF;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }}
        </style>
    </head>
    <body>
        <h1>Análisis de Texto</h1>
        <p>Cantidad de palabras: {cantidad_de_palabras}</p>
        <h2>Frecuencia de palabras:</h2>
        <div class="scrollable-table">
            <table>
                <tr>
                    <th>#</th>
                    <th>Palabra</th>
                    <th>Frecuencia</th>
                    <th>Sinónimos</th>
                </tr>
    ''')

    max_frecuencia = frecuencia_de_palabras.most_common(1)[0][1]
    for i, (palabra, frecuencia) in enumerate(frecuencia_de_palabras.most_common(), 1):
        porcentaje = 100 * frecuencia / max_frecuencia
        sinonimos = ", ".join(encontrar_sinonimos(palabra))
        f.write(f'''
        <tr>
            <td>{i}</td>
            <td>{palabra}</td>
            <td>
                <div class="progress-bar">
                    <div style="width: {porcentaje}%;"></div>
                </div>
                {frecuencia}
            </td>
            <td>{sinonimos}</td>
        </tr>
        ''')

    f.write(f'''
            </table>
        </div>
        <div class="resaltado">
            <h2>Texto con palabras más frecuentes resaltadas:</h2>
            <p>{texto_resaltado}</p>
        </div>
    </body>
    </html>
    ''')

