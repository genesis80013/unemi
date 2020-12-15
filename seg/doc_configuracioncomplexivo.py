import json
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse, HttpResponse
from django.template import Context, loader
from seg.forms import *
from seg.models import *
from seg.views import *
from django.db import transaction
from django.http import Http404
from seg.funciones import similitud, validarImagen, valiTimeDelegado
from django.db.models import Sum
from seg.funciones import validarfechamayor, validarrangofechas

#@login_required(redirect_field_name='ret', login_url='/')
@transaction.atomic()
def view(request):
    data = {}
    data['permite_modificar'] = True
    if 'user' in request.session:
        if request.method == 'POST':
            if 'action' in request.POST:
                action = request.POST['action']
                if action == 'add_reactivodocente':
                    try:
                        vali = request.POST['valiopciones']
                        vali2 = request.POST['validetalles']
                        if vali == "1" and vali2 == "1" and 'nota' in request.POST and 'tipopregunta' in request.POST:
                            asignacion = AsignacionDocenteReactivo.objects.get(pk=int(request.POST['id']))
                            if asignacion.revision is True:
                                return JsonResponse({"result": "error", "mensaje": 'Acceso denegado.'})
                            cronograma = CronogramaPlanificacionExamen.objects.get(periodo=asignacion.asignacion.periodo, status=True)
                            porcentaje = cronograma.porcsimilitud
                            tipo = asignacion.formato.formatoreactivo.tiporeactivo.nombre.lower()
                            atributos = json.loads(request.POST['lista_items1'])
                            opciones = json.loads(request.POST['lista_items2'])
                            tipopregunta = request.POST['tipopregunta']
                            aleatorio = False
                            if 'aleatorio' in request.POST:
                                aleatorio = True
                            nota = float(request.POST['nota'])
                            if nota >= asignacion.formato.formatoreactivo.notamin and nota <= asignacion.formato.formatoreactivo.notamax:
                                texto = ""
                                if tipopregunta == "vf":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                elif tipopregunta == "om":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                    for i in opciones:
                                        texto += i['texto'] + " "
                                elif tipopregunta == "em":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                    for i in opciones:
                                        texto += i['textoa'] + " " + i['textob'] + " "
                                listado = [texto]
                                if tipo == "general":
                                    reactivos = ReactivoDocente.objects.filter(status=True, tipopregunta__abreviatura=tipopregunta, asignaciondocente__area=asignacion.area, asignaciondocente__status=True)
                                else:
                                    reactivos = ReactivoDocente.objects.filter(status=True, tipopregunta__abreviatura=tipopregunta, asignaciondocente__status=True, asignaciondocente__asignatura=asignacion.asignatura)
                                for r in reactivos:
                                    lista = DetalleReactivoDocente.objects.filter(status=True, reactivo=r).exclude(atributo=None)
                                    texto = ""
                                    for a in lista:
                                        texto += a.texto + " "
                                    if r.tipopregunta.abreviatura == "om" or r.tipopregunta.abreviatura == "em":
                                        lista2 = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None)
                                        for a in lista2:
                                            texto += a.texto + " "
                                    listado.append(texto)
                                sim = similitud(listado, porcentaje)
                                if sim:
                                    mensaje = 'El reactivo que ingreso tiene un total de ' + sim['csim'].__str__() + '% en similitud con otro reactivo ingresado posteriormente'
                                    return JsonResponse({"result": "error", "mensaje": mensaje})
                                else:
                                    tipopregunta = TipoPreguntaReactivo.objects.get(status=True, abreviatura=tipopregunta)
                                    reactivo = ReactivoDocente(asignaciondocente=asignacion, tipopregunta=tipopregunta, aleatorio=aleatorio, nota=nota, estadoinicial=True, estadofinal=None, observacion=None)
                                    reactivo.save()
                                    for l in atributos:
                                        atributo = AtributoReactivo.objects.get(pk=int(l['idatributo']))
                                        imagen = None
                                        if l['imagen'] in request.FILES:
                                            imagen = validarImagen(request.FILES[l['imagen']])
                                        texto = l['texto']
                                        atributoreactivo = DetalleReactivoDocente(reactivo=reactivo, atributo=atributo, texto=texto, archivo=imagen)
                                        atributoreactivo.save()
                                    for l in opciones:
                                        imagen = None
                                        if l['imagen'] in request.FILES:
                                            imagen = validarImagen(request.FILES[l['imagen']])
                                        texto = l['texto']
                                        valor = float(l['valor'])
                                        resp = l['vali']
                                        atributoreactivo = DetalleReactivoDocente(reactivo=reactivo, atributo=None, texto=texto, archivo=imagen, valorporcentual=valor, activo=resp)
                                        atributoreactivo.save()
                                    reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion).count()
                                    if reactivos >= asignacion.cantidad and asignacion.estadofinal is False:
                                        asignacion.estadofinal = True
                                        asignacion.save()
                                    return JsonResponse({"result": "ok"})
                            else:
                                return JsonResponse({"result": "error", "mensaje": 'Calificación incorrecta.'})
                        else:
                            if vali == "0":
                                return JsonResponse({"result": "error","mensaje": 'Verificar que las opciones cumplan con el formato requerido.'})
                            elif vali2 == "0":
                                return JsonResponse({"result": "error", "mensaje": 'Error al enviar los datos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_reactivodocente':
                    try:
                        vali = request.POST['valiopciones']
                        vali2 = request.POST['validetalles']
                        if vali == "1" and vali2 == "1" and 'nota' in request.POST:
                            reactivo = ReactivoDocente.objects.get(pk=int(request.POST['id']))
                            if reactivo.estadofinal is True:
                                return JsonResponse({"result": "error", "mensaje": 'No se puede editar, reactivo esta aprobado.'})
                            cronograma = CronogramaPlanificacionExamen.objects.get(periodo=reactivo.asignaciondocente.asignacion.periodo, status=True)
                            porcentaje = cronograma.porcsimilitud
                            tipo = reactivo.asignaciondocente.formato.formatoreactivo.tiporeactivo.nombre.lower()
                            atributos = json.loads(request.POST['lista_items1'])
                            opciones = json.loads(request.POST['lista_items2'])
                            tipopregunta = reactivo.tipopregunta.abreviatura.lower()
                            aleatorio = False
                            if 'aleatorio' in request.POST:
                                aleatorio = True
                            nota = float(request.POST['nota'])
                            if nota >= reactivo.asignaciondocente.formato.formatoreactivo.notamin and nota <= reactivo.asignaciondocente.formato.formatoreactivo.notamax:
                                texto = ""
                                if tipopregunta == "vf":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                elif tipopregunta == "om":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                    for i in opciones:
                                        texto += i['texto'] + " "
                                elif tipopregunta == "em":
                                    for i in atributos:
                                        texto += i['texto'] + " "
                                    for i in opciones:
                                        texto += i['textoa'] + " " + i['textob'] + " "
                                listado = [texto]
                                if tipo == "general":
                                    reactivos = ReactivoDocente.objects.filter(status=True, tipopregunta__abreviatura=tipopregunta, asignaciondocente__area=reactivo.asignaciondocente.area, asignaciondocente__status=True).exclude(pk=reactivo.id)[:450]
                                else:
                                    reactivos = ReactivoDocente.objects.filter(status=True, tipopregunta__abreviatura=tipopregunta, asignaciondocente__status=True, asignaciondocente__asignatura=reactivo.asignaciondocente.asignatura).exclude(pk=reactivo.id)[:450]
                                for r in reactivos:
                                    lista = DetalleReactivoDocente.objects.filter(status=True, reactivo=r).exclude(atributo=None)
                                    texto = ""
                                    for a in lista:
                                        texto += a.texto + " "
                                    if r.tipopregunta.abreviatura == "om" or r.tipopregunta.abreviatura == "em":
                                        lista2 = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None)
                                        for a in lista2:
                                            texto += a.texto + " "
                                    listado.append(texto)
                                sim = similitud(listado, porcentaje)
                                if sim:
                                    mensaje = 'El reactivo que ingreso tiene un total de ' + sim['csim'].__str__() + '% en similitud con otro reactivo ingresado posteriormente'
                                    return JsonResponse({"result": "error", "mensaje": mensaje})
                                else:
                                    reactivo.nota = nota
                                    reactivo.aleatorio = aleatorio
                                    reactivo.save()
                                    for l in atributos:
                                        if l['action'] == 'edit':
                                            atributo = DetalleReactivoDocente.objects.get(id=l['idatributo'])
                                            imagen = None
                                            if l['imagen'] in request.FILES:
                                                imagen = validarImagen(request.FILES[l['imagen']])
                                            texto = l['texto']
                                            atributo.texto = texto
                                            atributo.archivo = imagen
                                            atributo.save()
                                    eliminados = json.loads(request.POST['lista_items3'])
                                    for l in eliminados:
                                        detalle = DetalleReactivoDocente.objects.get(pk=int(l['idopcion']))
                                        detalle.status = False
                                        detalle.save()
                                    for l in opciones:
                                        imagen = None
                                        if l['imagen'] in request.FILES:
                                            imagen = validarImagen(request.FILES[l['imagen']])
                                        texto = l['texto']
                                        valor = float(l['valor'])
                                        resp = l['vali']
                                        if l['action'] == "add":
                                            atributoreactivo = DetalleReactivoDocente(reactivo=reactivo, atributo=None, texto=texto, archivo=imagen, valorporcentual=valor, activo=resp)
                                            atributoreactivo.save()
                                        elif l['action'] == 'edit':
                                            atributoreactivo = DetalleReactivoDocente.objects.get(pk=int(l['idopcion']))
                                            atributoreactivo.texto = texto
                                            atributoreactivo.valorporcentual = valor
                                            atributoreactivo.activo = resp
                                            atributoreactivo.save()

                                    return JsonResponse({"result": "ok"})
                            else:
                                return JsonResponse({"result": "error", "mensaje": 'Calificación incorrecta.'})
                        else:
                            if vali == "0":
                                return JsonResponse({"result": "error", "mensaje": 'Verificar que las opciones cumplan con el formato requerido.'})
                            elif vali2 == "0":
                                return JsonResponse({"result": "error", "mensaje": 'Error al enviar los datos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'del_reactivodocente':
                    try:
                        reactivo = ReactivoDocente.objects.get(pk=int(request.POST['id']))
                        opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo)
                        for p in opciones:
                            p.status=False
                            p.save()
                        reactivo.status=False
                        reactivo.save()
                        reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=reactivo.asignaciondocente).count()
                        if reactivos < reactivo.asignaciondocente.cantidad:
                            asignacion = reactivo.asignaciondocente
                            asignacion.estadofinal = False
                            asignacion.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_similitud':
                    try:
                        if 'idasignaturamalla' in request.POST:
                            asignaturamalla = AsignaturaMalla.objects.get(pk=int(request.POST['idasignaturamalla']))
                            reactivos = list(ReactivoDocente.objects.filter(status=True, asignaciondocente__asignatura=asignaturamalla))
                        else:
                            area = ReactivoArea.objects.get(pk=int(request.POST['idarea']))
                            reactivos = list(ReactivoDocente.objects.filter(status=True, asignaciondocente__area=area))
                        preguntas = [request.POST['texto']]
                        for r in reactivos:
                            lista = DetalleReactivoDocente.objects.filter(status=True, reactivo=r).exclude(atributo=None)
                            texto = ""
                            for a in lista:
                                texto += a.texto + " "
                            if r.tipopregunta.abreviatura == "om" or r.tipopregunta.abreviatura == "em":
                                lista2 = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None)
                                for a in lista2:
                                    texto += a.texto + " "
                            preguntas.append(texto)
                        if 'porcentaje' in request.POST:
                            porcentaje = request.POST['porcentaje'].replace(',', '.')
                            porcentaje = int(porcentaje)
                        else:
                            porcentaje = 50
                        sim = similitud(preguntas, porcentaje)
                        if sim:
                            mensaje = 'El reactivo que ingreso tiene un total de ' + sim['csim'].__str__() + '% en similitud con otro reactivo ingresado posteriormente'
                            reactivo = reactivos[int(sim['index']-1)]
                            reactivo = {'atributos': list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo).exclude(atributo=None).values('atributo__nombre','texto','archivo')),
                                        'opciones': list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo, atributo=None).values('texto','archivo'))}
                            return JsonResponse({"result": "error", "mensaje": mensaje,"reactivo":reactivo})
                        return JsonResponse({"result":"ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'adm_detallereactivo':
                    try:
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_estadoestudiante':
                    try:
                        delegado = GrupoExamenDelegado.objects.get(pk=int(request.POST['id']))
                        grupo = delegado.grupoexamen
                        datos = json.loads(request.POST['lista_items1'])
                        for d in datos:
                            estudiante = GrupoExamenEstudiante.objects.get(pk=int(d['id']))
                            if estudiante.grupoexamen == grupo:
                                estudiante.activo = d['activo']
                                estudiante.observacion = d['observacion']
                                estudiante.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                else:
                    return JsonResponse({"result": "bad", "mensaje": u"Página no encontrada."})
            else:
                return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
        else:
            if 'action' in request.GET:
                action = request.GET['action']
                if action == 'adm_reactivo':
                    try:
                        return view_reactivo(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_reactivodocente':
                    try:
                        if 'id' in request.GET:
                            asignacion = AsignacionDocenteReactivo.objects.get(pk=int(request.GET['id']))
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre == "GENERAL":
                                data['title'] = "REACTIVOS - " + asignacion.area.nombre
                                data['tipo'] = "general"
                            else:
                                data['title'] = "REACTIVOS - " + asignacion.asignatura.asignatura.nombre
                                data['tipo'] = "especifico"
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion)
                            lista = []
                            for r in reactivos:
                                atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo__profvisible=True).exclude(atributo=None).order_by('atributo_id')
                                opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None).order_by('id')
                                if len(lista) == 0:
                                    lista = [{'reactivo': r, 'atributos': atributos, 'opciones': opciones}]
                                else:
                                    lista.append({'reactivo': r, 'atributos': atributos, 'opciones': opciones})
                            data['reactivos'] = lista
                            return render(request, "doc_examencomplexivo/adm_reactivodocente.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_reactivodocente':
                    try:
                        data['user'] = user = request.session['user']
                        data['porcentaje'] = CronogramaPlanificacionExamen.objects.get(periodo__activo=True, status=True).porcsimilitud
                        data['asignacion'] = asignacion = AsignacionDocenteReactivo.objects.get(pk=int(request.GET['id']))
                        data['title'] = "CRONOGRAMA PARA " + asignacion.asignacion.periodo.nombre
                        data['reactivos'] = reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion).order_by('id').values('id', 'estadofinal', 'observacion')
                        data['atributos'] = atributos = AtributoReactivo.objects.filter(status=True, profvisible=True, estado=True, formatoreactivo=asignacion.formato.formatoreactivo).order_by('id')
                        data['tipopreguntas'] = tipos = TipoPreguntaReactivo.objects.filter(status=True, activo=True).order_by('nombre')
                        data['rango'] = range(asignacion.formato.formatoreactivo.opcionesmax)
                        return render(request, "doc_examencomplexivo/add_reactivodocente.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_reactivodocente':
                    try:
                        data['user'] = user = request.session['user']
                        data['reactivo'] = reactivo = ReactivoDocente.objects.get(pk=int(request.GET['id']))
                        data['asignacion'] = asignacion = AsignacionDocenteReactivo.objects.get(pk=int(reactivo.asignaciondocente.id))
                        data['title'] = "CRONOGRAMA PARA " + asignacion.asignacion.periodo.nombre
                        data['reactivos'] = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion).order_by('id').values('id', 'estadofinal', 'observacion')
                        data['atributos'] = atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo).exclude(atributo=None).order_by('id')
                        data['listado'] = opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo, atributo=None).order_by('id')
                        if reactivo.tipopregunta.abreviatura == "om":
                            rango = range(asignacion.formato.formatoreactivo.opcionesmax)
                            index = 0
                            lista = []
                            for r in rango:
                                if index < len(opciones):
                                    if len(lista) == 0:
                                        lista = [{'index': r, 'opcion': opciones[index]}]
                                    else:
                                        lista.append({'index': r, 'opcion': opciones[index]})
                                else:
                                    lista.append({'index': r, 'opcion': None})
                                index = index + 1
                            data['opciones'] = lista
                        elif reactivo.tipopregunta.abreviatura == "em":
                            rango = range(asignacion.formato.formatoreactivo.opcionesmax)
                            index = 0
                            lista = []
                            for r in rango:
                                if index < len(opciones):
                                    text1 = opciones[index].texto.split(';')[0]
                                    text2 = opciones[index].texto.split(';')[1]
                                    if len(lista) == 0:
                                        lista = [{'index': r, 'opcion': opciones[index], 'textoa': text1, 'textob': text2}]
                                    else:
                                        lista.append({'index': r, 'opcion': opciones[index], 'textoa': text1, 'textob': text2})
                                else:
                                    lista.append({'index': r, 'opcion': None})
                                index = index + 1
                            data['opciones'] = lista
                        else:
                            data['opciones'] = opciones
                        return render(request, "doc_examencomplexivo/edit_reactivodocente.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'del_reactivodocente':
                    try:
                        data['title'] = u'Eliminar Reactivo'
                        data['reactivo'] = reactivo = ReactivoDocente.objects.get(pk=int(request.GET['id']))
                        if reactivo.asignaciondocente.formato.formatoreactivo.tiporeactivo.nombre.lower() == "general":
                            data['nombre'] = reactivo.asignaciondocente.area
                        else:
                            data['nombre'] = reactivo.asignaciondocente.asignatura.asignatura
                        return render(request, "doc_examencomplexivo/del_reactivodocente.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallereactivo':
                    try:
                        data['title'] = 'REVISION DE REACTIVOS'
                        data['asignacion'] = asignacion = AsignacionDocenteReactivo.objects.get(pk=int(request.GET['id']))
                        data['reactivos'] = reactivos = reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion).order_by('id')
                        if 'idr' in request.GET:
                            index = int(request.GET['idr'])
                            data['actual'] = actual = reactivos[index]
                            if index < len(reactivos) - 1:
                                data['next'] = index+1
                            elif index < len(reactivos):
                                data['next'] = -1
                        else:
                            data['actual'] = actual = reactivos.first()
                            data['next'] = 1
                        data['atributos'] = atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=actual).exclude(atributo=None).order_by('id')
                        data['opciones'] = opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=actual, atributo=None).order_by('id')
                        if reactivos.count() <= 1:
                            data['next'] = -1
                        return render(request, "doc_examencomplexivo/adm_detallereactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_delegadoexamen':
                    try:
                        data['title'] = u'Examen complexivo'
                        data['user'] = user = request.session['user']
                        periodo = Periodo.objects.filter(status=True, activo=True).exists()
                        if has_group(user, "UPA"):
                            if periodo:
                                periodo = Periodo.objects.get(status=True, activo=True)
                                grupos = GrupoExamenDelegado.objects.filter(status=True, grupoexamen__cronogramaexamen__periodo=periodo, principal=True)
                                data['grupos'] =  lista = [{'grupo': i, 'vali': valiTimeDelegado(i.grupoexamen.fecha, i.grupoexamen.inicio, i.grupoexamen.fin)} for i in grupos]
                        else:
                            if periodo:
                                periodo = Periodo.objects.get(status=True, activo=True)
                                persona = Persona.objects.get(pk=int(user.id))
                                docente = Profesor.objects.get(status=True, persona=persona)
                                grupos = GrupoExamenDelegado.objects.filter(status=True, docente=docente, grupoexamen__cronogramaexamen__periodo=periodo, principal=True)
                                data['grupos'] = lista = [{'grupo': i, 'vali': valiTimeDelegado(i.grupoexamen.fecha, i.grupoexamen.inicio, i.grupoexamen.fin)} for i in grupos]
                        return render(request,'doc_examencomplexivo/adm_delegadoexamen.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_examenestudiante':
                    try:
                        if 'id' in request.GET:
                            data['delegado'] = delegado = GrupoExamenDelegado.objects.get(pk=int(request.GET['id']))
                            data['grupo'] = grupo = delegado.grupoexamen
                            data['title'] = 'Estudiantes de examen complexivo'
                            data['carrera'] = grupo.cronogramaexamen.carrera.carrera
                            data['estudiantes'] = estudiantes = GrupoExamenEstudiante.objects.filter(status=True, grupoexamen=grupo)
                            data['destino'] = "/doc_configuracioncomplexivo?action=adm_delegadoexamen"
                            return render(request, "doc_examencomplexivo/edit_examenestudiante.html", data)
                        else:
                            return HttpResponseRedirect('/')
                    except Exception as ex:
                        raise Http404("Error: Consulte con el administrador")
                elif action == 'adm_similitud':
                    try:
                        data['title'] = 'SIMILITUD DE REACTIVOS'
                        data['user'] = user = request.session['user']
                        persona = Persona.objects.get(pk=user.id)
                        docente = Profesor.objects.filter(persona=persona, status=True).exists()
                        periodo = Periodo.objects.filter(status=True, activo=True).exists()
                        if docente and periodo:
                            profesor = Profesor.objects.get(persona=persona, status=True)
                            periodo = Periodo.objects.get(status=True, activo=True)
                            data['asignaturas'] = asignaturas = ProfesorMateria.objects.filter(status=True, profesor=profesor, materia__nivel__periodo=periodo).values('materia__asignaturamalla', 'materia__asignaturamalla__asignatura__nombre','materia__asignaturamalla__malla__carrera__nombre').distinct()
                        return render(request, "doc_examencomplexivo/adm_similitud.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                else:
                    raise Http404('Error: Página no encontrada')
            else:
                raise Http404('Error: Página no encontrada')
    else:
        return HttpResponseRedirect('/')