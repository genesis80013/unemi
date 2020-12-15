from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import random
from django.db.models import Count

# Create your views here.
from seg.models import *
from seg.funciones import validarrangofecha
from seg.templatetags.auth_extras import *

@login_required(redirect_field_name='ret', login_url='/')
def view(request):
    data = {}
    data['pais'] = Pais.objects.all()
    data['numero'] = 100
    data['title'] = "Paises"
    return render(request, "holamundo.html", data)

def view_tiporeactivo(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Tipo de reactivos'
    data['tiporeactivo'] = TipoReactivo.objects.filter(status=True)
    return render(request, "adm_examencomplexivo/adm_tiporeactivo.html", data)

def view_formatoreactivo(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Formato de reactivos'
    data['formatoreactivo'] = FormatoReactivo.objects.filter(status=True)
    return render(request, "adm_examencomplexivo/adm_formatoreactivo.html", data)

def view_tipopregunta(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Tipo de pregunta'
    data['tipopregunta'] = TipoPreguntaReactivo.objects.filter(status=True)
    return render(request, "adm_examencomplexivo/adm_tipopregunta.html", data)

def view_areareactivo(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Área de reactivos'
    data['areas'] = ReactivoArea.objects.filter(status=True)
    return render(request, "adm_examencomplexivo/adm_areareactivo.html", data)

def view_cronogramaplanificacion(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Cronograma de planificación para examen complexivo'
    data['cronograma'] = CronogramaPlanificacionExamen.objects.filter(status=True)
    return render(request, "adm_examencomplexivo/adm_cronogramaplanificacion.html", data)

def view_asignacionreactivo(request):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'Cronograma de planificación para examen complexivo'
    data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
    vali = CronogramaPlanificacionExamen.objects.filter(status=True, periodo=Periodo.objects.get(activo=True)).exists()
    if vali:
        data['cronograma'] = CronogramaPlanificacionExamen.objects.get(status=True, periodo=Periodo.objects.get(activo=True))
        persona = Persona.objects.get(pk=int(user.id))
        if has_group(user, "UPA"):
            data['valigeneral'] = valig = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="GENERAL").exists()
            generales = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="GENERAL")
            data['valiespecifico'] = valie = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", grupocarrera__status=True).exists()
            especificos = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", grupocarrera__status=True)
        elif has_group(user, "COORDINADOR"):
            data['valigeneral'] = valig = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="GENERAL", persona=persona).exists()
            generales = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="GENERAL", persona=persona)
            data['valiespecifico'] = valie = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", coordinador__persona=persona, grupocarrera__status=True).exists()
            especificos = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", coordinador__persona=persona, grupocarrera__status=True)
        lista = []
        for p in generales:
            vali = validarrangofecha(p.inicio, p.fin)
            if len(lista) == 0:
                lista = [{'fila': p, 'vali': vali}]
            else:
                lista.append({'fila': p, 'vali': vali})
        data['generales'] = lista
        lista = []
        for p in especificos:
            vali = validarrangofecha(p.inicio, p.fin)
            if p.grupocarrera.activocarrera:
                mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=p.grupocarrera)
                tipo = "carrera"
            else:
                mallas = p.grupomalla
                tipo = "malla"
            if len(lista) == 0:
                lista = [{'fila': p, 'vali': vali, 'mallas': mallas, 'tipo': tipo}]
            else:
                lista.append({'fila': p, 'vali': vali, 'mallas': mallas, 'tipo': tipo})
        data['especificos'] = lista
    return render(request, "cord_examencomplexivo/adm_asignacionreactivo.html", data)

def view_reactivo(request):
    data = {}
    data['user'] = user = request.session['user']
    data['periodos'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
    cronograma = CronogramaPlanificacionExamen.objects.filter(periodo__activo=True, status=True).exists()
    periodo = Periodo.objects.filter(status=True, activo=True).exists()
    title = 'Cronograma de examen complexivo'
    if cronograma and periodo:
        periodo = Periodo.objects.get(status=True, activo=True)
        cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=periodo)
        data['title'] = cronograma.nombre
        persona = Persona.objects.get(pk=int(user.id))
        if has_group(user, "UPA"):
            data['valigeneral'] = valigeneral = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, formato__formatoreactivo__tiporeactivo__nombre="GENERAL").order_by('area__nombre', 'persona__apellido1', 'persona__apellido2', 'persona__nombres').exists()
            data['valiespecifico'] = valiespecifico = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO").exists()
        elif has_group(user, 'DOCENTE'):
            docente = Profesor.objects.get(status=True, persona=persona)
            data['valigeneral'] = valigeneral = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, persona=persona, formato__formatoreactivo__tiporeactivo__nombre="GENERAL").order_by('area__nombre').exists()
            data['valiespecifico'] = valiespecifico = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, docente=docente, formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO").exists()
        if valigeneral:
            lista = []
            if has_group(user, "DOCENTE"):
                generales = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, persona=persona, formato__formatoreactivo__tiporeactivo__nombre="GENERAL").order_by('estadofinal','area__nombre')
            elif has_group(user, "UPA"):
                generales = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, formato__formatoreactivo__tiporeactivo__nombre="GENERAL").order_by('estadofinal', 'area__nombre', 'persona__apellido1', 'persona__apellido2', 'persona__nombres')
            for p in generales:
                vali = validarrangofecha(p.inicio, p.fin)
                reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=p, estadofinal=False).count()
                count = ReactivoDocente.objects.filter(status=True, asignaciondocente=p).count()
                if len(lista) == 0:
                    lista = [{'fila': p, 'vali': vali, 'observaciones': reactivos, 'count': count}]
                else:
                    lista.append({'fila': p, 'vali': vali, 'observaciones': reactivos, 'count': count})
            data['generales'] = lista
        if valiespecifico:
            lista = []
            if has_group(user, "DOCENTE"):
                especificos = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, docente=docente, formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO").order_by('estadofinal','asignacion__grupocarrera__grupofacultad', 'asignacion__grupocarrera', 'asignatura__nivelmalla', 'asignatura')
            elif has_group(user, "UPA"):
                especificos = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion__periodo=periodo, formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO").order_by('estadofinal', 'asignacion__grupocarrera__grupofacultad', 'asignacion__grupocarrera', 'asignatura__nivelmalla', 'asignatura', 'docente__persona__apellido1', 'docente__persona__apellido2', 'docente__persona__nombres')
            for p in especificos:
                vali = validarrangofecha(p.inicio, p.fin)
                reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=p, estadofinal=False).count()
                count = ReactivoDocente.objects.filter(status=True, asignaciondocente=p).count()
                if len(lista) == 0:
                    lista = [{'fila': p, 'vali': vali, 'observaciones': reactivos, 'count': count}]
                else:
                    lista.append({'fila': p, 'vali': vali, 'observaciones': reactivos, 'count': count})
            data['especificos'] = lista
    return render(request, "doc_examencomplexivo/adm_reactivo.html", data)

