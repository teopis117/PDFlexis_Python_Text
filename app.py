from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from collections import Counter
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
import pdfplumber
import language_tool_python
import textstat

app = Flask(__name__)

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

def calcular_calificacion(indice_flesch, cantidad_de_palabras, cantidad_errores):
    # Esta es solo una propuesta para calcular la calificación, puedes ajustar la fórmula según tus necesidades.
    calificacion = (indice_flesch / 100) * (1 - (cantidad_errores / cantidad_de_palabras))
    return round(calificacion * 100, 2)  # Devuelve la calificación como un porcentaje con dos decimales.

def generar_explicacion_calificacion(calificacion):
    if calificacion >= 80:
        return "El documento tiene un buen nivel de legibilidad y pocos errores gramaticales."
    elif calificacion >= 60:
        return "El documento tiene un nivel de legibilidad adecuado pero tiene varios errores gramaticales."
    else:
        return "El documento tiene un nivel de legibilidad bajo y muchos errores gramaticales."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    archivo = request.files['archivo']
    nombre_archivo = secure_filename(archivo.filename)
    archivo.save(nombre_archivo)
    texto = ""
    with pdfplumber.open(nombre_archivo) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text()

    cantidad_de_palabras, frecuencia_de_palabras = analizador_de_texto(texto)
    num_palabras_resaltar = 10
    texto_resaltado = resaltar_palabras(texto, [palabra for palabra, _ in frecuencia_de_palabras.most_common(num_palabras_resaltar)])

    resultado = []
    for palabra, frecuencia in frecuencia_de_palabras.most_common():
        sinonimos = encontrar_sinonimos(palabra)
        resultado.append({
            'palabra': palabra,
            'frecuencia': frecuencia,
            'sinonimos': sinonimos,
            'porcentaje': 100 * frecuencia / cantidad_de_palabras,
        })
    
    # Agregamos la detección de errores gramaticales
    tool = language_tool_python.LanguageTool('es')
    errores_gramaticales = tool.check(texto)

    # Agregamos el índice de legibilidad Flesch
    indice_flesch = textstat.flesch_reading_ease(texto)
    
    # Calculamos la calificación
    calificacion = calcular_calificacion(indice_flesch, cantidad_de_palabras, len(errores_gramaticales))
    
    # Generamos la explicación de la calificación
    explicacion_calificacion = generar_explicacion_calificacion(calificacion)
    
    os.remove(nombre_archivo)
    return render_template('resultado.html', 
                           cantidad_de_palabras=cantidad_de_palabras, 
                           resultado=resultado, 
                           texto_resaltado=texto_resaltado,
                           errores_gramaticales=errores_gramaticales,
                           indice_flesch=indice_flesch,
                           calificacion=calificacion,
                           explicacion_calificacion=explicacion_calificacion)

if __name__ == '__main__':
    app.run(debug=True)
