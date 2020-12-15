import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import JsonResponse
from seg.forms import *
from seg.models import *
from seg.views import *
from django.db.models import Sum
from django.db import transaction
from django.http import Http404
from seg.funciones import validarfechamayor, validarrangofechas
from random import sample


#@login_required(redirect_field_name='ret', login_url='/')
@transaction.atomic()
def view(request):
    data = {}
    data['permite_modificar'] = True
    if request.method == 'POST':
        if 'user' in request.session:
            if 'action' in request.POST:
                action = request.POST['action']
                user = request.session['user']
                if action == 'add_pais':
                    try:
                        vali = PaisForm(request.POST, request.FILES)
                        if vali.is_valid():
                            pais = Pais(nombre=vali.cleaned_data['nombre'],
                                        estado=vali.cleaned_data['estado'])
                            pais.save()
                            if 'imagen' in request.FILES:
                                foto = request.FILES['imagen']
                                if foto.name.find(".") > 0:
                                    ext = foto.name[foto.name.rfind("."):]
                                else:
                                    return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})
                                foto.name = "imagen_pais_%s_%s" % (pais.id, ext)
                                pais.imagen = foto
                                pais.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_pais':
                    try:
                        vali = PaisForm(request.POST, request.FILES)
                        if vali.is_valid():
                            pais = Pais.objects.get(pk=int(request.POST['id']))
                            pais.nombre = vali.cleaned_data['nombre']
                            pais.estado = vali.cleaned_data['estado']
                            if 'imagen' in request.FILES:
                                foto = request.FILES['imagen']
                                if foto.name.find(".") > 0:
                                    ext = foto.name[foto.name.rfind("."):]
                                else:
                                    return JsonResponse({"result": "error",
                                                         "mensaje": 'No es un archivo valido.'})
                                foto.name = "imagen_pais_%s_%s" % (pais.id, ext)
                                pais.imagen = foto
                            pais.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error",
                                                 "mensaje": 'datos erroneos en el formulario. %s' % vali._errors})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error",
                                             "mensaje": 'Ocurrio un problema contacte con el administrador. %s' % ex})
                elif action == 'del_pais':
                    try:
                        pais = Pais.objects.get(pk=int(request.POST['id']))
                        pais.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_tiporeactivo':
                    try:
                        vali = TipoReactivoForm(request.POST, request.FILES)
                        if vali.is_valid():
                            tipo = TipoReactivo(nombre=vali.cleaned_data['nombre'],
                                        estado=vali.cleaned_data['estado'])
                            tipo.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_tiporeactivo':
                    try:
                        vali = TipoReactivoForm(request.POST, request.FILES)
                        if vali.is_valid():
                            tipo = TipoReactivo.objects.get(pk=int(request.POST['id']))
                            tipo.nombre = vali.cleaned_data['nombre']
                            tipo.estado = vali.cleaned_data['estado']
                            tipo.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_tiporeactivo':
                    try:
                        tipo = TipoReactivo.objects.get(pk=int(request.POST['id']))
                        tipo.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_formatoreactivo':
                    try:
                        vali = FormatoReactivoForm(request.POST, request.FILES)
                        lista = request.POST['valilista']
                        if vali.is_valid():
                            persona = Persona.objects.get(pk=int(user.id))
                            profe = Profesor.objects.get(status=True, persona=persona)
                            if lista == '0':
                                return JsonResponse({"result": "error", "mensaje": 'no hay campos para el formato.'})
                            else:
                                formato = FormatoReactivo(
                                    nombre=vali.cleaned_data['nombre'],
                                    profesor=profe,
                                    descripcion=vali.cleaned_data['descripcion'],
                                    opcionesmin=vali.cleaned_data['opcionesmin'],
                                    opcionesmax=vali.cleaned_data['opcionesmax'],
                                    respuestasmin=vali.cleaned_data['respuestasmin'],
                                    respuestasmax=vali.cleaned_data['respuestasmax'],
                                    notamin=vali.cleaned_data['notamin'],
                                    notamax=vali.cleaned_data['notamax'],
                                    tiporeactivo=vali.cleaned_data['tiporeactivo'],
                                    estado=vali.cleaned_data['estado'],
                                    valiopciones=vali.cleaned_data['valiopciones']
                                )
                                aux = FormatoReactivo.objects.filter(tiporeactivo=formato.tiporeactivo,estado=True, status=True).exists()
                                if aux and formato.estado == True:
                                    return JsonResponse({"result": "error", "mensaje": 'Ya existe un formato activo para ' + formato.tiporeactivo.nombre})
                                else:
                                    formato.save()
                                    campos = json.loads(request.POST['lista_items1'])
                                    for campo in campos:
                                        if campo['estvisible']=='1':
                                            estuvisible = True
                                        else:
                                            estuvisible = False
                                        if campo['docvisible']=='1':
                                            docvisible = True
                                        else:
                                            docvisible = False
                                        atributo = AtributoReactivo(formatoreactivo=formato, nombre=campo['nombre'], detalle=campo['detalle'], estuvisible=estuvisible, profvisible=docvisible, estado=True)
                                        atributo.save()
                                    if 'archivo' in request.FILES:
                                        archivo = request.FILES['archivo']
                                        if archivo.name.find(".") > 0:
                                            ext = archivo.name[archivo.name.rfind("."):]
                                        else:
                                            return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})
                                        archivo.name = "archivo_formato_%s_%s" % (formato.id, ext)
                                        formato.archivo = archivo
                                        formato.save()
                                return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_formatoreactivo':
                    try:
                        vali = FormatoReactivoForm(request.POST, request.FILES)
                        lista = request.POST['valilista']
                        if vali.is_valid():
                            persona = Persona.objects.get(pk=int(user.id))
                            profe = Profesor.objects.get(status=True, persona=persona)
                            if lista == '0':
                                return JsonResponse({"result": "error", "mensaje": 'no hay campos para el formato.'})
                            else:
                                formato = FormatoReactivo.objects.get(pk=int(request.POST['id']))
                                formato.nombre = vali.cleaned_data['nombre']
                                formato.profesor = profe
                                formato.descripcion = vali.cleaned_data['descripcion']
                                formato.opcionesmin = vali.cleaned_data['opcionesmin']
                                formato.opcionesmax = vali.cleaned_data['opcionesmax']
                                formato.respuestasmin = vali.cleaned_data['respuestasmin']
                                formato.respuestasmax = vali.cleaned_data['respuestasmax']
                                formato.notamin = vali.cleaned_data['notamin']
                                formato.notamax = vali.cleaned_data['notamax']
                                formato.tiporeactivo = vali.cleaned_data['tiporeactivo']
                                formato.estado = vali.cleaned_data['estado']
                                formato.valiopciones = vali.cleaned_data['valiopciones']
                                aux = FormatoReactivo.objects.filter(tiporeactivo=formato.tiporeactivo, estado=True, status=True).exists()
                                if aux:
                                    aux = FormatoReactivo.objects.get(tiporeactivo=formato.tiporeactivo, estado=True, status=True)
                                    if formato.estado is True and aux.estado is True and formato.id != aux.id:
                                        return JsonResponse({"result": "error", "mensaje": 'ya existe un formato activo.'})
                                formato.save()
                                campos = json.loads(request.POST['lista_items1'])
                                for campo in campos:
                                    if campo['estvisible'] == '1':
                                        estuvisible = True
                                    else:
                                        estuvisible = False
                                    if campo['docvisible'] == '1':
                                        docvisible = True
                                    else:
                                        docvisible = False
                                    if campo['action'] == 'add':
                                        atributo = AtributoReactivo(formatoreactivo=formato, nombre=campo['nombre'], detalle=campo['detalle'], estuvisible=estuvisible, profvisible=docvisible, estado=True)
                                        atributo.save()
                                    elif campo['action'] == 'edit':
                                        atributo = AtributoReactivo.objects.get(pk=int(campo['idatr']))
                                        atributo.formatoreactivo = formato
                                        atributo.nombre = campo['nombre']
                                        atributo.detalle = campo['detalle']
                                        atributo.estuvisible = estuvisible
                                        atributo.profvisible = docvisible
                                        atributo.estado = True
                                        atributo.save()
                                    elif campo['action'] == 'del':
                                        atributo = AtributoReactivo.objects.get(pk=int(campo['idatr']))
                                        atributo.estado = False
                                        atributo.status = False
                                        atributo.save()
                                if 'archivo' in request.FILES:
                                    archivo = request.FILES['archivo']
                                    if archivo.name.find(".") > 0:
                                        ext = archivo.name[archivo.name.rfind("."):]
                                    else:
                                        return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})
                                    archivo.name = "archivo_formato_%s_%s" % (formato.id, ext)
                                    formato.archivo = archivo
                                    formato.save()
                                return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_formatoreactivo':
                    try:
                        formato = FormatoReactivo.objects.get(pk=int(request.POST['id']))
                        formato.estado = False
                        formato.status = False
                        formato.save()
                        formato.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_tipopregunta':
                    try:
                        vali = TipoPreguntaReactivoForm(request.POST)
                        if vali.is_valid():
                            tipopregunta = TipoPreguntaReactivo(nombre=vali.cleaned_data['nombre'], abreviatura=vali.cleaned_data['abreviatura'], activo=vali.cleaned_data['activo'])
                            tipopregunta.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_tipopregunta':
                    try:
                        vali = TipoPreguntaReactivoForm(request.POST)
                        if vali.is_valid():
                            tipo = TipoPreguntaReactivo.objects.get(pk=int(request.POST['id']))
                            tipo.nombre= vali.cleaned_data['nombre']
                            tipo.abreviatura= vali.cleaned_data['abreviatura']
                            tipo.activo= vali.cleaned_data['activo']
                            tipo.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_tipopregunta':
                    try:
                        tipo = TipoPreguntaReactivo.objects.get(pk=int(request.POST['id']))
                        tipo.activo = False
                        tipo.status = False
                        tipo.save()
                        tipo.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_areareactivo':
                    try:
                        vali = AreaReactivoForm(request.POST)
                        if vali.is_valid():
                            area = ReactivoArea(nombre=vali.cleaned_data['nombre'], activo=vali.cleaned_data['activo'])
                            area.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_areareactivo':
                    try:
                        vali = AreaReactivoForm(request.POST)
                        if vali.is_valid():
                            area = ReactivoArea.objects.get(pk=int(request.POST['id']))
                            area.nombre = vali.cleaned_data['nombre']
                            area.activo = vali.cleaned_data['activo']
                            area.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_areareactivo':
                    try:
                        area = ReactivoArea.objects.get(pk=int(request.POST['id']))
                        area.activo = False
                        area.status = False
                        area.save()
                        area.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'vali_cronogramaperiodo':
                    try:
                        ban = CronogramaPlanificacionExamen.objects.filter(status=True, periodo=int(request.POST['id'])).exists()
                        if ban:
                            return JsonResponse({"result": "ok", "mensaje": '1'})
                        else:
                            return JsonResponse({"result": "ok", "mensaje": '0'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_coordinadorescarrera':
                    try:
                        coordinadores = CoordinadorCarrera.objects.filter(status=True, periodo=int(request.POST['idperiodo']), carrera__facultad=int(request.POST['idfacultad'])).order_by('carrera__facultad')
                        lista = list(coordinadores.values('carrera__facultad','carrera__facultad__nombre','carrera', 'carrera__nombre', 'id', 'persona__nombres', 'persona__apellido1', 'persona__apellido2'))
                        return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_carreras':
                    try:
                        if 'idfacultad' in request.POST:
                            lista = list(Carrera.objects.filter(status=True, facultad=int(request.POST['idfacultad'])).order_by('nombre').values('id','nombre'))
                            return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_grupocarreras':
                    try:
                        if 'idfacultad' in request.POST:
                            lista = list(GrupoCarreraExamen.objects.filter(status=True, grupofacultad=int(request.POST['idfacultad'])).order_by('carrera__nombre').values('id','carrera__nombre','activocarrera', 'carrera'))
                            return JsonResponse({"result": "ok", "mensaje": lista, 'index': request.POST['index']})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_coordinadores':
                    try:
                        if 'idcarrera' in request.POST and 'idperiodo' in request.POST:
                            coordinadores = CoordinadorCarrera.objects.filter(status=True, periodo=int(request.POST['idperiodo']), carrera=int(request.POST['idcarrera'])).order_by('persona__nombres')
                            lista = list(coordinadores.values('id', 'carrera', 'carrera__nombre', 'persona__nombres', 'persona__apellido1', 'persona__apellido2'))
                        else:
                            lista = []
                        return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_mallas':
                    try:
                        if 'idcarrera' in request.POST:
                            mallas = Malla.objects.filter(status=True, carrera=int(request.POST['idcarrera']))
                            lista = list(Malla.objects.filter(status=True, carrera__id=int(request.POST['idcarrera'])).order_by('-vigente', 'nombre').values('id','nombre','vigente'))
                            return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_asignacionescarrera':
                    try:
                        if 'idcarrera' in request.POST:
                            grupocarrera = GrupoCarreraExamen.objects.get(pk=int(request.POST['idcarrera']))
                            if grupocarrera.activocarrera:
                                mallas = list(GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=grupocarrera).values('id', 'malla__id', 'malla__nombre', 'malla__vigente'))
                                if AsignacionGrupoCoordinador.objects.filter(status=True, grupocarrera=grupocarrera).exists():
                                    asignacion = AsignacionGrupoCoordinador.objects.get(status=True, grupocarrera=grupocarrera)
                                    asignacion = [{
                                        'id': asignacion.id,
                                        'carreraid': asignacion.grupocarrera.id,
                                        'carrera': asignacion.grupocarrera.carrera.nombre,
                                        'facultadid': asignacion.grupocarrera.grupofacultad.id,
                                        'facultad': asignacion.grupocarrera.grupofacultad.facultad.nombre,
                                        'grupomalla': None,
                                        'periodoid': asignacion.periodo.id,
                                        'formatoid': asignacion.formato.id,
                                        'formato': asignacion.formato.formatoreactivo.nombre,
                                        'inicio': datetime.strftime(asignacion.inicio, "%d-%m-%Y"),
                                        'fin': datetime.strftime(asignacion.fin, "%d-%m-%Y"),
                                        'activoc': asignacion.activoasignar,
                                        'bateria': asignacion.tamaniobateria,
                                        'coordinadorid': asignacion.coordinador.id,
                                        'coordinador': asignacion.coordinador.persona.nombres+' '+asignacion.coordinador.persona.apellido1+' '+asignacion.coordinador.persona.apellido2}]
                                else:
                                    asignacion = []
                                return JsonResponse({"result": "ok", "mensaje1": mallas, "mensaje": asignacion, 'tipo': "carrera"})
                            else:
                                #Cuando es por malla
                                if AsignacionGrupoCoordinador.objects.filter(status=True,grupocarrera=grupocarrera).exists():
                                    asignacion = []
                                    asig = AsignacionGrupoCoordinador.objects.filter(status=True, grupocarrera=grupocarrera)
                                    for a in asig:
                                        malla = a.grupomalla.malla.nombre
                                        if a.grupomalla.malla.vigente:
                                            malla = malla + "- VIGENTE"
                                        else:
                                            malla = malla + "- NO VIGENTE"
                                        item = {
                                            'id': a.id,
                                            'grupomallaid': a.grupomalla.id,
                                            'mallaid': a.grupomalla.malla.id,
                                            'malla': malla,
                                            'periodoid': a.periodo.id,
                                            'formatoid': a.formato.id,
                                            'formato': a.formato.formatoreactivo.nombre,
                                            'inicio': datetime.strftime(a.fin, "%d-%m-%Y"),
                                            'fin': datetime.strftime(a.fin, "%d-%m-%Y"),
                                            'activoc': a.activoasignar,
                                            'bateria': a.tamaniobateria,
                                            'coordinadorid': a.coordinador.id,
                                            'coordinador': a.coordinador.persona.nombres+' '+a.coordinador.persona.apellido1+' '+a.coordinador.persona.apellido2
                                        }
                                        if len(asignacion) == 0:
                                            asignacion = [item]
                                        else:
                                            asignacion.append(item)

                                else:
                                    asignacion = []
                                grupo = [{
                                    'id': grupocarrera.id,
                                    'carrera': grupocarrera.carrera.nombre,
                                    'activocarrera': grupocarrera.activocarrera,
                                    'facultadid': grupocarrera.grupofacultad.id,
                                    'facultad': grupocarrera.grupofacultad.facultad.nombre
                                }]
                                return JsonResponse({"result": "ok", "mensaje1": asignacion, "mensaje": grupo, 'tipo': "malla"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_cronogramaplanificacion':
                    try:
                        if request.POST['valiperiodo'] == '1':
                            return JsonResponse({"result": "error", "mensaje": 'El periodo seleccionado ya tiene un cronograma.'})
                        else:
                            if request.POST['valiformato'] == '1':
                                vali = CronogramaPlanificacionForm(request.POST)
                                if vali.is_valid():
                                    ban = validarfechamayor(vali.cleaned_data['fin'], vali.cleaned_data['inicio'])
                                    if ban:
                                        lista1 = request.POST['valilista1']
                                        lista2 = request.POST['valilista2']
                                        if lista1 == '1' and lista2 == '1':
                                            lista1 = json.loads(request.POST['lista_items1'])
                                            lista2 = json.loads(request.POST['lista_items2'])
                                            persona = Persona.objects.get(pk=int(user.id))
                                            cronograma = CronogramaPlanificacionExamen(nombre=vali.cleaned_data['nombre'], periodo=vali.cleaned_data['periodo'], persona=persona, inicio=vali.cleaned_data['inicio'], fin=vali.cleaned_data['fin'], porcsimilitud=vali.cleaned_data['porcsimilitud'])
                                            ban2 = validarrangofechas(cronograma.inicio, cronograma.fin, lista1)
                                            if ban2:
                                                cronograma.save()
                                                bateria = Bateria(cronograma=cronograma, periodo=cronograma.periodo)
                                                bateria.save()
                                                formatos = json.loads(request.POST['lista_items3'])
                                                for f in formatos:
                                                    idformato = f['idformato']
                                                    valorf = f['activo']
                                                    if valorf == 1:
                                                        formato = FormatoReactivo.objects.get(pk=int(idformato))
                                                        nombre = 'FORMATO DE ' + formato.tiporeactivo.nombre + ' PARA ' + cronograma.nombre
                                                        formato = GrupoFormatoReactivo(nombre=nombre, grupocronograma=cronograma, formatoreactivo=formato)
                                                        formato.save()
                                                for l in lista1:
                                                    profesor = Profesor.objects.get(pk=int(l['iddocente']))
                                                    persona = Persona.objects.get(pk=int(profesor.persona_id))
                                                    nombre = 'CRONOGRAMA PARA ' + cronograma.periodo.nombre
                                                    formatoreactivo = FormatoReactivo.objects.get(pk=int(l['idformato']))
                                                    formato = GrupoFormatoReactivo.objects.get(grupocronograma=cronograma, formatoreactivo=formatoreactivo)
                                                    if l['activoc'] == '1':
                                                        activoasignar = True
                                                    else:
                                                        activoasignar = False
                                                    bateria = int(l['bateria'])
                                                    inicio = datetime(int(l['inicio'].split('-')[2]),int(l['inicio'].split('-')[1]),int(l['inicio'].split('-')[0]))
                                                    fin = datetime(int(l['fin'].split('-')[2]),int(l['fin'].split('-')[1]),int(l['fin'].split('-')[0]))
                                                    asignacion = AsignacionGrupoCoordinador(nombre=nombre, periodo=cronograma.periodo, persona=persona, formato=formato, inicio=inicio, fin=fin, activoasignar=activoasignar, estadoinicial=True, estadofinal=False, tamaniobateria=bateria)
                                                    asignacion.save()
                                                for l in lista2:
                                                    facultad = Facultad.objects.get(pk=int(l['idfacultad']))
                                                    nombre = 'CRONOGRAMA PARA ' + facultad.nombre + ' EN ' + cronograma.periodo.nombre
                                                    grupo = GrupoFacultadExamen(nombre=nombre, grupocronograma=cronograma, facultad=facultad)
                                                    grupo.save()
                                                    for c in l['carreras']:
                                                        carrera = Carrera.objects.get(pk=int(c['idcarrera']))
                                                        nombre = 'CRONOGRAMA PARA ' + carrera.nombre + ' EN ' + cronograma.periodo.nombre
                                                        if c['idtipocarrera'] == "carrera":
                                                            activocarrera = True
                                                        else:
                                                            activocarrera = False
                                                        if c['idtipocarrera'] == "malla":
                                                            activomalla = True
                                                        else:
                                                            activomalla = False
                                                        grupocarrera = GrupoCarreraExamen(nombre=nombre, grupofacultad=grupo, carrera=carrera, activocarrera=activocarrera, activomalla=activomalla)
                                                        grupocarrera.save()
                                                return JsonResponse({"result": "ok"})
                                            else:
                                                return JsonResponse({"result": "error", "mensaje": 'Error en fechas para coordinadores y docentes'})
                                        else:
                                            return JsonResponse({"result": "error", "mensaje": 'Error, ingresar los coordinadores'})
                                    else:
                                        return JsonResponse({"result": "error", "mensaje": 'El rango de fechas para el cronograma es erroneo.'})
                                else:
                                    return JsonResponse( {"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                            else:
                                return JsonResponse({"result": "error", "mensaje": 'Seleccionar los formatos para reactivos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_cronogramaplanificacion':
                    try:
                        if request.POST['valiperiodo'] == '1':
                            return JsonResponse({"result": "error", "mensaje": 'El periodo seleccionado ya tiene un cronograma.'})
                        else:
                            if request.POST['valiformato'] == '1':
                                vali = CronogramaPlanificacionForm(request.POST)
                                if vali.is_valid():
                                    ban = validarfechamayor(vali.cleaned_data['fin'], vali.cleaned_data['inicio'])
                                    if ban:
                                        lista1 = request.POST['valilista1']
                                        lista2 = request.POST['valilista2']
                                        if lista1 == '1' and lista2 == '1':
                                            lista1 = json.loads(request.POST['lista_items1'])
                                            lista2 = json.loads(request.POST['lista_items2'])
                                            cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.POST['id']))
                                            fin2 = cronograma.fin
                                            cronograma.nombre = vali.cleaned_data['nombre']
                                            cronograma.inicio = vali.cleaned_data['inicio']
                                            cronograma.fin = vali.cleaned_data['fin']
                                            cronograma.porcsimilitud = vali.cleaned_data['porcsimilitud']
                                            ban2 = validarrangofechas(cronograma.inicio, cronograma.fin, lista1)
                                            if ban2:
                                                cronograma.save()
                                                formatos = json.loads(request.POST['lista_items3'])
                                                for f in formatos:
                                                    idformato = f['idformato']
                                                    valorf = f['activo']
                                                    if valorf == 1 and f['idgrupoformato']=="":
                                                        formato = FormatoReactivo.objects.get(pk=int(idformato))
                                                        nombre = 'FORMATO DE ' + formato.tiporeactivo.nombre + ' PARA ' + cronograma.nombre
                                                        formato = GrupoFormatoReactivo(nombre=nombre, grupocronograma=cronograma, formatoreactivo=formato)
                                                        formato.save()
                                                for l in lista1:
                                                    if l['action'] == 'del':
                                                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(l['idasignacion']))
                                                        asignacion.status = False
                                                        asignacion.save()
                                                    else:
                                                        profesor = Profesor.objects.get(pk=int(l['iddocente']))
                                                        persona = Persona.objects.get(pk=int(profesor.persona_id))
                                                        nombre = 'CRONOGRAMA PARA ' + cronograma.periodo.nombre
                                                        formatoreactivo = FormatoReactivo.objects.get(pk=int(l['idformato']))
                                                        formato = GrupoFormatoReactivo.objects.get(grupocronograma=cronograma, formatoreactivo=formatoreactivo)
                                                        if l['activoc'] == '1':
                                                            activoasignar = True
                                                        else:
                                                            activoasignar = False
                                                        bateria = int(l['bateria'])
                                                        inicio = datetime(int(l['inicio'].split('-')[2]), int(l['inicio'].split('-')[1]), int(l['inicio'].split('-')[0]))
                                                        fin = datetime(int(l['fin'].split('-')[2]), int(l['fin'].split('-')[1]), int(l['fin'].split('-')[0]))
                                                        if l['action'] == 'add':
                                                            asignacion = AsignacionGrupoCoordinador(nombre=nombre, periodo=cronograma.periodo, persona=persona, formato=formato, inicio=inicio, fin=fin, activoasignar=activoasignar, estadoinicial=True, estadofinal=False, tamaniobateria=bateria)
                                                            asignacion.save()
                                                        elif l['action'] == 'edit':
                                                            asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(l['idasignacion']))
                                                            asignacion.inicio = inicio
                                                            asignacion.fin = fin
                                                            asignacion.formato = formato
                                                            asignacion.persona = persona
                                                            asignacion.tamaniobateria = bateria
                                                            asignacion.activoasignar = activoasignar
                                                            asignacion.save()
                                                for l in lista2:
                                                    if l['action'] == 'del':
                                                        facultad = GrupoFacultadExamen.objects.get(pk=int(l['idgrupofacultad']))
                                                        facultad.status = False
                                                        facultad.save()
                                                        asignaciones = GrupoCarreraExamen.objects.filter(status=True, grupofacultad=facultad)
                                                        for a in asignaciones:
                                                            a.status = False
                                                            a.save()
                                                            mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=a)
                                                            for m in mallas:
                                                                m.status = False
                                                                m.save()
                                                            coordinadores = AsignacionGrupoCoordinador.objects.filter(status=True, grupocarrera=a)
                                                            for c in coordinadores:
                                                                c.status = False
                                                                c.save()
                                                    else:
                                                        facultad = Facultad.objects.get(pk=int(l['idfacultad']))
                                                        nombre = 'CRONOGRAMA PARA ' + facultad.nombre + ' EN ' + cronograma.periodo.nombre
                                                        if l['action'] == 'add':
                                                            grupo = GrupoFacultadExamen(nombre=nombre, grupocronograma=cronograma, facultad=facultad)
                                                            grupo.save()
                                                        else:
                                                            grupo = GrupoFacultadExamen.objects.get(pk=int(l['idgrupofacultad']))
                                                        for c in l['carreras']:
                                                            if c['action'] == 'add':
                                                                carrera = Carrera.objects.get(pk=int(c['idcarrera']))
                                                                nombre = 'CRONOGRAMA PARA ' + carrera.nombre + ' EN ' + cronograma.periodo.nombre
                                                                if c['idtipocarrera'] == "carrera":
                                                                    activocarrera = True
                                                                else:
                                                                    activocarrera = False
                                                                if c['idtipocarrera'] == "malla":
                                                                    activomalla = True
                                                                else:
                                                                    activomalla = False
                                                                grupocarrera = GrupoCarreraExamen(nombre=nombre, grupofacultad=grupo, carrera=carrera, activocarrera=activocarrera, activomalla=activomalla)
                                                                grupocarrera.save()
                                                            elif c['action'] == 'del':
                                                                grupocarrera = GrupoCarreraExamen.objects.get(pk=int(c['idgrupocarrera']))
                                                                grupocarrera.status = False
                                                                grupocarrera.save()
                                                                coordinadores = AsignacionGrupoCoordinador.objects.filter(grupocarrera=grupocarrera)
                                                                for c in coordinadores:
                                                                    c.status = False
                                                                    c.save()
                                                return JsonResponse({"result": "ok"})
                                            else:
                                                return JsonResponse({"result": "error","mensaje": 'Error en fechas para coordinadores y docentes'})
                                        else:
                                            return JsonResponse({"result": "error", "mensaje": 'Error, ingresar los coordinadores'})
                                    else:
                                        return JsonResponse({"result": "error","mensaje": 'El rango de fechas para el cronograma es erroneo.'})
                                else:
                                    return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                            else:
                                return JsonResponse({"result": "error", "mensaje": 'Seleccionar los formatos para reactivos.'})

                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_cronogramaplanificacion':
                    try:
                        cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.POST['id']))
                        examenes = CronogramaExamen.objects.filter(status=True, planificacion=cronograma).exists()
                        if examenes is False:
                            cronograma.status = False
                            cronograma.save()
                            formatos = GrupoFormatoReactivo.objects.filter(status=True, grupocronograma=cronograma)
                            for f in formatos:
                                f.status = False
                                f.save()
                            facultades = GrupoFacultadExamen.objects.filter(status=True, grupocronograma=cronograma)
                            for f in facultades:
                                f.status = False
                                f.save()
                            carreras = GrupoCarreraExamen.objects.filter(status=True, grupofacultad__grupocronograma=cronograma)
                            for f in carreras:
                                f.status = False
                                f.save()
                            mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera__grupofacultad__grupocronograma=cronograma)
                            for f in mallas:
                                f.status = False
                                f.save()
                            coordinadores = AsignacionGrupoCoordinador.objects.filter(status=True, grupocarrera__grupofacultad__grupocronograma=cronograma)
                            for f in coordinadores:
                                f.status = False
                                f.save()
                            generales = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=cronograma.periodo, formato__formatoreactivo__tiporeactivo__nombre="GENERAL")
                            for f in generales:
                                f.status = False
                                f.save()
                            docentes = AsignacionDocenteReactivo.objects.filter(status=True, asignacion__periodo=cronograma.periodo)
                            for f in docentes:
                                f.status = False
                                f.save()
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente__asignacion__periodo=cronograma.periodo)
                            for f in reactivos:
                                f.status = False
                                f.save()
                            bateria = Bateria.objects.get(status=True, cronograma=cronograma, periodo=cronograma.periodo)
                            bateria.status=False
                            bateria.save()
                            batcarreras = BateriaCarrera.objects.filter(status=True, bateria=bateria)
                            for r in batcarreras:
                                r.status=False
                                r.save()
                                examen = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=r)
                                for e in examen:
                                    e.status = False
                                    e.save()
                            reactivos = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera__bateria=bateria)
                            for r in reactivos:
                                r.status = False
                                r.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "Error no se puede borrar"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_asignacioncoordinador':
                    try:
                        vali = request.POST['valilista']
                        if vali == '1':
                            datos = json.loads(request.POST['lista_items1'])
                            for dato in datos:
                                if dato['tipo']== 'carrera':
                                    coordinador = CoordinadorCarrera.objects.get(pk=int(dato['idcoordinador']))
                                    formato = GrupoFormatoReactivo.objects.get(pk=int(dato['idformato']))
                                    carrera = GrupoCarreraExamen.objects.get(pk=int(dato['idcarrera']))
                                    activoc = dato['activoc']
                                    inicio = datetime(int(dato['inicio'].split('-')[2]), int(dato['inicio'].split('-')[1]), int(dato['inicio'].split('-')[0]))
                                    fin = datetime(int(dato['fin'].split('-')[2]), int(dato['fin'].split('-')[1]), int(dato['fin'].split('-')[0]))
                                    periodo = carrera.grupofacultad.grupocronograma.periodo
                                    bateria = int(dato['bateria'])
                                    nombre = 'ASIGNACION PARA ' + dato['carrera']
                                    if dato['action'] == 'add':
                                        asignacion = AsignacionGrupoCoordinador(nombre=nombre, grupocarrera=carrera, coordinador=coordinador, periodo=periodo, formato=formato, inicio=inicio, fin=fin, activoasignar=activoc, estadorevision=False, estadoasignar=True, estadoinicial=True, estadofinal=False, tamaniobateria=bateria)
                                        asignacion.save()
                                        for a in dato['asignaciones']:
                                            malla = Malla.objects.get(pk=int(a['idmalla']))
                                            nombre = 'CRONOGRAMA PARA ' + malla.nombre
                                            grupomalla = GrupoCarreraMallaExamen(nombre=nombre, grupocarrera=carrera, malla=malla)
                                            grupomalla.save()
                                        bateria = Bateria.objects.get(cronograma=carrera.grupofacultad.grupocronograma, status=True)
                                        bateriacarrera = BateriaCarrera(bateria=bateria, carrera=carrera, malla=None)
                                        bateriacarrera.save()
                                    elif dato['action'] == 'edit':
                                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(dato['idasignacion']))
                                        asignacion.formato = formato
                                        asignacion.coordinador = coordinador
                                        asignacion.inicio = inicio
                                        asignacion.fin = fin
                                        asignacion.activoasignar = activoc
                                        asignacion.tamaniobateria = bateria
                                        asignacion.save()
                                        for a in dato['asignaciones']:
                                            if a['action'] == 'add':
                                                malla = Malla.objects.get(pk=int(a['idmalla']))
                                                nombre = 'CRONOGRAMA PARA ' + malla.nombre
                                                grupomalla = GrupoCarreraMallaExamen(nombre=nombre, grupocarrera=carrera, malla=malla)
                                                grupomalla.save()
                                            elif a['action'] == 'del':
                                                grupomalla = GrupoCarreraMallaExamen.objects.get(pk=int(a['idgrupomalla']))
                                                grupomalla.status = False
                                                grupomalla.save()
                                                grupomalla.delete()
                                    elif dato['action'] == 'del':
                                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(dato['idasignacion']))
                                        asignacion.status = False
                                        asignacion.save()
                                        asignaciones = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=carrera)
                                        for a in asignaciones:
                                            a.status = False
                                            a.save()
                                        bateriacarrera = BateriaCarrera.objects.get(carrera=carrera, status=True, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                                        bateriacarrera.status=False
                                        bateriacarrera.save()
                                        baterias = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateriacarrera)
                                        for b in baterias:
                                            b.status=False
                                            b.save()
                                else:
                                    grupocarrera = GrupoCarreraExamen.objects.get(pk=int(dato['idcarrera']))
                                    if dato['action'] != 'del':
                                        for a in dato['asignaciones']:
                                            bateria = int(a['bateria'])
                                            inicio = datetime(int(a['inicio'].split('-')[2]), int(a['inicio'].split('-')[1]), int(a['inicio'].split('-')[0]))
                                            fin = datetime(int(a['fin'].split('-')[2]), int(a['fin'].split('-')[1]), int(a['fin'].split('-')[0]))
                                            coordinador = CoordinadorCarrera.objects.get(pk=int(a['idcoordinador']))
                                            formato = GrupoFormatoReactivo.objects.get(pk=int(a['idformato']))
                                            activoc = a['activoc']
                                            if a['action'] == 'add':
                                                malla = Malla.objects.get(pk=int(a['idmalla']))
                                                nombre = 'CRONOGRAMA PARA '+ malla.nombre
                                                gmalla = GrupoCarreraMallaExamen(nombre=nombre, grupocarrera=grupocarrera, malla=malla)
                                                gmalla.save()
                                                nombre = 'CRONOGRAMA PARA ' + grupocarrera.carrera.nombre
                                                asignacion = AsignacionGrupoCoordinador(nombre=nombre, grupocarrera=grupocarrera, grupomalla=gmalla, coordinador=coordinador, periodo=grupocarrera.grupofacultad.grupocronograma.periodo, formato=formato, inicio=inicio, fin=fin, activoasignar=activoc, estadorevision=False, estadoasignar=True, estadoinicial=True, estadofinal=False, tamaniobateria=bateria)
                                                asignacion.save()
                                                bateria = Bateria.objects.get(cronograma=grupocarrera.grupofacultad.grupocronograma, status=True)
                                                bateriacarrera = BateriaCarrera(bateria=bateria, carrera=grupocarrera, malla=gmalla)
                                                bateriacarrera.save()
                                            elif a['action'] == 'edit':
                                                asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(a['idasignacion']))
                                                asignacion.coordinador = coordinador
                                                asignacion.formato
                                                asignacion.activoasignar = activoc
                                                asignacion.inicio = inicio
                                                asignacion.fin = fin
                                                asignacion.tamaniobateria = bateria
                                                asignacion.save()
                                            elif a['action'] == 'del':
                                                asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(a['idasignacion']))
                                                asignacion.status = False
                                                asignacion.save()
                                                grupomalla = GrupoCarreraMallaExamen.objects.get(pk=int(a['idgrupomalla']))
                                                grupomalla.status = False
                                                grupomalla.save()
                                                bateriacarrera = BateriaCarrera.objects.get(carrera=grupomalla.grupocarrera, malla=grupomalla, status=True, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                                                bateriacarrera.status = False
                                                bateriacarrera.save()
                                                baterias = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateriacarrera)
                                                for b in baterias:
                                                    b.status = False
                                                    b.save()
                                    else:
                                        asignaciones = AsignacionGrupoCoordinador.objects.filter(status=True, grupocarrera=a['idcarrera'])
                                        for a in asignaciones:
                                            a.status = False
                                            a.save()
                                            grupomalla = GrupoCarreraMallaExamen.objects.get(pk=int(a['idgrupomalla']))
                                            grupomalla.status = False
                                            grupomalla.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'Error al enviar los datos.'})

                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_areasperiodo':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        if periodo.activo:
                            areas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('area', 'area__nombre').distinct()
                        else:
                            areas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion__periodo=periodo, asignacion__formato__formatoreactivo__tiporeactivo__nombre="GENERAL").values('area', 'area__nombre').order_by('area').distinct()
                        lista = list(areas)
                        return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_totalreactivosarea':
                    try:
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        area = ReactivoArea.objects.get(pk=int(request.POST['id']))
                        if periodo.activo:
                            reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__area=area)
                        else:
                            reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion__periodo=periodo,
                                                                       asignaciondocente__area=area)
                        count = len(reactivos).__str__()
                        return JsonResponse({"result": "ok", "mensaje": count})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'adm_reactivosarea':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        area = ReactivoArea.objects.get(pk=int(request.POST['id']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        cantidad = int(request.POST['cantidad'])
                        if periodo.activo:
                            reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__area=area).order_by('id')
                        else:
                            reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion__periodo=periodo, asignaciondocente__area=area).order_by('id')
                        lista = []
                        for r in reactivos:
                            atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=r).exclude(atributo=None).order_by('id').values('atributo__nombre', 'texto', 'archivo')
                            opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None).order_by('id').values('texto','archivo')
                            item = {'reactivo': r.id, 'tipopregunta': r.tipopregunta.nombre, 'aleatorio': r.aleatorio, 'nota': r.nota, 'atributos': list(atributos), 'opciones': list(opciones), 'vali': False}
                            if len(lista) == 0:
                                lista = [item]
                            else:
                                lista.append(item)
                        if cantidad <= len(lista):
                            L = sample(range(0, len(reactivos)), cantidad)
                            l = sorted(L)
                            for item in l:
                                lista[item]['vali'] = True
                        elif cantidad > len(lista):
                            return JsonResponse({"result": "error", "mensaje": 'La cantidad no puede ser mayor a '+len(lista).__str__()})
                        lista = list(lista)
                        return JsonResponse({"result": "ok", "mensaje": lista, 'asignatura':request.POST['id']})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_reactivosareabateria':
                    try:
                        datos = sorted(json.loads(request.POST['lista_reactivos']))
                        lista = []
                        for d in datos:
                            reactivo = ReactivoDocente.objects.get(pk=int(d))
                            atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo).exclude(atributo=None).order_by('id').values('atributo__nombre', 'texto', 'archivo')
                            opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo, atributo=None).order_by('id').values('texto','archivo')
                            item = {'reactivo': reactivo.id, 'tipopregunta': reactivo.tipopregunta.nombre, 'aleatorio': reactivo.aleatorio, 'nota': reactivo.nota, 'atributos': list(atributos), 'opciones': list(opciones), 'vali': False}
                            if len(lista) == 0:
                                lista = [item]
                            else:
                                lista.append(item)
                        return JsonResponse({"result":"ok", "mensaje":lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_bateriaexamen':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasignacion']))
                        carreras = json.loads(request.POST['lista_items2'])
                        vali = request.POST['vali']
                        if vali == '1' and len(carreras) != 0:
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="GENERAL")
                            datos = json.loads(request.POST['lista_items1'])
                            lista = []
                            for d in datos:
                                if len(lista) == 0:
                                    lista = d['reactivos']
                                else:
                                    lista.extend(d['reactivos'])
                            lista = sorted(lista)
                            for l in carreras:
                                bateriacarrera = BateriaCarrera.objects.get(pk=int(l))
                                vali = BateriaExamenComplexivo.objects.filter(bateriacarrera=bateriacarrera, coordinador=asignacion, tiporeactivo=tiporeactivo).exists()
                                if vali:
                                    bateria = BateriaExamenComplexivo.objects.get(bateriacarrera=bateriacarrera, coordinador=asignacion, tiporeactivo=tiporeactivo)
                                else:
                                    bateria = BateriaExamenComplexivo(bateriacarrera=bateriacarrera, coordinador=asignacion, tiporeactivo=tiporeactivo, revision=False, estadoinicial=True, estadofinal=False)
                                    bateria.save()
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateria).values('reactivo_id').order_by('reactivo_id'))
                                for r in reactivos:
                                    if not (r['reactivo_id']).__str__() in lista:
                                        detalle = BateriaDetalle.objects.get(reactivo_id=int(r['reactivo_id']), bateria=bateria, status=True)
                                        detalle.status = False
                                        detalle.save()
                                for l in lista:
                                    reactivo = ReactivoDocente.objects.get(pk=int(l))
                                    if not BateriaDetalle.objects.filter(status=True, bateria=bateria, reactivo=reactivo).exists():
                                        detalle = BateriaDetalle(bateria=bateria, reactivo=reactivo)
                                        detalle.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'Revisar los datos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_cronogramacarreras':
                    try:
                        cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.POST['idcronograma']))
                        grupocarrera = GrupoCarreraExamen.objects.filter(status=True, grupofacultad__grupocronograma=cronograma).exists()
                        if grupocarrera:
                            grupocarrera = GrupoCarreraExamen.objects.filter(status=True, grupofacultad__grupocronograma=cronograma).values('id', 'carrera__nombre')
                            lista = [{'id': i['id'], 'carrera__nombre': i['carrera__nombre']} for i in grupocarrera]
                            return JsonResponse({"result":"ok", "mensaje":lista})
                        else:
                            return JsonResponse({"result":"error", "mensaje":'No hay planificación para ese periodo'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_cronogramaexamen':
                    try:
                        vali = CronogramaExamenForm(request.POST)
                        if vali.is_valid():
                            planificacion = vali.cleaned_data['planificacion']
                            periodo = Periodo.objects.get(status=True, activo=True)
                            cronograma = CronogramaExamen(nombre=vali.cleaned_data['nombre'], periodo=periodo, planificacion=planificacion, carrera=vali.cleaned_data['carrera'], fecha=vali.cleaned_data['fecha'], tiempo=None, activo=vali.cleaned_data['activo'])
                            cronograma.save()
                            #grupos
                            if request.POST['vali'] == '1':
                                datos = json.loads(request.POST['lista_items1'])
                                for d in datos:
                                    if d['action'] == "add":
                                        inicio = datetime(cronograma.fecha.year, cronograma.fecha.month, cronograma.fecha.day,int(d['inicio'].split(':')[0]),int(d['inicio'].split(':')[1]))
                                        fin = datetime(cronograma.fecha.year, cronograma.fecha.month, cronograma.fecha.day,int(d['fin'].split(':')[0]),int(d['fin'].split(':')[1]))
                                        tiempo = d['tiempo']
                                        if tiempo == "" or tiempo == None:
                                            tiempo = 0
                                        else:
                                            int(d['tiempo'])
                                        grupo = GrupoExamen(
                                            nombre=d['nombre'],
                                            aula=d['aula'],
                                            cronogramaexamen=cronograma,
                                            fecha = cronograma.fecha,
                                            inicio=inicio.time(),
                                            fin=fin.time(),
                                            minutos=tiempo,
                                            cantidad=int(d['cantidad']),
                                            notamin=float(d['notamin']),
                                            notamax=float(d['notamax']),
                                            tipoexamen=int(d['idtipoexamen']),
                                            activo=d['activo']
                                        )
                                        grupo.save()
                            return JsonResponse({"result": "ok",'mensaje':'prueba'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_cronogramaexamen':
                    try:
                        vali = CronogramaExamenForm(request.POST)
                        if vali.is_valid():
                            examen = CronogramaExamen.objects.get(pk=int(request.POST['id']))
                            examen.planificacion = vali.cleaned_data['planificacion']
                            examen.nombre = vali.cleaned_data['nombre']
                            examen.carrera = vali.cleaned_data['carrera']
                            examen.fecha = vali.cleaned_data['fecha']
                            examen.activo = vali.cleaned_data['activo']
                            examen.save()
                            return JsonResponse({"result": "ok", 'mensaje': 'prueba'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_cronogramaexamen':
                    try:
                        examen = CronogramaExamen.objects.get(pk=int(request.POST['id']))
                        examen.status=False
                        examen.save()
                        #los grupos
                        grupos = GrupoExamen.objects.filter(status=True, cronogramaexamen=examen)
                        for g in grupos:
                            g.status = False
                            g.save()
                            #delegados
                            delegados = GrupoExamenDelegado.objects.filter(status=True, grupoexamen=g)
                            for d in delegados:
                                d.status=False
                                d.save()
                            #baterias
                            baterias = GrupoExamenConfiguracion.objects.filter(status=True, grupoexamen=g)
                            for b in baterias:
                                b.status=False
                                b.save()
                                #configuraciones
                                configuraciones = GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=b)
                                for c in configuraciones:
                                    c.status=False
                                    c.save()
                                #estudiantes
                                estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamenconfiguracion=b)
                                for e in estudiantes:
                                    e.status = False
                                    e.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_grupoexamen':
                    try:
                        vali = GrupoExamenForm(request.POST)
                        if vali.is_valid() and request.POST['vali'] == '1' and request.POST['valiestudiantes'] == '1':
                            examen = CronogramaExamen.objects.get(pk=int(request.POST['id']))
                            tiempo = vali.cleaned_data['minutos']
                            grupo = GrupoExamen(
                                nombre=vali.cleaned_data['grupo'],
                                aula=vali.cleaned_data['aula'],
                                cronogramaexamen=examen,
                                fecha=examen.fecha,
                                inicio=vali.cleaned_data['inicio'],
                                fin=vali.cleaned_data['fin'],
                                minutos=tiempo,
                                cantidad=vali.cleaned_data['cantidad'],
                                notamin=vali.cleaned_data['notamin'],
                                notamax=vali.cleaned_data['notamax'],
                                tipoexamen=vali.cleaned_data['tipo'],
                                activo=vali.cleaned_data['mostrar']
                            )
                            grupo.save()
                            estudiantes = json.loads(request.POST['lista_items1'])
                            for e in estudiantes:
                                #verificar bateria de estudiante
                                estudiante = MatriculaTitulacion.objects.get(pk=int(e['idmatricula']))
                                grupoestudiante = GrupoExamenEstudiante(
                                    grupoexamen=grupo,
                                    estudiante=estudiante
                                )
                                grupoestudiante.save()
                            #guardar configuracion
                            #guardar estudiantes
                            return JsonResponse({"result": "ok", 'mensaje': 'prueba'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_grupoexamen':
                    try:
                        vali = GrupoExamenForm(request.POST)
                        if vali.is_valid() and request.POST['vali'] == '1' and request.POST['valiestudiantes'] == '1':
                            grupo = GrupoExamen.objects.get(pk=int(request.POST['id']))
                            tiempo = vali.cleaned_data['minutos']
                            grupo.nombre = vali.cleaned_data['grupo']
                            grupo.aula = vali.cleaned_data['aula']
                            grupo.fecha = vali.cleaned_data['fecha']
                            grupo.inicio = vali.cleaned_data['inicio']
                            grupo.fin = vali.cleaned_data['fin']
                            grupo.minutos = tiempo
                            grupo.cantidad = vali.cleaned_data['cantidad']
                            grupo.notamin = vali.cleaned_data['notamin']
                            grupo.notamax = vali.cleaned_data['notamax']
                            grupo.tipoexamen = vali.cleaned_data['tipo']
                            grupo.activo = vali.cleaned_data['mostrar']
                            grupo.save()
                            estudiantes = json.loads(request.POST['lista_items1'])
                            for e in estudiantes:
                                # verificar bateria de estudiante
                                if e['action'] == "add":
                                    estudiante = MatriculaTitulacion.objects.get(pk=int(e['idmatricula']))
                                    grupoestudiante = GrupoExamenEstudiante(
                                        grupoexamen=grupo,
                                        estudiante=estudiante
                                    )
                                    grupoestudiante.save()
                                elif e['action'] == "del":
                                    grupoestudiante = GrupoExamenEstudiante.objects.get(pk=int(e['id']))
                                    grupoestudiante.status=False
                                    grupoestudiante.save()
                            return JsonResponse({"result": "ok", 'mensaje': 'prueba'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_grupoexamen':
                    try:
                        grupo = GrupoExamen.objects.get(pk=int(request.POST['id']))
                        grupo.status=False
                        grupo.save()
                        #delegados
                        delegados = GrupoExamenDelegado.objects.filter(status=True, grupoexamen=grupo)
                        for d in delegados:
                            d.status=False
                            d.save()
                        # baterias
                        baterias = GrupoExamenConfiguracion.objects.filter(status=True, grupoexamen=grupo)
                        for b in baterias:
                            b.status = False
                            b.save()
                            # configuraciones
                            configuraciones = GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=b)
                            for c in configuraciones:
                                c.status = False
                                c.save()
                            # estudiantes
                            estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamenconfiguracion=b)
                            for e in estudiantes:
                                e.status = False
                                e.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_estudiantebateria':
                    try:
                        bateria = BateriaCarrera.objects.get(pk=int(request.POST['idbateria']))
                        reactivos = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).count()
                        grupo = GrupoExamen.objects.get(pk=int(request.POST['idgrupo']))
                        estudiantes = list(BateriaEstudiante.objects.filter(status=True, bateriacarrera=bateria, periodo=grupo.cronogramaexamen.periodo).
                                           values('matricula','matricula__inscripcion__persona', 'matricula__inscripcion__persona__nombres',
                                                  'matricula__inscripcion__persona__apellido1', 'matricula__inscripcion__persona__apellido2'))
                        lista = [{'id': i['matricula'], 'persona': i['matricula__inscripcion__persona__nombres']+" "+i['matricula__inscripcion__persona__apellido1'] + " " + i['matricula__inscripcion__persona__apellido2']} for i in estudiantes]
                        return JsonResponse({"result":"ok", "mensaje":lista, "count":reactivos.__str__()})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_secciones':
                    try:
                        bateria = BateriaCarrera.objects.get(pk=int(request.POST['idbateria']))
                        areas = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).exclude(reactivo__asignaciondocente__area=None).values('reactivo__asignaciondocente__area', 'reactivo__asignaciondocente__area__nombre').distinct('reactivo__asignaciondocente__area'))
                        asignaturas = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area=None).values('reactivo__asignaciondocente__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').distinct('reactivo__asignaciondocente__asignatura'))
                        lista1 = [{'id': i['reactivo__asignaciondocente__area'],
                                   'seccion': i['reactivo__asignaciondocente__area__nombre'],
                                   'tipo':'area',
                                   'total': BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area=int(i['reactivo__asignaciondocente__area'])).exclude(reactivo__asignaciondocente__area=None).count().__str__()} for i in areas]
                        lista2 = [{'id': i['reactivo__asignaciondocente__asignatura'], 'seccion': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'tipo':'asig', 'total': BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area=None, reactivo__asignaciondocente__asignatura=int(i['reactivo__asignaciondocente__asignatura'])).count().__str__()} for i in asignaturas]
                        return JsonResponse({"result":"ok", "mensaje":lista1+lista2})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_grupoexamenconfiguracion':
                    try:
                        if request.POST['vali'] == '1':
                            datos=json.loads(request.POST['lista_items1'])
                            grupo = GrupoExamen.objects.get(pk=int(request.POST['id']))
                            for d in datos:
                                bateria = BateriaCarrera.objects.get(pk=int(d['idbateria']))
                                if d['action'] == 'add':
                                    grupobateria = GrupoExamenConfiguracion(grupoexamen=grupo, bateria=bateria, tiposeleccion=int(d['idtiposeleccion']), filtroseleccion=int(d['idfiltroseleccion']))
                                    grupobateria.save()
                                    for e in d['estudiantes']:
                                        estudiante = MatriculaTitulacion.objects.get(pk=int(e['idestudiante']))
                                        if e['action'] == 'add':
                                            estudiante = GrupoExamenEstudiante(grupoexamenconfiguracion=grupobateria, estudiante=estudiante)
                                            estudiante.save()
                                    for a in d['ajustes']:
                                        if a['idarea'] == "":
                                            area = None
                                        else:
                                            area = ReactivoArea.objects.get(pk=int(a['idarea']))
                                        if a['idasignatura'] == "":
                                            asignatura = None
                                        else:
                                            asignatura = AsignaturaMalla.objects.get(pk=int(a['idasignatura']))
                                        ajuste = GrupoConfiguracion(grupoexamenconfiguracion=grupobateria, area=area, asignatura=asignatura, cantidad=int(a['cantidad']), rangoinicio=a['rangoinicio'], rangofin=a['rangofin'], aleatorio=a['aleatorio'])
                                        ajuste.save()
                                elif d['action'] == 'del':
                                    grupobateria = GrupoExamenConfiguracion(pk=int(d['id']))
                                    grupobateria.status=False
                                    grupobateria.save()
                                    estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamenconfiguracion=grupobateria)
                                    for e in estudiantes:
                                        e.status=False
                                        e.save()
                                    ajustes = GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=grupobateria)
                                    for e in ajustes:
                                        e.status=False
                                        e.save()
                            return JsonResponse({"result": "ok", 'mensaje': 'prueba'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_delegadoexamen':
                    try:
                        if request.POST['vali'] == "1":
                            grupo = GrupoExamen.objects.get(pk=int(request.POST['id']))
                            datos=json.loads(request.POST['lista_items1'])
                            for d in datos:
                                docente = Profesor.objects.get(pk=int(d['idprofesor']))
                                if d['action'] == 'add':
                                    delegado = GrupoExamenDelegado(grupoexamen=grupo,docente=docente, tipodelegado=int(d['idtipodelegado']), principal=d['principal']);
                                    delegado.save()
                                elif d['action'] == "edit":
                                    delegado = GrupoExamenDelegado.objects.get(pk=int(d['id']))
                                    delegado.principal = d['principal']
                                    delegado.tipodelegado = int(d['idtipodelegado'])
                                    delegado.save()
                                elif d['action'] == "del":
                                    delegado = GrupoExamenDelegado.objects.get(pk=int(d['id']))
                                    delegado.status=False
                                    delegado.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje":"Error erroneos"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_revisionbateria':
                    try:
                        datos = json.loads(request.POST['lista_items1'])
                        for d in datos:
                            bateriacarrera = BateriaCarrera.objects.get(pk=int(d['idcarrera']))
                            bateriacarrera.revision = d['vali']
                            bateriacarrera.save()
                        return JsonResponse({"result": "ok", 'mensaje': 'prueba'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_impugnacion':
                    try:
                        impugnacion = ImpugnacionExamen.objects.get(pk=int(request.POST['id']))
                        if request.POST['estado'] == "true":
                            impugnacion.estado = True
                        else:
                            impugnacion.estado = False
                        impugnacion.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                else:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al enviar los datos."})
            else:
                return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
        else:
            return JsonResponse({"result": "session"})
    else:
        if 'user' in request.session:
            if 'action' in request.GET:
                action = request.GET['action']
                if action == 'add_pais':
                    try:
                        data['title'] = u'Agregar Pais'
                        data['form'] = PaisForm(initial={'estado': True})
                        return render(request, "add_pais.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')

                elif action == 'edit_pais':
                    try:
                        data['title'] = u'Editar Pais'
                        data['pais'] = pais = Pais.objects.get(pk=int(request.GET['id']))
                        data['form'] = PaisForm(initial={'nombre': pais.nombre,
                                                         'estado': pais.estado})
                        return render(request, "add_pais.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')

                elif action == 'del_pais':
                    try:
                        data['title'] = u'Eliminar Pais'
                        data['pais'] = Pais.objects.get(pk=int(request.GET['id']))
                        return render(request, "del_pais.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_tiporeactivo':
                    try:
                        return view_tiporeactivo(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_tiporeactivo':
                    try:
                        data['title'] = u'Agregar Tipo de reactivo'
                        data['form'] = TipoReactivoForm(initial={'estado': True})
                        return render(request, "adm_examencomplexivo/add_tiporeactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_tiporeactivo':
                    try:
                        data['title'] = u'Editar Tipo de reactivo'
                        data['tiporeactivo'] = tipo = TipoReactivo.objects.get(pk=int(request.GET['id']))
                        data['form'] = TipoReactivoForm(initial={'nombre': tipo.nombre, 'estado':tipo.estado})
                        return render(request, "adm_examencomplexivo/edit_tiporeactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_tiporeactivo':
                    try:
                        data['title'] = u'Eliminar Tipo de reactivo'
                        data['tiporeactivo'] = TipoReactivo.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_tiporeactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_formatoreactivo':
                    try:
                        return view_formatoreactivo(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_formatoreactivo':
                    try:
                        data['title'] = u'Agregar Formato de reactivo'
                        data['form'] = FormatoReactivoForm()
                        return render(request, "adm_examencomplexivo/add_formatoreactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_formatoreactivo':
                    try:
                        data['title'] = u'Editar Formato de reactivo'
                        data['formato'] = formato = FormatoReactivo.objects.get(pk=int(request.GET['id']))
                        data['form'] = FormatoReactivoForm(initial={'nombre': formato.nombre, 'descripcion': formato.descripcion, 'tiporeactivo': formato.tiporeactivo, 'notamin': int(formato.notamin), 'notamax': int(formato.notamax), 'opcionesmin': formato.opcionesmin, 'opcionesmax': formato.opcionesmax, 'respuestasmin': formato.respuestasmin, 'respuestasmax': formato.respuestasmax, 'estado': formato.estado,'valiopciones': formato.valiopciones})
                        data['atributos'] = AtributoReactivo.objects.filter(status=True, formatoreactivo=formato, estado=True)
                        return render(request, "adm_examencomplexivo/edit_formatoreactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_formatoreactivo':
                    try:
                        data['title'] = u'Eliminar formato de reactivo'
                        data['formato'] = FormatoReactivo.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_formatoreactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_atributoreactivo':
                    try:
                        if 'idformato' in request.GET:
                            formato = FormatoReactivo.objects.get(pk=int(request.GET['idformato']))
                            data['atributoreactivo'] = AtributoReactivo.objects.filter(formatoreactivo=formato, estado=True)
                            data['title'] = "CAMPOS DE %s" % formato
                            return render(request, "adm_examencomplexivo/ajax_atributos.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_tipopregunta':
                    try:
                        return view_tipopregunta(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_tipopregunta':
                    try:
                        data['title'] = u'Agregar tipo de pregunta'
                        data['form'] = TipoPreguntaReactivoForm(initial={'activo':True})
                        return render(request, "adm_examencomplexivo/add_tipopregunta.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_tipopregunta':
                    try:
                        data['title'] = u'Editar tipo de pregunta'
                        data['tipopregunta'] = tipo = TipoPreguntaReactivo.objects.get(pk=int(request.GET['id']))
                        data['form'] = TipoPreguntaReactivoForm(initial={'nombre': tipo.nombre, 'abreviatura': tipo.abreviatura, 'activo': tipo.activo})
                        return render(request, "adm_examencomplexivo/edit_tipopregunta.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_tipopregunta':
                    try:
                        data['title'] = u'Eliminar tipo de pregunta'
                        data['tipopregunta'] = TipoPreguntaReactivo.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_tipopregunta.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_areareactivo':
                    try:
                        return view_areareactivo(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_areareactivo':
                    try:
                        data['title'] = u'Agregar área'
                        data['form'] = AreaReactivoForm(initial={'activo': True})
                        return render(request, "adm_examencomplexivo/add_areareactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_areareactivo':
                    try:
                        data['title'] = u'Editar área'
                        data['area'] = area = ReactivoArea.objects.get(pk=int(request.GET['id']))
                        data['form'] = AreaReactivoForm(initial={'nombre': area.nombre, 'activo': area.activo})
                        return render(request, "adm_examencomplexivo/edit_areareactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_areareactivo':
                    try:
                        data['title'] = u'Eliminar área'
                        data['area'] = ReactivoArea.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_areareactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_cronogramaplanificacion':
                    try:
                        return view_cronogramaplanificacion(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_cronogramaplanificacion':
                    try:
                        data['title'] = u'Agregar cronograma'
                        data['formatos'] = FormatoReactivo.objects.filter(status=True, estado=True)
                        data['facultades'] = Facultad.objects.filter(status=True).order_by('-id')
                        data['docentes'] = Profesor.objects.filter(status=True)
                        data['form'] = CronogramaPlanificacionForm(initial={'tambateria':300})
                        return render(request, "adm_examencomplexivo/add_cronogramaplanificacion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallecronograma':
                    try:
                        if 'id' in request.GET:
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['id']))
                            data['formatos'] = GrupoFormatoReactivo.objects.filter(status=True, grupocronograma=cronograma)
                            data['title'] = 'Detalles'
                            data['general'] = AsignacionGrupoCoordinador.objects.filter(status=True, formato__formatoreactivo__tiporeactivo__nombre="GENERAL", periodo=cronograma.periodo)
                            data['especifico'] = AsignacionGrupoCoordinador.objects.filter(status=True, formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", periodo=cronograma.periodo, grupocarrera__status=True,grupocarrera__grupofacultad__grupocronograma=cronograma).order_by('grupocarrera__carrera__facultad', 'grupocarrera__carrera')
                            return render(request, "adm_examencomplexivo/ajax_detallecronograma.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_asignacioncoordinador':
                    try:
                        cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['id']))
                        data['title'] = cronograma.nombre
                        data['cronograma'] = cronograma
                        grupofac = GrupoFacultadExamen.objects.filter(status=True, grupocronograma=cronograma)
                        lista = []
                        for g in grupofac:
                            carreras = GrupoCarreraExamen.objects.filter(status=True, grupofacultad=g)
                            lista2 = []
                            for c in carreras:
                                asignaciones = AsignacionGrupoCoordinador.objects.filter(grupocarrera=c, status=True)
                                mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=c)
                                if len(lista2) == 0:
                                    lista2 = [{'carrera': c, 'asignaciones': asignaciones, 'mallas': mallas}]
                                else:
                                    lista2.append({'carrera': c, 'asignaciones': asignaciones, 'mallas': mallas})
                            if len(lista) == 0:
                                lista = [{'facultad': g, 'carreras': lista2}]
                            else:
                                lista.append({'facultad': g, 'carreras': lista2})
                        data['grupos'] = lista
                        data['user'] = request.session['user']
                        return render(request, "adm_examencomplexivo/adm_asignacioncoordinador.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_asignacioncoordinador':
                    try:
                        data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['idcro']))
                        data['formato'] = formato = GrupoFormatoReactivo.objects.filter(status=True, grupocronograma=cronograma)
                        data['form'] = AsignacionGrupoCoordinadorForm(initial={'cronograma': cronograma, 'tambateria': 300, 'inicio':  datetime.strftime(cronograma.inicio, "%d-%m-%Y"), 'fin':  datetime.strftime(cronograma.fin, "%d-%m-%Y"), 'activoasignar': True})
                        data['title'] = cronograma.nombre
                        data['facultad'] = facultad = GrupoFacultadExamen.objects.filter(status=True, grupocronograma=cronograma)
                        data['carrera'] = carrera = GrupoCarreraExamen.objects.filter(status=True, grupofacultad__grupocronograma=cronograma)
                        return render(request, "adm_examencomplexivo/add_asignacioncoordinador.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_cronogramaplanificacion':
                    try:
                        data['title'] = u'Editar cronograma de planificacion para examen complexivo'
                        data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['id']))
                        data['form'] = CronogramaPlanificacionForm(initial={'nombre': cronograma.nombre, 'periodo': cronograma.periodo, 'inicio': datetime.strftime(cronograma.inicio, "%d-%m-%Y"), 'fin': datetime.strftime(cronograma.fin, "%d-%m-%Y"), 'porcsimilitud': int(cronograma.porcsimilitud), 'tambateria': int('300'), 'iniciocord': datetime.strftime(cronograma.inicio, "%d-%m-%Y"), 'fincord': datetime.strftime(cronograma.fin, "%d-%m-%Y")})
                        data['formatos'] = formatos = GrupoFormatoReactivo.objects.filter(status=True, grupocronograma=cronograma)
                        data['facultades'] = Facultad.objects.filter(status=True).order_by('-id')
                        data['docentes'] = Profesor.objects.filter(status=True)
                        data['generales'] = generales = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=cronograma.periodo, formato__formatoreactivo__tiporeactivo__nombre="GENERAL")
                        data['carreras'] = grupocarrera = GrupoCarreraExamen.objects.filter(status=True, grupofacultad__grupocronograma=cronograma).order_by('grupofacultad__facultad')
                        return render(request, "adm_examencomplexivo/edit_cronogramaplanificacion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_cronogramaplanificacion':
                    try:
                        data['title'] = u'Eliminar cronograma de planificación'
                        data['cronograma'] = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_cronograma.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_revisionbateria':
                    try:
                        periodo = Periodo.objects.filter(status=True, activo=True).exists()
                        if periodo:
                            data['user'] = request.session['user']
                            periodo = Periodo.objects.get(status=True, activo=True)
                            data['title'] = "CRONOGRAMAS PARA " + periodo.nombre
                            data['cronogramas'] = CronogramaPlanificacionExamen.objects.filter(status=True, periodo=periodo)
                            return render(request, "adm_examencomplexivo/adm_revisionbateria.html", data)
                        else:
                            return HttpResponseRedirect('/')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallerevision':
                    try:
                        data['title'] = 'REVISION DE BATERIA'
                        data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(pk=int(request.GET['id']))
                        baterias = BateriaCarrera.objects.filter(status=True, bateria__cronograma=cronograma)
                        lista = [{'bateria': i,
                                 'generales': BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=i, reactivo__asignaciondocente__formato__formatoreactivo__tiporeactivo__nombre="GENERAL").count(),
                                 'especificos': BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=i, reactivo__asignaciondocente__formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO").count()
                                 } for i in baterias]
                        data['baterias'] = lista
                        return render(request, "adm_examencomplexivo/adm_revisionbateriadetalle.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'view_bateriacomplexivodetalle':
                    try:
                        tipo = request.GET['tipo']
                        bateriacarrera = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        if tipo == "e":
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="ESPECIFICO")
                            asignaturamalla = AsignaturaMalla.objects.get(pk=int(request.GET['idtipo']))
                            data['title'] = 'BATERIA DE ' + asignaturamalla.asignatura.nombre
                            reactivos = BateriaDetalle.objects.filter(status=True,
                                                                      bateria__bateriacarrera=bateriacarrera,
                                                                      bateria__tiporeactivo=tiporeactivo,
                                                                      reactivo__asignaciondocente__asignatura=asignaturamalla)
                        else:
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="GENERAL")
                            area = ReactivoArea.objects.get(pk=int(request.GET['idtipo']))
                            data['title'] = 'BATERIA DE ' + area.nombre
                            reactivos = BateriaDetalle.objects.filter(status=True,
                                                                      bateria__bateriacarrera=bateriacarrera,
                                                                      bateria__tiporeactivo=tiporeactivo,
                                                                      reactivo__asignaciondocente__area=area)
                        lista = []
                        for i in reactivos:
                            extra = []
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.reactivo, atributo=None).order_by('id').values('texto', 'archivo', 'id'))
                            if i.reactivo.tipopregunta.nombre != "EMPAREJAMIENTO":
                                listopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id']} for a in opciones]
                                opciones = listopciones
                            else:
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                extra = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id']} for a in aleatorio]
                                listopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0]} for i in opciones]
                                opciones = listopciones
                            if i.reactivo.asignaciondocente.asignatura:
                                nombre = i.reactivo.asignaciondocente.asignatura.asignatura.nombre
                            else:
                                nombre = i.reactivo.asignaciondocente.area.nombre
                            lista.append({'nombre': nombre, 'tipopregunta': i.reactivo.tipopregunta.nombre, 'atributos': atributos, 'opciones': opciones, 'extra': extra})
                        data['reactivos'] = lista
                        data['bateriacarrera']=bateriacarrera
                        data['tipo'] = tipo
                        data['view'] = 2
                        return render(request,"adm_examencomplexivo/view_bateriacomplexivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'view_bateriacomplexivo':
                    try:
                        tipo = request.GET['tipo']
                        bateriacarrera = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        lista = []
                        if tipo =="e":
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="ESPECIFICO")
                            reactivos = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriacarrera, bateria__tiporeactivo=tiporeactivo).values('reactivo__asignaciondocente__asignatura_id','reactivo__asignaciondocente__asignatura__asignatura__nombre').order_by('reactivo__asignaciondocente__asignatura_id').distinct()
                            lista.extend({'id': i['reactivo__asignaciondocente__asignatura_id'], 'nombre': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'] } for i in reactivos)
                        else:
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="GENERAL")
                            reactivos = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriacarrera, bateria__tiporeactivo=tiporeactivo).values('reactivo__asignaciondocente__area_id','reactivo__asignaciondocente__area__nombre').order_by('reactivo__asignaciondocente__area_id').distinct()
                            lista.extend({'id': i['reactivo__asignaciondocente__area_id'], 'nombre': i['reactivo__asignaciondocente__area__nombre']} for i in reactivos)
                        data['tipo'] = tipo
                        data['reactivos'] = lista
                        data['view'] = 1
                        data['title'] = 'BATERIA DE ' + bateriacarrera.carrera.carrera.nombre
                        data['bateriacarrera'] = bateriacarrera
                        return render(request, "adm_examencomplexivo/view_bateriacomplexivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_bateriaexamen':
                    try:
                        data['title'] = 'Baterias de examen complexivo'
                        data['user'] = user = request.session['user']
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        vali = CronogramaPlanificacionExamen.objects.filter(status=True, periodo=Periodo.objects.get(activo=True)).exists()
                        if vali:
                            persona = Persona.objects.get(pk=int(user.id))
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=Periodo.objects.get(activo=True))
                            data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(status=True, periodo=cronograma.periodo, formato__formatoreactivo__tiporeactivo__nombre="GENERAL")
                            data['baterias'] = BateriaCarrera.objects.filter(status=True, bateria__cronograma=cronograma)
                        return render(request, "adm_examencomplexivo/adm_bateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_bateriaexamen':
                    try:
                        data['bateriacarrera'] = bateriacarrera = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        if bateriacarrera.revision is False:
                            data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['idcord']))
                            data['title'] = 'Bateria de reactivos generales'
                            data['areas'] = areas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('area__nombre', 'area').distinct()
                            data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                            data['carreras'] = BateriaCarrera.objects.filter(status=True, bateria__periodo=asignacion.periodo)
                            vali = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateriacarrera, tiporeactivo__nombre="GENERAL", coordinador=asignacion).exists()
                            if vali:
                                bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, bateriacarrera=bateriacarrera, tiporeactivo__nombre="GENERAL", coordinador=asignacion)
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__area', 'reactivo__asignaciondocente__area__nombre').distinct().order_by('reactivo__asignaciondocente__area__nombre'))
                                lista = []
                                for r in reactivos:
                                    listareactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__area=int(r['reactivo__asignaciondocente__area'])).values('reactivo_id'))
                                    listareactivos = [i['reactivo_id'].__str__() for i in listareactivos]
                                    item = {'id': r['reactivo__asignaciondocente__area'], 'area': r['reactivo__asignaciondocente__area__nombre'], 'reactivos': listareactivos}
                                    if len(lista) == 0:
                                        lista = [item]
                                    else:
                                        lista.append(item)
                                data['reactivos'] = lista
                            return render(request, "adm_examencomplexivo/edit_bateria.html", data)
                        else:
                            return HttpResponseRedirect('/adm_configuracioncomplexivo?action=adm_bateriaexamen')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_validarbateriaexamen':
                    try:
                        data['title'] = 'Baterias de examen complexivo'
                        data['user'] = user = request.session['user']
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        vali = CronogramaPlanificacionExamen.objects.filter(status=True, periodo=Periodo.objects.get(activo=True)).exists()
                        if vali:
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=Periodo.objects.get(activo=True))
                            data['baterias'] = BateriaCarrera.objects.filter(status=True, bateria__cronograma=cronograma)
                        return render(request, "adm_examencomplexivo/adm_validarbateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_validarbateriaexamen':
                    try:
                        data['title'] = 'Revisión de bateria'
                        data['bateria'] = bateria = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        lista = []
                        data['baterias'] = baterias = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateria)
                        return render(request, "adm_examencomplexivo/edit_validarbateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_cronogramaexamen':
                    try:
                        data['user'] = user = request.session['user']
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        data['title'] = 'Exámen complexivo - cronograma'
                        periodo = Periodo.objects.get(activo=True)
                        data['cronogramas'] = cronogramas = CronogramaExamen.objects.filter(status=True, periodo=periodo)
                        return render(request, "adm_examencomplexivo/adm_cronogramaexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_cronogramaexamen':
                    try:
                        data['title'] = 'Agregar cronograma'
                        data['form'] = CronogramaExamenForm(initial={'activo': True})
                        hora = datetime.strftime(datetime.now(), "%H:%M:%S")
                        data['form2'] = GrupoExamenForm(initial={'inicio':hora, 'fin':hora})
                        return render(request, "adm_examencomplexivo/add_cronogramaexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_cronogramaexamen':
                    try:
                        data['title'] = 'Agregar cronograma'
                        data['examen'] = examen = CronogramaExamen.objects.get(pk=int(request.GET['id']))
                        data['form'] = CronogramaExamenForm(initial={'nombre':examen.nombre,'activo': examen.activo, 'planificacion': examen.planificacion, 'carrera': examen.carrera, 'fecha': datetime.strftime(examen.fecha, "%d-%m-%Y")})
                        return render(request, "adm_examencomplexivo/edit_cronogramaexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_cronogramaexamen':
                    try:
                        data['title'] = u'Eliminar cronograma de examen'
                        data['examen'] = CronogramaExamen.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_cronogramaexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_grupoexamen':
                    try:
                        data['title'] = 'Grupos de examen complexivo'
                        data['examen'] = examen = CronogramaExamen.objects.get(pk=int(request.GET['id']))
                        data['grupos'] = GrupoExamen.objects.filter(status=True, cronogramaexamen=examen).order_by('nombre')
                        return render(request, "adm_examencomplexivo/adm_grupoexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_grupoexamen':
                    try:
                        data['title'] = 'Grupos de examen complexivo'
                        data['examen'] = examen = CronogramaExamen.objects.get(pk=int(request.GET['id']))
                        baterias = list(BateriaEstudiante.objects.filter(status=True, bateriacarrera__carrera__carrera=examen.carrera.carrera, periodo=examen.periodo).
                                                           values('bateriacarrera', 'bateriacarrera__bateria__periodo__nombre', 'bateriacarrera__carrera__carrera__nombre', 'bateriacarrera__malla__malla__nombre').distinct('bateriacarrera'))
                        lista = [{'idbateria': i['bateriacarrera'], 'bateria': 'BATERIA DE '+i['bateriacarrera__carrera__carrera__nombre'],
                                  'malla': i['bateriacarrera__malla__malla__nombre'],
                                  'periodo': i['bateriacarrera__bateria__periodo__nombre'],
                                  'estudiantes': list(BateriaEstudiante.objects.filter(status=True, bateriacarrera__carrera__carrera=examen.carrera.carrera, periodo=examen.periodo, bateriacarrera_id=int(i['bateriacarrera'])))} for i in baterias]
                        data['baterias'] = lista
                        data['form'] = GrupoExamenForm(initial={'fecha': datetime.strftime(examen.fecha, "%d-%m-%Y")})
                        data['estudiantes'] = estudiantes = list(MatriculaTitulacion.objects.
                                                                 exclude(grupoexamenestudiante__grupoexamen__cronogramaexamen=examen, grupoexamenestudiante__status=True)
                                                                 .filter(status=True, alternativa__grupotitulacion__periodogrupo__periodo=examen.periodo, alternativa__tipotitulacion__mecanismotitulacion__mecanismotitulacion__nombre="EXAMEN COMPLEXIVO", alternativa__carrera=examen.carrera.carrera)
                                                                 )
                        return render(request, "adm_examencomplexivo/add_grupoexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_grupoexamen':
                    try:
                        data['title'] = 'Grupos de examen complexivo'
                        data['grupo'] = grupo = GrupoExamen.objects.get(pk=int(request.GET['id']))
                        data['examen'] = grupo.cronogramaexamen
                        if grupo.tipoexamen!=3:
                            data['form'] = GrupoExamenForm(initial={'grupo': grupo.nombre, 'aula': grupo.aula,'fecha':datetime.strftime(grupo.fecha, "%d-%m-%Y"), 'cantidad': grupo.cantidad, 'tipo': grupo.tipoexamen, 'notamin': int(grupo.notamin), 'notamax': int(grupo.notamax), 'mostrar':grupo.activo})
                        else:
                            data['form'] = GrupoExamenForm(initial={'grupo': grupo.nombre, 'aula': grupo.aula,'fecha':datetime.strftime(grupo.fecha, "%d-%m-%Y"), 'cantidad': grupo.cantidad, 'tipo': grupo.tipoexamen, 'minutos': grupo.minutos, 'notamin': int(grupo.notamin), 'notamax': int(grupo.notamax), 'mostrar':grupo.activo})
                        data['estudiantes'] = GrupoExamenEstudiante.objects.filter(status=True, grupoexamen=grupo)
                        data['otros'] = list(MatriculaTitulacion.objects.
                                                                 exclude(grupoexamenestudiante__grupoexamen__cronogramaexamen=grupo.cronogramaexamen,
                                                                         grupoexamenestudiante__status=True)
                                                                 .filter(status=True, alternativa__grupotitulacion__periodogrupo__periodo=grupo.cronogramaexamen.periodo, alternativa__tipotitulacion__mecanismotitulacion__mecanismotitulacion__nombre="EXAMEN COMPLEXIVO", alternativa__carrera=grupo.cronogramaexamen.carrera.carrera)
                                                                 )
                        return render(request, "adm_examencomplexivo/edit_grupoexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_grupoexamen':
                    try:
                        data['title'] = u'Eliminar gupo de examen'
                        data['grupo'] = GrupoExamen.objects.get(pk=int(request.GET['id']))
                        return render(request, "adm_examencomplexivo/del_grupoexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_grupoexamenconfiguracion':
                    try:
                        data['title'] = 'Grupos de estudiantes en examen complexivo'
                        data['grupo'] = grupo = GrupoExamen.objects.get(pk=int(request.GET['id']))
                        data['form'] = GrupoExamenConfiguracionForm()
                        data['baterias'] = (BateriaEstudiante.objects.filter(status=True, bateriacarrera__carrera__carrera=grupo.cronogramaexamen.carrera.carrera, periodo=grupo.cronogramaexamen.periodo).values('bateriacarrera', 'bateriacarrera__bateria__periodo__nombre', 'bateriacarrera__carrera__carrera__nombre', 'bateriacarrera__malla__malla__nombre').distinct('bateriacarrera'))
                        gruposbateria = GrupoExamenConfiguracion.objects.filter(status=True, grupoexamen=grupo)
                        data['grupos'] = lista = [{'bateria': i, 'ajustes': (GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=i)), 'estudiantes': (GrupoExamenEstudiante.objects.filter(status=True, grupoexamenconfiguracion=i))} for i in gruposbateria]
                        return render(request, "adm_examencomplexivo/add_grupoexamenconfiguracion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_grupoexamenconfiguracion':
                    try:
                        grupo = GrupoExamen.objects.get(pk=int(request.GET['id']))
                        data['grupos'] = estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamen=grupo)
                        return render(request, "adm_examencomplexivo/adm_grupoexamenconfiguracion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_delegadoexamen':
                    try:
                        data['title'] = "Delegados de examen compexivo"
                        data['grupo'] = grupo = GrupoExamen.objects.get(pk=int(request.GET['id']))
                        data['form'] = DelegadoExamenForm()
                        data['delegados'] = delegados = GrupoExamenDelegado.objects.filter(status=True, grupoexamen=grupo)
                        return render(request, "adm_examencomplexivo/add_delegadoexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_impugnacion':
                    try:
                        data['title'] = 'Impugnaciones de examen complexivo'
                        data['impugnaciones'] = impugnaciones = ImpugnacionExamen.objects.filter(status=True).order_by('-periodo')
                        return render(request, "adm_examencomplexivo/adm_impugnacion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_impugnacion':
                    try:
                        data['title'] = 'Revisión de examen'
                        data['impugnacion'] = impugnacion = ImpugnacionExamen.objects.get(pk=int(request.GET['id']))
                        impugnaciones = ImpugnacionDetalle.objects.filter(status=True, impugnacion=impugnacion)
                        lista = []
                        for i in impugnaciones:
                            if i.reactivo:
                                lista.append(EstudianteExamenReactivo.objects.get(pk=i.reactivo.id))
                            elif i.area:
                                lista.extend(EstudianteExamenReactivo.objects.filter(status=True, bateriadetalle__reactivo__asignaciondocente__area=i.area))
                            else:
                                lista.extend(EstudianteExamenReactivo.objects.filter(status=True, bateriadetalle__reactivo__asignaciondocente__asignatura=i.asignatura))
                        reactivos = []
                        for i in lista:
                            extra = []
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo=None).order_by('id').values('texto', 'archivo', 'id'))
                            if i.bateriadetalle.reactivo.tipopregunta.nombre != "EMPAREJAMIENTO":
                                listopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion_id=a['id']).exists()} for a in opciones]
                                opciones = listopciones
                            else:
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                extra = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
                                listopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for i in opciones]
                                for i in listopciones:
                                    detalle = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion=i['id']).exists()
                                    if detalle:
                                        i['vali'] = True
                                        detalle = DetalleEstudianteExamen.objects.get(status=True, reactivo=i, opcion=i['id'])
                                        texto = DetalleReactivoDocente.objects.get(pk=int(detalle.emparejamiento))
                                        i['id2'] = str(texto.id)
                                        i['texto2'] = texto.texto.split(';')[1]
                                opciones = listopciones
                            if i.bateriadetalle.reactivo.asignaciondocente.asignatura:
                                nombre = i.bateriadetalle.reactivo.asignaciondocente.asignatura.asignatura.nombre
                            else:
                                nombre = i.bateriadetalle.reactivo.asignaciondocente.area.nombre
                            reactivos.append({'nombre':nombre,'tipopregunta': i.bateriadetalle.reactivo.tipopregunta.nombre, 'atributos': atributos, 'opciones': opciones, 'extra': extra})
                        data['reactivos'] = reactivos
                        return render(request, "adm_examencomplexivo/edit_impugnacion.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'ver_bateriageneral':
                    try:
                        data['title'] = 'BATERIA GENERAL'
                        data['bateria'] = bateria = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        vali = BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateria, tiporeactivo__nombre="GENERAL").exists()
                        if vali:
                            data['bateriaexamen'] = bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, bateriacarrera=bateria, tiporeactivo__nombre="GENERAL")
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values(
                                'reactivo__asignaciondocente__area', 'reactivo__asignaciondocente__area__nombre').order_by(
                                'reactivo__asignaciondocente__area').distinct())
                            lista = [{'id': i['reactivo__asignaciondocente__area'],
                                      'area': i['reactivo__asignaciondocente__area__nombre'],
                                      'reactivos': BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__area=int(i['reactivo__asignaciondocente__area'])).count()}
                                     for i in reactivos]
                            data['reactivos'] = lista
                        return render(request, 'adm_examencomplexivo/ver_bateriageneral.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'ver_detallebateriageneral':
                    try:

                        area = ReactivoArea.objects.get(pk=int(request.GET['idarea']))
                        data['title'] = "REACTIVOS DE " + area.nombre
                        data['bateria'] = bateriacarrera = BateriaCarrera.objects.get(pk=int(request.GET['id']))
                        reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriacarrera, reactivo__asignaciondocente__area=area).values('reactivo_id', 'reactivo__tipopregunta__nombre', 'reactivo__aleatorio', 'reactivo__nota').order_by('reactivo_id'))
                        listado = []
                        for i in reactivos:
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo_id=i['reactivo_id'], atributo=None).order_by('id').values('texto', 'archivo'))
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo_id=i['reactivo_id'], atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            listopciones = []
                            if i['reactivo__tipopregunta__nombre'] == "EMPAREJAMIENTO":
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                index = 0
                                for a in aleatorio:
                                    listopciones.append({'texto': opciones[index]['texto'].split(';')[0], 'texto2': opciones[a]['texto'].split(';')[1], 'archivo': opciones[index]['archivo']})
                                    index += 1
                                opciones = listopciones
                            elif i['reactivo__tipopregunta__nombre'] == "OPCION MULTIPLE" and i['reactivo__aleatorio']:
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                listopciones = [{'texto': opciones[a]['texto'], 'archivo': opciones[a]['archivo']} for a in aleatorio]
                                opciones = listopciones
                            listado.append({'reactivo': i['reactivo_id'], 'aleatorio': i['reactivo__aleatorio'], 'tipo': i['reactivo__tipopregunta__nombre'], 'nota': i['reactivo__nota'], 'opciones': opciones, 'atributos': atributos})
                        data['reactivos'] = listado
                        data['tipo'] = "detalle"
                        return render(request, 'adm_examencomplexivo/ver_bateriageneraldetalle.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'ver_examen':
                    try:
                        data['title'] = 'Examen complexivo'
                        data['estudiante'] = estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.GET['id']))
                        lista = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante= estudiante)
                        reactivos = []
                        for i in lista:
                            extra = []
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo=None).order_by('id').values('texto', 'archivo', 'id'))
                            if i.bateriadetalle.reactivo.tipopregunta.nombre != "EMPAREJAMIENTO":
                                listopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion_id=a['id']).exists()} for a in opciones]
                                opciones = listopciones
                            else:
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                extra = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
                                listopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for i in opciones]
                                for i in listopciones:
                                    detalle = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion=i['id']).exists()
                                    if detalle:
                                        i['vali'] = True
                                        detalle = DetalleEstudianteExamen.objects.get(status=True, reactivo=i, opcion=i['id'])
                                        texto = DetalleReactivoDocente.objects.get(pk=int(detalle.emparejamiento))
                                        i['id2'] = str(texto.id)
                                        i['texto2'] = texto.texto.split(';')[1]
                                opciones = listopciones
                            if i.bateriadetalle.reactivo.asignaciondocente.asignatura:
                                nombre = i.bateriadetalle.reactivo.asignaciondocente.asignatura.asignatura.nombre
                            else:
                                nombre = i.bateriadetalle.reactivo.asignaciondocente.area.nombre
                            reactivos.append({'nombre':nombre,'tipopregunta': i.bateriadetalle.reactivo.tipopregunta.nombre, 'atributos': atributos, 'opciones': opciones, 'extra': extra})
                        data['reactivos'] = reactivos
                        return render(request, "adm_examencomplexivo/ver_examen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_reportexamen':
                    try:
                        data['user'] = request.session['user']
                        data['title'] = 'REPORTE DE EXAMEN COMPLEXIVO'
                        data['examen'] = examen = CronogramaExamen.objects.get(pk=int(request.GET['id']))
                        estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamen__cronogramaexamen=examen).order_by('estudiante__inscripcion__persona__apellido1','estudiante__inscripcion__persona__apellido2','estudiante__inscripcion__persona__nombres')
                        lista = [{'estudiante':i, 'grupo': i.grupoexamen, 'general':None, 'especifico':None, 'calificacion':None, 'resultado':None} for i in estudiantes]
                        for i in lista:
                            notagen = 0
                            notaesp = 0
                            actual = 0
                            reactivos = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=i['estudiante'], estado=True)
                            total = (reactivos.aggregate(total=Sum('bateriadetalle__reactivo__nota')))['total']
                            maximo = i['estudiante'].grupoexamen.notamax
                            for g in reactivos:
                                nota = g.bateriadetalle.reactivo.nota
                                countopciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=g.bateriadetalle.reactivo, activo=True).count()
                                valiopciones = g.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.valiopciones
                                index = 0
                                opciones = DetalleEstudianteExamen.objects.filter(status=True, reactivo=g, opcion__activo=True)
                                tipo = g.bateriadetalle.reactivo.tipopregunta.nombre
                                cal = 0
                                if tipo == "EMPAREJAMIENTO":
                                    for o in opciones:
                                        if o.emparejamiento == str(o.opcion_id):
                                            cal += ((o.opcion.valorporcentual * nota) / 100)
                                            index += 1
                                else:
                                    for o in opciones:
                                        cal += ((o.opcion.valorporcentual * nota) / 100)
                                        index += 1
                                if valiopciones:
                                    if index == countopciones:
                                        actual += cal
                                    else:
                                        cal = 0
                                else:
                                    actual += cal
                                if g.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.tiporeactivo.nombre == "GENERAL" and cal != 0:
                                    notagen += 1
                                elif g.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.tiporeactivo.nombre == "ESPECIFICO" and cal != 0:
                                    notaesp += 1
                            i['calificacion'] = round((actual * maximo) / total,2)
                            i['general'] = notagen
                            i['especifico'] = notaesp
                        data['examenes'] = lista
                        return render(request, "adm_examencomplexivo/adm_reportexamen.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                else:
                    raise Http404('Error: Página no encontrada')
        else:
            return HttpResponseRedirect('/')
