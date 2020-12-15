from datetime import datetime, timedelta
from django.db import models
from django.http.response import JsonResponse
import Levenshtein
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
stopwords = stopwords.words('spanish')


class ModeloBase(models.Model):
    """ Modelo base para todos los modelos del proyecto """
    status = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.fecha_modificacion = datetime.now()
        else:
            self.fecha_creacion = datetime.now()
        models.Model.save(self)

    class Meta:
        abstract = True


def validarOpciones(tamaño, lista, cantmin):
    contador = 0
    min = 0
    for list in lista:
        if list['tipo'] == "opc":
            contador += float(list['valp'])
            min += 1
    if contador == 100 and min >= cantmin:
        return True
    else:
        False


def validarImagen(imagen):
    if imagen.name.find(".") > 0:
        ext = imagen.name[imagen.name.rfind("."):]
        if ext.lower() == '.jpeg' or ext.lower() == '.jpg' or ext.lower() == '.png':
            return imagen
        else:
            return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})
    else:
        return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})


def clean_string(text):
    try:
        text = ''.join([word for word in text if word not in string.punctuation])
        text = text.lower()
        text = ' '.join([word for word in text.split() if word not in stopwords])
        return text
    except Exception as ex:
        return ex


def cosine_sim_vectors(vec1, vec2):
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]


def validarTexto():
    # Este es un método
    a = 'Hello, All you people'
    b = 'hello, all You peopl'
    c = Levenshtein.distance(a, b)
    # Este es el segundo método
    sentences = ['This is a foo bar sentence',
                 'This sentence is similar to a foo bar sentence',
                 'This is another string, but it is not quite similar to the previous ones.',
                 'I am also just another string.']

    cleaned = list(map(clean_string, sentences))
    print(cleaned)
    vectorizer = CountVectorizer().fit_transform(cleaned)
    vectors = vectorizer.toarray()
    csim = cosine_sim_vectors(vectors[2], vectors[3])
    csim
    return c


def convert_list_string(lista):
    texto = ""
    for i in lista:
        texto += i['texto'] + " "
    return texto


def similitud(sentencias, porcentaje):
    sentences = sentencias
    cleaned = list(map(clean_string, sentences))
    vectorizer = CountVectorizer().fit_transform(cleaned)
    vectors = vectorizer.toarray()
    por = porcentaje / 100
    for index in range(1, len(sentences)):
        csim = cosine_sim_vectors(vectors[0], vectors[index])
        if csim > por:
            item = {'index': index, 'csim': (csim * 100).__round__(2)}
            return item
    return False


def validarFechaHora(fecha, hora, hora2):
    hoy = datetime.today()
    print(hoy)
    if hoy.year == fecha.year:  ##es el año
        if hoy.month == fecha.month:  ## es el mes
            if hoy.day == fecha.day:  ##es el día
                hora = datetime.combine(datetime.today(), hora)
                hora2 = hora + timedelta(hours=hora2)
                if hoy.hour >= hora.hour and hoy.hour <= hora2.hour:
                    return 1
                elif hoy.hour > hora2.hour:
                    return 2
                elif hoy.hour < hora.hour:
                    return 0
            elif hoy.day > fecha.day:
                return 2
            else:
                return 0
        elif hoy.month > fecha.month:
            return 2
        else:
            return 0
    elif hoy.year > fecha.year:
        return 2
    else:
        return 0


def validarfechamayor(mayor, menor):
    if mayor.year == menor.year:
        if mayor.month == menor.month:
            if mayor.day == menor.day:
                return True
            elif mayor.day > menor.day:
                return True
            else:
                return False
        elif mayor.month > menor.month:
            return True
        else:
            return False
    elif mayor.year > menor.year:
        return True
    else:
        return False


def validarrangofechas(inicio, fin, lista):
    ban = False
    for l in lista:
        ban = False
        inicial = datetime(int(l['inicio'].split('-')[2]), int(l['inicio'].split('-')[1]),
                           int(l['inicio'].split('-')[0]))
        final = datetime(int(l['fin'].split('-')[2]), int(l['fin'].split('-')[1]), int(l['fin'].split('-')[0]))
        ban1 = validarfechamayor(inicial, inicio)
        ban2 = validarfechamayor(fin, inicial)
        ban3 = validarfechamayor(final, inicio)
        ban4 = validarfechamayor(fin, final)
        if ban1 is True and ban2 is True and ban3 is True and ban4 is True:
            ban = True
        else:
            ban = False
            break
    return ban


def validarrangofecha(fecha1, fecha2):
    if fecha1 and fecha2:
        hoy = datetime.today()
        if hoy.year >= fecha1.year and hoy.year <= fecha2.year:  ##sí se encuentra en el año
            if hoy.month >= fecha1.month and hoy.month <= fecha2.month:
                if hoy.month > fecha1.month and hoy.month < fecha2.month:
                    return True
                elif hoy.month == fecha1.month and hoy.month == fecha2.month:
                    if hoy.day >= fecha1.day and hoy.day <= fecha2.day:
                        return True
                    else:
                        return False
                elif hoy.month == fecha1.month:
                    if hoy.day >= fecha1.day:
                        return True
                    else:
                        return False
                elif hoy.month == fecha2.month:
                    if hoy.day <= fecha2.day:
                        return True
                    else:
                        return False
            else:
                return False
        else:
            return False
    else:
        return False

def validarEmparejamiento(lista):
    ban = True
    for i in lista:
        item = i['texto']
        lista = item.split(';')
        if len(lista) != 2:
            ban = False
            break
    return ban

def valiTimeDelegado(fecha, inicio, fin):
    hoy = datetime.today()
    if hoy.year == fecha.year:  ##es el año
        if hoy.month == fecha.month:  ## es el mes
            if hoy.day == fecha.day:  ##es el día
                if hoy.hour < fin.hour:
                    return True
                else:
                    if hoy.hour == fin.hour:
                        if hoy.minute <= fin.minute:
                            return True
                        else:
                            return False
                    else:
                        return False
            else:
                return False
        else:
            return False
    else:
        return False

def valiTime(fecha, inicio, fin):
    hoy = datetime.today()
    if hoy.year == fecha.year:  ##es el año
        if hoy.month == fecha.month:  ## es el mes
            if hoy.day == fecha.day:  ##es el día
                if hoy.hour >= inicio.hour and hoy.hour <= fin.hour:
                    if hoy.hour == inicio.hour:
                        if hoy.minute >= inicio.minute:
                            return True
                        else:
                            return False
                    elif hoy.hour == fin.hour:
                        if hoy.minute <= fin.minute:
                            return True
                        else:
                            return False
                    else:
                        return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False