def view_examencomplexivo(request, mensaje):
    data = {}
    data['user'] = user = request.session['user']
    data['title'] = 'EXAMEN COMPLEXIVO'
    data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
    persona = Persona.objects.get(pk=int(user.id))
    if has_group(user,'UPA'):
        data['examenes'] = GrupoExamenEstudiante.objects.filter(status=True, activo=True)
    else:
        data['examenes'] = GrupoExamenEstudiante.objects.filter(status=True, estudiante__inscripcion__persona=persona, activo=True)
    data['mensaje'] = mensaje
    return render(request, "est_examencomplexivo/adm_examencomplexivo.html", data)

def view_editexamencomplexivo(request, indice, reactivos, grupoestudiante):
    data = {}
    data['title'] = 'EXAMEN COMPLEXIVO'
    data['grupoestudiante'] = grupoestudiante
    data['reactivos'] = reactivos
    listopciones = []
    grupoemparejamiento = []
    data['reactivos'] = reactivos
    actual = reactivos[indice]
    atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivos[indice].bateriadetalle.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
    opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivos[indice].bateriadetalle.reactivo, atributo=None).order_by('id').values('texto', 'archivo', 'id'))
    data['maxresp'] = limites = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivos[indice].bateriadetalle.reactivo, atributo=None, activo=True).count()
    if actual.bateriadetalle.reactivo.tipopregunta.nombre != "EMPAREJAMIENTO":
        if actual.bateriadetalle.reactivo.aleatorio:
            aleatorio = random.sample(range(0, len(opciones)), len(opciones))
            listopciones = [{'texto': opciones[a]['texto'], 'archivo': opciones[a]['archivo'], 'id': opciones[a]['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivos[indice], opcion_id=opciones[a]['id']).exists()} for a in aleatorio]
            opciones = listopciones
        else:
            listopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivos[indice], opcion_id=a['id']).exists()} for a in opciones]
            opciones = listopciones
    else:
        aleatorio = random.sample(range(0, len(opciones)), len(opciones))
        index = 0
        #poner las opciones de emparejamiento en aleatorio
        grupoemparejamiento = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivos[indice], emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
        #poner las opciones
        if actual.bateriadetalle.reactivo.aleatorio:
            aleatorio = random.sample(range(0, len(opciones)), len(opciones))
            listopciones = [{'id':opciones[a]['id'], 'texto': opciones[a]['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali':False} for a in aleatorio]
        else:
            listopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali':False }for i in opciones]
        for i in listopciones:
            detalle = DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivos[indice], opcion=i['id']).exists()
            if detalle:
                i['vali'] = True
                detalle = DetalleEstudianteExamen.objects.get(status=True, reactivo=reactivos[indice], opcion=i['id'])
                texto = DetalleReactivoDocente.objects.get(pk=int(detalle.emparejamiento))
                i['id2'] = str(texto.id)
                i['texto2'] = texto.texto.split(';')[1]
        opciones = listopciones
    data['actual'] = {'reactivo': actual, 'aleatorio': actual.bateriadetalle.reactivo.aleatorio, 'tipo': actual.bateriadetalle.reactivo.tipopregunta.nombre, 'nota': actual.bateriadetalle.reactivo.nota, 'opciones': opciones, 'atributos': atributos, 'grupoemparejamiento':grupoemparejamiento}
    if indice == 0:
        data['index'] = 0
    else:
        data['index'] = indice
    if indice < len(reactivos) - 1:
        data['vali'] = True
    return render(request, 'est_examencomplexivo/edit_examencomplexivo.html', data)


