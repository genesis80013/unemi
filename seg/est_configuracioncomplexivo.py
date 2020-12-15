import json
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from seg.forms import *
from seg.models import *
from seg.views import *
from seg.funciones import valiTime
from seg.reportes import est_reportbateria
from django.db import transaction
from django.http import Http404
from django.db.models import Sum, Count
from datetime import datetime
import random
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
                if action == 'add_examencomplexivo':
                    try:
                        data['grupoestudiante'] = grupoestudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['id']))
                        vali = valiTime(grupoestudiante.grupoexamen.fecha, grupoestudiante.grupoexamen.inicio,grupoestudiante.grupoexamen.fin)  ##validar el tiempo y si es el usuario
                        if vali:
                            if grupoestudiante.activo:
                                if grupoestudiante.estadoinicial is False:  ##entra por primera vez
                                    if grupoestudiante.grupoexamenconfiguracion == None:
                                        #es por grupo
                                        bateria = BateriaEstudiante.objects.get(matricula=grupoestudiante.estudiante, status=True, periodo=grupoestudiante.grupoexamen.cronogramaexamen.periodo).bateriacarrera
                                        cantidad = grupoestudiante.grupoexamen.cantidad
                                        reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).order_by('reactivo_id'))
                                        aleatorio = sample(range(0, len(reactivos)), int(cantidad))
                                        for a in aleatorio:
                                            ##guardar reactivo en BD
                                            reactivo = EstudianteExamenReactivo(grupoexamenestudiante=grupoestudiante, bateriadetalle=reactivos[a], estado=False)
                                            reactivo.save()
                                    else:
                                        if grupoestudiante.grupoexamenconfiguracion.tiposeleccion == 1 and grupoestudiante.grupoexamenconfiguracion.filtroseleccion == 1:  # aleatoriocompleto
                                            bateria = grupoestudiante.grupoexamenconfiguracion.bateria
                                            cantidad = grupoestudiante.grupoexamenconfiguracion.grupoexamen.cantidad
                                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).order_by('reactivo_id'))
                                            aleatorio = sample(range(0, len(reactivos)), int(cantidad))
                                            for a in aleatorio:
                                                ##guardar reactivo en BD
                                                reactivo = EstudianteExamenReactivo(grupoexamenestudiante=grupoestudiante, bateriadetalle=reactivos[a], estado=False)
                                                reactivo.save()
                                        elif grupoestudiante.grupoexamenconfiguracion.tiposeleccion == 1 and grupoestudiante.grupoexamenconfiguracion.filtroseleccion == 2:  # aleatorioseccion
                                            bateria = grupoestudiante.grupoexamenconfiguracion.bateria
                                            cantidad = grupoestudiante.grupoexamenconfiguracion.grupoexamen.cantidad
                                            seccion = GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=grupoestudiante.grupoexamenconfiguracion)
                                            for r in seccion:
                                                if r.area:
                                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area=r.area).order_by('reactivo_id'))
                                                else:
                                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__asignatura=r.asignatura).order_by('reactivo_id'))
                                                aleatorio = sample(range(0, len(reactivos)), int(r.cantidad))
                                                for a in aleatorio:
                                                    ##guardar reactivo en BD
                                                    reactivo = EstudianteExamenReactivo(grupoexamenestudiante=grupoestudiante, bateriadetalle=reactivos[a], estado=False)
                                                    reactivo.save()
                                        elif grupoestudiante.grupoexamenconfiguracion.tiposeleccion == 2 and grupoestudiante.grupoexamenconfiguracion.filtroseleccion == 1:  # rangocompleto
                                            bateria = grupoestudiante.grupoexamenconfiguracion.bateria
                                            cantidad = grupoestudiante.grupoexamenconfiguracion.grupoexamen.cantidad
                                            seccion = GrupoConfiguracion.objects.get(status=True, grupoexamenconfiguracion=grupoestudiante.grupoexamenconfiguracion)
                                            inicio = seccion.rangoinicio
                                            fin = seccion.rangofin
                                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).order_by('reactivo_id'))
                                            reactivos = reactivos[inicio - 1:fin]
                                            aleatorio = sample(range(0, len(reactivos)), int(cantidad))
                                            for a in aleatorio:
                                                ##guardar reactivo en BD
                                                reactivo = EstudianteExamenReactivo(grupoexamenestudiante=grupoestudiante, bateriadetalle=reactivos[a], estado=False)
                                                reactivo.save()
                                        elif grupoestudiante.grupoexamenconfiguracion.tiposeleccion == 2 and grupoestudiante.grupoexamenconfiguracion.filtroseleccion == 2:  # rangoseccion
                                            bateria = grupoestudiante.grupoexamenconfiguracion.bateria
                                            cantidad = grupoestudiante.grupoexamenconfiguracion.grupoexamen.cantidad
                                            seccion = GrupoConfiguracion.objects.filter(status=True, grupoexamenconfiguracion=grupoestudiante.grupoexamenconfiguracion)
                                            for r in seccion:
                                                if r.area:
                                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area=r.area).order_by('reactivo_id'))
                                                else:
                                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__asignatura=r.asignatura).order_by('reactivo_id'))
                                                reactivos = reactivos[r.rangoinicio - 1: r.rangofin]
                                                aleatorio = sample(range(0, len(reactivos)), int(r.cantidad))
                                                for a in aleatorio:
                                                    ##guardar reactivo en BD
                                                    reactivo = EstudianteExamenReactivo(grupoexamenestudiante=grupoestudiante, bateriadetalle=reactivos[a], estado=False)
                                                    reactivo.save()
                                            data['index'] = 0
                                    reactivos = list(EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante).order_by('id'))
                                    grupoestudiante.estadoinicial = True
                                    grupoestudiante.save()
                                    return view_editexamencomplexivo(request, 0, reactivos, grupoestudiante)
                                else:
                                    if grupoestudiante.estadofinal is True:  # mostrar el detalle del examen
                                        return view_examencomplexivo(request, None)
                                    else:  ##mostrar donde se quedo
                                        reactivos = list(EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante).order_by('id'))
                                        ultimo = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante, estado=True).order_by('id').last()
                                        if ultimo is None:
                                            indice = 0
                                        else:
                                            indice = reactivos.index(ultimo) + 1
                                            if indice == len(reactivos):
                                                indice = indice - 1
                                        return view_editexamencomplexivo(request, indice, reactivos, grupoestudiante)
                            else:
                                return view_examencomplexivo(request, 'Solicitar acceso')
                        else:
                            return view_examencomplexivo(request, 'Error, Límite de tiempo excedido')
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return view_examencomplexivo(request, 'Ocurrio un problema contacte con el administrador.')
                elif action == 'edit_examencomplexivo':
                    try:
                        estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['idestudiante']))
                        vali = valiTime(estudiante.grupoexamen.fecha, estudiante.grupoexamen.inicio, estudiante.grupoexamen.fin)#validar si es fecha hora y si es el usuario
                        if vali:
                            if estudiante.activo:
                                reactivo = EstudianteExamenReactivo.objects.get(pk=int(request.POST['idactual']))
                                tipoexamen = request.POST['tipoexamen']
                                datos = json.loads(request.POST['lista_items1'])
                                eliminar = DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivo).exists()
                                if eliminar:
                                    eliminar = DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivo).delete()
                                ##add opciones
                                if tipoexamen == "EMPAREJAMIENTO":
                                    for i in datos:
                                        if i['vali'] is True:
                                            opcion = DetalleReactivoDocente.objects.get(pk=int(i['id1']))
                                            opcion2 = DetalleReactivoDocente.objects.get(pk=int(i['id2']))
                                            texto = opcion2.id.__str__()
                                            detalle = DetalleEstudianteExamen(reactivo=reactivo, opcion=opcion, emparejamiento=texto)
                                            detalle.save()
                                else:
                                    for i in datos:
                                        opcion = DetalleReactivoDocente.objects.get(pk=int(i['id1']))
                                        detalle = DetalleEstudianteExamen(reactivo=reactivo, opcion=opcion, emparejamiento='')
                                        detalle.save()
                                eliminar = DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivo).exists()
                                if eliminar:
                                    reactivo.estado = True
                                else:
                                    reactivo.estado = False
                                reactivo.save()
                                return JsonResponse({"result": "ok"})
                            else:
                                return JsonResponse({"result": "error", 'mensaje':'Acceso denegado, solicitar acceso.', 'tipo':2})
                        else:
                            return JsonResponse({"result": "error", 'mensaje': 'Límite de tiempo excedido.', 'tipo': 1})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.','tipo':3})
                elif action == 'next_examencomplexivo':
                    try:
                        estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['idestudiante']))
                        vali = valiTime(estudiante.grupoexamen.fecha, estudiante.grupoexamen.inicio, estudiante.grupoexamen.fin)  # validar si es fecha hora y si es el usuario
                        if vali:
                            index = int(request.POST['index']) + 1
                            reactivos = list(EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante).order_by('id'))
                            if index == len(reactivos):
                                data['title'] = 'EXAMEN COMPLEXIVO'
                                data['grupoestudiante'] = estudiante
                                data['reactivos'] = reactivos
                                data['count'] = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante, estado=True).count()
                                data['tipoexamen'] = tipo = int(request.POST['tipo'])
                                data['index'] = index
                                return render(request, 'est_examencomplexivo/add_confirmarexamen.html', data)
                            else:
                                return view_editexamencomplexivo(request, index, reactivos, estudiante)
                        else:
                            return view_examencomplexivo(request, 'Error, límite de tiempo excedido.')
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return view_examencomplexivo(request, 'Ocurrio un problema contacte con el administrador.')
                elif action == 'ant_examencomplexivo':
                    try:
                        estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['idestudiante']))
                        vali = valiTime(estudiante.grupoexamen.fecha, estudiante.grupoexamen.inicio, estudiante.grupoexamen.fin)#validar si es fecha hora y si es el usuario
                        if vali:
                            if estudiante.activo:
                                index = int(request.POST['index']) - 1
                                reactivos = list(EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante).order_by('id'))
                                return view_editexamencomplexivo(request, index, reactivos, estudiante)
                            else:
                                return view_examencomplexivo(request, 'Acceso denegado.')
                        else:
                            return view_examencomplexivo(request, 'Error, límite de tiempo excedido.')
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return view_examencomplexivo(request, 'Ocurrio un problema contacte con el administrador.')
                elif action == 'add_confirmarexamencomplexivo':
                    try:
                        estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['idestudiante']))
                        estudiante.estadofinal = True
                        estudiante.save()
                        data['user'] = request.session['user']
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return view_examencomplexivo(request, 'Ocurrio un problema contacte con el administrador.')
                elif action == 'add_simulacionexamen':
                    try:
                        bateria = BateriaCarrera.objects.get(pk=int(request.POST['bateria']))
                        matricula = MatriculaTitulacion.objects.get(pk=int(request.POST['matricula']))
                        area = request.POST['area']
                        cantidad = int(request.POST['cantidad'])
                        if area == "":
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria).order_by('reactivo_id'))
                        else:
                            tipo = area.split(';')[1]
                            id = int(area.split(';')[0])
                            if tipo == "g":
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__area_id=id).order_by('reactivo_id'))
                            else:
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateria, reactivo__asignaciondocente__asignatura_id=id).order_by('reactivo_id'))
                        if cantidad>len(reactivos):
                            cantidad = len(reactivos)
                        #guardar simulacion
                        if cantidad != 0:
                            simulacion = SimulacionExamen(matricula=matricula, bateriacarrera=bateria, cantidad=cantidad)
                            simulacion.save()
                            aleatorio = sample(range(0, len(reactivos)), int(cantidad))
                            for a in aleatorio:
                                ##guardar reactivo en BD
                                reactivo = SimulacionExamenReactivo(simulacion=simulacion, detallebateria=reactivos[a], estado=False)
                                reactivo.save()
                            return JsonResponse({'result':'ok', 'mensaje': simulacion.id, 'mensaje2': 0})
                        else:
                            return JsonResponse({'result': 'error', 'mensaje': 'La bateria seleccionada no contiene reactivos'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_seccionbateria':
                    try:
                        bateriacarrera =BateriaCarrera.objects.get(pk=int(request.POST['idbateriacarrera']))
                        general = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriacarrera).exclude(reactivo__asignaciondocente__area=None).values('reactivo__asignaciondocente__area','reactivo__asignaciondocente__area__nombre').order_by('reactivo__asignaciondocente__area').distinct()
                        especifico = BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriacarrera).exclude(reactivo__asignaciondocente__asignatura=None).values('reactivo__asignaciondocente__asignatura','reactivo__asignaciondocente__asignatura__asignatura__nombre').order_by('reactivo__asignaciondocente__asignatura').distinct()
                        lista = [{'id':i['reactivo__asignaciondocente__area'], 'nombre': i['reactivo__asignaciondocente__area__nombre'], 'tipo':'g'} for i in general]
                        lista.extend({'id':i['reactivo__asignaciondocente__asignatura'], 'nombre': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'tipo':'e'} for i in especifico)
                        return JsonResponse({'result': 'ok', 'mensaje': lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_simulacionexamen':
                    try:
                        simulacion = SimulacionExamen.objects.get(pk=int(request.POST['id']))
                        reactivo = SimulacionExamenReactivo.objects.get(pk=int(request.POST['actual']))
                        tipoexamen = request.POST['tipoexamen']
                        datos = json.loads(request.POST['lista_items1'])
                        eliminar = SimulacionDetalle.objects.filter(status=True, reactivo=reactivo).exists()
                        if eliminar:
                            eliminar = SimulacionDetalle.objects.filter(status=True, reactivo=reactivo).delete()
                        #insertar opciones
                        if tipoexamen == "EMPAREJAMIENTO":
                            for i in datos:
                                if i['vali'] is True:
                                    opcion = DetalleReactivoDocente.objects.get(pk=int(i['id1']))
                                    opcion2 = DetalleReactivoDocente.objects.get(pk=int(i['id2']))
                                    texto = opcion2.id.__str__()
                                    detalle = SimulacionDetalle(reactivo=reactivo, opcion=opcion, emparejamiento=texto)
                                    detalle.save()
                        else:
                            for i in datos:
                                opcion = DetalleReactivoDocente.objects.get(pk=int(i['id1']))
                                detalle = SimulacionDetalle(reactivo=reactivo, opcion=opcion, emparejamiento='')
                                detalle.save()
                        eliminar = SimulacionDetalle.objects.filter(status=True, reactivo=reactivo).exists()
                        if eliminar:
                            reactivo.estado = True
                        else:
                            reactivo.estado = False
                        reactivo.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_impugnacion':
                    try:
                        estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.POST['id']))
                        periodo = estudiante.grupoexamen.cronogramaexamen.periodo
                        examen = estudiante.grupoexamen.cronogramaexamen
                        fecha = datetime.today()
                        descripcion = str(request.POST['descripcion'])
                        impugnacion = ImpugnacionExamen(periodo=periodo, examen=examen, grupoexamenestudiante=estudiante, descripcion=descripcion, fecha=fecha, estado=False)
                        impugnacion.save()
                        areas = json.loads(request.POST['areas'])
                        preguntas = json.loads(request.POST['preguntas'])
                        for a in areas:
                            if a['tipo'] == 'g':
                                area = ReactivoArea.objects.get(pk=int(a['id']))
                                asignatura = None
                            else:
                                area = None
                                asignatura = AsignaturaMalla.objects.get(pk=int(a['id']))
                            detalle = ImpugnacionDetalle(impugnacion=impugnacion, area=area, asignatura=asignatura, reactivo=None)
                            detalle.save()
                        for a in preguntas:
                            reactivo = EstudianteExamenReactivo.objects.get(pk=int(a['id']))
                            area = None
                            asignatura = None
                            detalle = ImpugnacionDetalle(impugnacion=impugnacion, area=area, asignatura=asignatura, reactivo=reactivo)
                            detalle.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
            else:
                return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
        else:
            return JsonResponse({"result": "session"})
    else:
        if 'action' in request.GET:
            if 'user' in request.session:
                action = request.GET['action']
                if action == 'adm_verbateria':
                    try:
                        data['title'] = 'Baterias de examen complexivo'
                        data['user'] = user = request.session['user']
                        persona = Persona.objects.get(pk=int(user.id))
                        if has_group(user, "UPA"):
                            data['actuales'] = actuales = BateriaEstudiante.objects.filter(status=True, periodo__activo=True).order_by('matricula__alternativa__facultad', 'matricula__alternativa__carrera')
                        else:
                            data['actuales'] = actuales = BateriaEstudiante.objects.filter(status=True, periodo__activo=True, matricula__inscripcion__persona=persona).order_by('matricula__alternativa__facultad', 'matricula__alternativa__carrera')
                        return render(request, "est_examencomplexivo/adm_verbateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallebateria':
                    try:
                        data['user'] = user = request.session['user']
                        data['actual'] = bateria = BateriaEstudiante.objects.get(pk=int(request.GET['id']))
                        data['title'] = 'BATERIA DE ' + bateria.bateriacarrera.bateria.periodo.nombre + ' CARRERA ' + bateria.bateriacarrera.carrera.carrera.nombre
                        baterias = list(BateriaExamenComplexivo.objects.filter(status=True, bateriacarrera=bateria.bateriacarrera))
                        lista = []
                        for b in baterias:
                            if b.tiporeactivo.nombre == "GENERAL":
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=b).values('reactivo__asignaciondocente__area__nombre','reactivo__asignaciondocente__area').order_by('reactivo__asignaciondocente__area__nombre').distinct())
                                lista.extend({'tipo': "GENERAL", 'id': i['reactivo__asignaciondocente__area'], 'nombre': i['reactivo__asignaciondocente__area__nombre'], 'cantidad': BateriaDetalle.objects.filter(status=True, bateria=b, reactivo__asignaciondocente__area__id=i['reactivo__asignaciondocente__area']).count()} for i in reactivos)
                            else:
                                reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=b).values('reactivo__asignaciondocente__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').order_by('reactivo__asignaciondocente__asignatura__asignatura__nombre').distinct())
                                lista.extend({'tipo': "ESPECIFICO", 'id': i['reactivo__asignaciondocente__asignatura'], 'nombre': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'cantidad': BateriaDetalle.objects.filter(status=True, bateria=b, reactivo__asignaciondocente__asignatura=i['reactivo__asignaciondocente__asignatura']).count()} for i in reactivos)
                        data['reactivos'] = lista
                        return render(request, "est_examencomplexivo/adm_detallebateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_verbateriareactivo':
                    try:
                        tipo = request.GET['tipo']
                        data['bateria'] = bateriaest = BateriaEstudiante.objects.get(pk=int(request.GET['id']))
                        if tipo == "GENERAL":
                            area = ReactivoArea.objects.get(pk=int(request.GET['idtip']))
                            nombre = area.nombre
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriaest.bateriacarrera, reactivo__asignaciondocente__area=area).values('reactivo_id', 'reactivo__aleatorio', 'reactivo__tipopregunta__nombre', 'reactivo__nota').order_by('reactivo_id'))
                        else:
                            asignatura = AsignaturaMalla.objects.get(pk=int(request.GET['idtip']))
                            nombre = asignatura.asignatura.nombre
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriaest.bateriacarrera, reactivo__asignaciondocente__asignatura=asignatura).values('reactivo_id', 'reactivo__aleatorio', 'reactivo__tipopregunta__nombre', 'reactivo__nota').order_by('reactivo_id'))
                        data['nombre'] = nombre
                        data['title'] = 'REACTIVOS DE ' + nombre
                        lista = []
                        for r in reactivos:
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=r['reactivo_id'], atributo=None).order_by('id').values('texto', 'archivo'))
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=r['reactivo_id'], atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            listopciones = []
                            if r['reactivo__tipopregunta__nombre'] == "EMPAREJAMIENTO":
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                index = 0
                                for a in aleatorio:
                                    listopciones.append({'texto': opciones[index]['texto'].split(';')[0], 'texto2': opciones[a]['texto'].split(';')[1], 'archivo': opciones[index]['archivo']})
                                    index += 1
                                opciones = listopciones
                            elif r['reactivo__tipopregunta__nombre'] == "OPCION MULTIPLE" and r['reactivo__aleatorio']:
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                for a in aleatorio:
                                    listopciones.append({'texto': opciones[a]['texto'], 'archivo': opciones[a]['archivo']})
                                opciones = listopciones
                            lista.append({'reactivo': r['reactivo_id'], 'aleatorio': r['reactivo__aleatorio'], 'tipo': r['reactivo__tipopregunta__nombre'], 'nota': r['reactivo__nota'], 'opciones': opciones, 'atributos': atributos})
                        data['reactivos'] = lista
                        return render(request, "est_examencomplexivo/adm_verbateriareactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_descargarbateria':
                    try:
                        user = request.session['user']
                        tipo = request.GET['tipo']
                        data['bateria'] = bateriaest = BateriaEstudiante.objects.get(pk=int(request.GET['id']))
                        if tipo == "GENERAL":
                            area = ReactivoArea.objects.get(pk=int(request.GET['idtip']))
                            nombre = area.nombre
                            reactivos = list(BateriaDetalle.objects.filter(status=True,  bateria__bateriacarrera=bateriaest.bateriacarrera, reactivo__asignaciondocente__area=area).values('reactivo_id', 'reactivo__aleatorio', 'reactivo__tipopregunta__nombre', 'reactivo__nota'))
                        else:
                            asignatura = AsignaturaMalla.objects.get(pk=int(request.GET['idtip']))
                            nombre = asignatura.asignatura.nombre
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria__bateriacarrera=bateriaest.bateriacarrera, reactivo__asignaciondocente__asignatura=asignatura).values('reactivo_id', 'reactivo__aleatorio', 'reactivo__tipopregunta__nombre', 'reactivo__nota').order_by('reactivo_id'))
                        data['nombre'] = nombre
                        lista = []
                        for r in reactivos:
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=r['reactivo_id'], atributo=None).order_by('id').values('texto', 'archivo'))
                            atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=r['reactivo_id'], atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                            listopciones = []
                            if r['reactivo__tipopregunta__nombre'] == "EMPAREJAMIENTO":
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                index = 0
                                for a in aleatorio:
                                    listopciones.append({'texto': opciones[index]['texto'].split(';')[0], 'texto2': opciones[a]['texto'].split(';')[1], 'archivo': opciones[index]['archivo']})
                                    index += 1
                                opciones = listopciones
                            elif r['reactivo__tipopregunta__nombre'] == "OPCION MULTIPLE" and r['reactivo__aleatorio']:
                                aleatorio = range(0, len(opciones))
                                aleatorio = random.sample(aleatorio, len(opciones))
                                for a in aleatorio:
                                    listopciones.append({'texto': opciones[a]['texto'], 'archivo': opciones[a]['archivo']})
                                opciones = listopciones
                            lista.append({'reactivo': r['reactivo_id'], 'aleatorio': r['reactivo__aleatorio'], 'tipo': r['reactivo__tipopregunta__nombre'], 'nota': r['reactivo__nota'], 'opciones': opciones, 'atributos': atributos})
                        data['reactivos'] = lista
                        return est_reportbateria(data['reactivos'], data['nombre'], bateriaest.bateriacarrera.carrera.carrera.nombre, bateriaest.bateriacarrera.carrera.carrera.facultad.nombre)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_examencomplexivo':
                    try:
                        return view_examencomplexivo(request,None)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detalleexamencomplexivo':
                    try:
                        grupoestudiante = GrupoExamenEstudiante.objects.get(pk=int(request.GET['id']))
                        minimo = grupoestudiante.grupoexamen.notamin
                        maximo = grupoestudiante.grupoexamen.notamax
                        reactivos = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante).order_by('bateriadetalle__bateria__tiporeactivo','bateriadetalle__reactivo__asignaciondocente__area','bateriadetalle__reactivo__asignaciondocente__asignatura')
                        total = (reactivos.aggregate(total=Sum('bateriadetalle__reactivo__nota')))['total']
                        #agrepar por secciones
                        grupoarea = list(reactivos.filter(bateriadetalle__bateria__tiporeactivo__nombre="GENERAL").exclude(bateriadetalle__bateria__tiporeactivo__nombre="ESPECIFICO").values('bateriadetalle__reactivo__asignaciondocente__area','bateriadetalle__reactivo__asignaciondocente__area__nombre').distinct())
                        grupoasignatura = reactivos.filter(bateriadetalle__bateria__tiporeactivo__nombre="ESPECIFICO").exclude(bateriadetalle__bateria__tiporeactivo__nombre="GENERAL").values('bateriadetalle__reactivo__asignaciondocente__asignatura','bateriadetalle__reactivo__asignaciondocente__asignatura__asignatura__nombre').distinct()
                        lista=[{'seccion': i['bateriadetalle__reactivo__asignaciondocente__area__nombre'],'puntaje':0, 'reactivos': EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante, estado=True, bateriadetalle__reactivo__asignaciondocente__area=i['bateriadetalle__reactivo__asignaciondocente__area'])} for i in grupoarea]
                        lista.extend({ 'seccion': i['bateriadetalle__reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'puntaje':0,  'reactivos': EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=grupoestudiante, estado=True, bateriadetalle__reactivo__asignaciondocente__asignatura=i['bateriadetalle__reactivo__asignaciondocente__asignatura'])} for i in grupoasignatura)
                        aux = 0
                        for l in lista:
                            actual = 0
                            for i in l['reactivos']:
                                nota = i.bateriadetalle.reactivo.nota
                                countopciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, activo=True).count()
                                valiopciones = i.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.valiopciones
                                index = 0
                                opciones = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion__activo=True)
                                tipo = i.bateriadetalle.reactivo.tipopregunta.nombre
                                cal = 0
                                if tipo == "EMPAREJAMIENTO":
                                    for o in opciones:
                                        if o.emparejamiento == str(o.opcion_id):
                                            cal += ((o.opcion.valorporcentual * nota) / 100)
                                            index+=1
                                else:
                                    for o in opciones:
                                        cal += ((o.opcion.valorporcentual * nota) / 100)
                                        index += 1

                                if valiopciones:
                                    if index == countopciones:
                                        actual += cal
                                else:
                                    actual += cal
                            aux += actual
                            l['puntaje'] = actual
                        data['calificacion'] = calificacion = round((aux * maximo) / total,2)
                        data['title'] = 'Resumen del examen complexivo'
                        data['estudiante'] = grupoestudiante
                        data['grupos'] = lista
                        data['total'] = reactivos.count()
                        #reactivos
                        listareactivos = []
                        for i in reactivos:
                            listaextra = []
                            listaopciones = []
                            valiacierto = False
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo=None).order_by('id').values('texto', 'archivo', 'id', 'activo'))
                            if i.bateriadetalle.reactivo.tipopregunta.nombre == "EMPAREJAMIENTO":
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                listaextra = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
                                listaopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for i in opciones]
                                for o in listaopciones:
                                    detalle = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion=o['id']).exists()
                                    if detalle:
                                        o['vali'] = True
                                        detalle = DetalleEstudianteExamen.objects.get(status=True, reactivo=i, opcion=o['id'])
                                        texto = DetalleReactivoDocente.objects.get(pk=int(detalle.emparejamiento))
                                        o['id2'] = str(texto.id)
                                        o['id'] = str(o['id'])
                                        o['texto2'] = texto.texto.split(';')[1]
                                if i.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.valiopciones:
                                    vali = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i)
                                    cont = 0
                                    for v in vali:
                                        if v.opcion_id == int(v.emparejamiento):
                                            cont+=1
                                    if cont == len(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo=None, activo=True)):
                                        valiacierto = True
                                else:
                                    vali = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i)
                                    cont = 0
                                    for v in vali:
                                        if v.opcion_id == int(v.emparejamiento):
                                            cont += 1
                                    if cont > 0:
                                        valiacierto = True
                            else:
                                listaopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'estado':a['activo'], 'vali': DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion_id=a['id']).exists()} for a in opciones]
                                if i.bateriadetalle.reactivo.asignaciondocente.formato.formatoreactivo.valiopciones:
                                    vali = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion__activo=True).count()
                                    if vali == len(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo=None, activo=True)):
                                        valiacierto = True
                                else:
                                    vali = DetalleEstudianteExamen.objects.filter(status=True, reactivo=i, opcion__activo=True).count()
                                    if vali > 0:
                                        valiacierto = True
                            listareactivos.append({
                                'reactivo': i.bateriadetalle.reactivo,
                                'vali': valiacierto,
                                'atributos': list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo')),
                                'opciones': listaopciones,
                                'listaextra': listaextra
                            })
                        data['reactivos'] = listareactivos
                        return render(request,'est_examencomplexivo/adm_detalleexamen.html',data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_simulexamencomplexivo':
                    try:
                        data['user'] = user = request.session['user']
                        data['title'] = 'Simulador de examen complexivo'
                        periodo = Periodo.objects.filter(status=True, activo=True).exists()
                        if periodo:
                            periodo = Periodo.objects.get(status=True, activo=True)
                            persona = Persona.objects.get(pk=user.id)
                            if has_group(user, "UPA"):
                                data['matriculas'] = matriculas = list(MatriculaTitulacion.objects.filter(status=True, alternativa__grupotitulacion__periodogrupo__periodo=periodo, alternativa__tipotitulacion__mecanismotitulacion__mecanismotitulacion__nombre="EXAMEN COMPLEXIVO"))
                            else:
                                data['matriculas'] = matriculas = list(MatriculaTitulacion.objects.filter(status=True, alternativa__grupotitulacion__periodogrupo__periodo=periodo, alternativa__tipotitulacion__mecanismotitulacion__mecanismotitulacion__nombre="EXAMEN COMPLEXIVO", inscripcion__persona=persona))
                        return render(request,'est_examencomplexivo/adm_simulexamencomplexivo.html',data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_simulacionexamen':
                    try:
                        data['carreras'] = Carrera.objects.filter(status=True)
                        user = request.session['user']
                        persona = Persona.objects.get(pk=int(user.id))
                        data['matricula'] = matricula = MatriculaTitulacion.objects.get(pk=int(request.GET['id']))
                        data['baterias'] = baterias = list(BateriaCarrera.objects.filter(status=True, revision=True, carrera__carrera=matricula.alternativa.carrera).exclude(bateriaestudiante__periodo=matricula.alternativa.grupotitulacion.periodogrupo.periodo))
                        data['title'] = 'Simulador de examen complexivo'
                        return render(request,'est_examencomplexivo/add_simulacionexamen.html',data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_simulacionexamen':
                    try:
                        data['simulacion'] = simulacion = SimulacionExamen.objects.get(pk=int(request.GET['id']))
                        data['title'] = 'Simulación de examen complexivo'
                        indice = int(request.GET['index'])
                        data['reactivos'] = reactivos = list(SimulacionExamenReactivo.objects.filter(status=True, simulacion=simulacion).order_by('id'))
                        actual = reactivos[indice]
                        grupoemparejamiento = []
                        atributos = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivos[indice].detallebateria.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))
                        opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivos[indice].detallebateria.reactivo, atributo=None).order_by('id').values('texto', 'archivo','id'))
                        data['maxresp'] = limites = DetalleReactivoDocente.objects.filter(status=True,reactivo=reactivos[indice].detallebateria.reactivo,atributo=None,activo=True).count()
                        if actual.detallebateria.reactivo.tipopregunta.nombre != "EMPAREJAMIENTO":
                            if actual.detallebateria.reactivo.aleatorio:
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                listopciones = [{'texto': opciones[a]['texto'], 'archivo': opciones[a]['archivo'], 'id': opciones[a]['id'], 'vali': SimulacionDetalle.objects.filter(status=True,reactivo=reactivos[indice],opcion_id=opciones[a]['id']).exists()} for a in aleatorio]
                                opciones = listopciones
                            else:
                                listopciones = [{'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'vali': SimulacionDetalle.objects.filter(status=True, reactivo=reactivos[indice], opcion_id=a['id']).exists()} for a in opciones]
                                opciones = listopciones
                        else:
                            aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                            index = 0
                            # poner las opciones de emparejamiento en aleatorio
                            grupoemparejamiento = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'],'vali': SimulacionDetalle.objects.filter(status=True, reactivo=reactivos[indice], emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
                            # poner las opciones
                            if actual.detallebateria.reactivo.aleatorio:
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                listopciones = [{'id': opciones[a]['id'], 'texto': opciones[a]['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for a in aleatorio]
                            else:
                                listopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for i in opciones]
                            for i in listopciones:
                                detalle = DetalleEstudianteExamen.objects.filter(status=True, reactivo=reactivos[indice], opcion=i['id']).exists()
                                if detalle:
                                    i['vali'] = True
                                    detalle = DetalleEstudianteExamen.objects.get(status=True, reactivo=reactivos[indice], opcion=i['id'])
                                    texto = DetalleReactivoDocente.objects.get(pk=int(detalle.emparejamiento))
                                    i['id2'] = str(texto.id)
                                    i['texto2'] = texto.texto.split(';')[1]
                            opciones = listopciones
                        data['actual'] = {'reactivo': actual, 'aleatorio': actual.detallebateria.reactivo.aleatorio, 'tipo': actual.detallebateria.reactivo.tipopregunta.nombre, 'nota': actual.detallebateria.reactivo.nota, 'opciones': opciones, 'atributos': atributos, 'grupoemparejamiento': grupoemparejamiento}
                        if indice == 0:
                            data['index'] = 0
                        else:
                            data['index'] = indice
                        if indice < len(reactivos) - 1:
                            data['vali'] = True
                        return render(request, 'est_examencomplexivo/edit_simulacionexamen.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallesimulacion':
                    try:
                        data['title'] = 'Simulación de examen complexivo'
                        data['simulacion'] = simulacion = SimulacionExamen.objects.get(pk=int(request.GET['id']))
                        reactivos = SimulacionExamenReactivo.objects.filter(status=True, simulacion=simulacion)
                        aciertos = 0
                        for i in reactivos:
                            tipo=i.detallebateria.reactivo.tipopregunta.nombre
                            opciones = SimulacionDetalle.objects.filter(status=True, reactivo=i, opcion__activo=True)
                            count = 0
                            if tipo == "EMPAREJAMIENTO":
                                for o in opciones:
                                    if o.emparejamiento == str(o.opcion_id):
                                        count += 1
                                if opciones.count() != 0:
                                    if count == opciones.count():
                                        aciertos+=1
                            else:
                                for o in opciones:
                                    count+=1
                                if opciones.count()!=0:
                                    if count == opciones.count():
                                        aciertos+=1
                        data['aciertos'] = aciertos
                        listareactivos = []
                        for i in reactivos:
                            listaextra = []
                            listaopciones = []
                            valiacierto = False
                            opciones = list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.detallebateria.reactivo,atributo=None).order_by('id').values('texto', 'archivo', 'id', 'activo'))
                            if i.detallebateria.reactivo.tipopregunta.nombre == "EMPAREJAMIENTO":
                                aleatorio = random.sample(range(0, len(opciones)), len(opciones))
                                listaextra = [{'texto': opciones[a]['texto'].split(';')[1], 'id': opciones[a]['id'], 'vali': SimulacionDetalle.objects.filter(status=True, reactivo=i, emparejamiento=str(opciones[a]['id'])).exists()} for a in aleatorio]
                                listaopciones = [{'id': i['id'], 'texto': i['texto'].split(';')[0], 'id2': None, 'texto2': None, 'vali': False} for i in opciones]
                                for o in listaopciones:
                                    detalle = SimulacionDetalle.objects.filter(status=True, reactivo=i, opcion=o['id']).exists()
                                    if detalle:
                                        o['vali'] = True
                                        detalle = SimulacionDetalle.objects.get(status=True, reactivo=i, opcion=o['id'])
                                        texto = SimulacionDetalle.objects.get(pk=int(detalle.emparejamiento))
                                        o['id2'] = str(texto.id)
                                        o['id'] = str(o['id'])
                                        o['texto2'] = texto.texto.split(';')[1]
                                vali = SimulacionDetalle.objects.filter(status=True, reactivo=i)
                                cont = 0
                                for v in vali:
                                    if v.opcion_id == int(v.emparejamiento):
                                        cont += 1
                                if cont == len(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.detallebateria.reactivo, atributo=None, activo=True)):
                                    valiacierto = True
                            else:
                                listaopciones = [ {'texto': a['texto'], 'archivo': a['archivo'], 'id': a['id'], 'estado': a['activo'], 'vali': SimulacionDetalle.objects.filter(status=True, reactivo=i, opcion_id=a['id']).exists()} for a in opciones]
                                vali = SimulacionDetalle.objects.filter(status=True, reactivo=i, opcion__activo=True).count()
                                if vali == len(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.detallebateria.reactivo, atributo=None, activo=True)):
                                    valiacierto = True
                            listareactivos.append({'reactivo': i.detallebateria.reactivo, 'vali': valiacierto, 'atributos': list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.detallebateria.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo')), 'opciones': listaopciones, 'listaextra': listaextra})
                        data['reactivos'] = listareactivos
                        return render(request, 'est_examencomplexivo/adm_detallesimulacion.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'view_simulacionexamen':
                    try:
                        data['matricula'] = matricula = MatriculaTitulacion.objects.get(pk=int(request.GET['id']))
                        data['simulaciones'] = simulaciones = SimulacionExamen.objects.filter(status=True, matricula=matricula)
                        return render(request, 'est_examencomplexivo/adm_detallesimulacionexamen.html', data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_impugnacion':
                    try:
                        data['title'] = 'IMPUGNACION DE EXAMEN'
                        data['estudiante'] = estudiante = GrupoExamenEstudiante.objects.get(pk=int(request.GET['id']))
                        impugnacion = ImpugnacionExamen.objects.filter(status=True,grupoexamenestudiante=estudiante).exists()
                        lista = []
                        if estudiante.grupoexamen.activo is False:
                            general = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante).values('bateriadetalle__reactivo__asignaciondocente__area','bateriadetalle__reactivo__asignaciondocente__area__nombre').exclude(bateriadetalle__reactivo__asignaciondocente__area=None).order_by('bateriadetalle__reactivo__asignaciondocente__area').distinct()
                            especifico = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante).values('bateriadetalle__reactivo__asignaciondocente__asignatura','bateriadetalle__reactivo__asignaciondocente__asignatura__asignatura__nombre').exclude(bateriadetalle__reactivo__asignaciondocente__asignatura=None).order_by('bateriadetalle__reactivo__asignaciondocente__asignatura').distinct()
                            lista = [{'id': i['bateriadetalle__reactivo__asignaciondocente__area'], 'nombre':i['bateriadetalle__reactivo__asignaciondocente__area__nombre'], 'tipo': 'g'} for i in general]
                            lista.extend({'id': i['bateriadetalle__reactivo__asignaciondocente__asignatura'], 'nombre':i['bateriadetalle__reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'tipo': 'e'} for i in especifico)
                            data['areas'] = lista
                        else:
                            reactivos = EstudianteExamenReactivo.objects.filter(status=True, grupoexamenestudiante=estudiante)
                            lista = [{'reactivo': i, 'tipopregunta': i.bateriadetalle.reactivo.tipopregunta.nombre, 'area':i.bateriadetalle.reactivo.asignaciondocente.area, 'asignatura': i.bateriadetalle.reactivo.asignaciondocente.asignatura,
                                      'atributos': list(DetalleReactivoDocente.objects.filter(status=True, reactivo=i.bateriadetalle.reactivo, atributo__estuvisible=True).exclude(atributo=None).order_by('atributo_id').values('atributo__nombre', 'texto', 'archivo'))} for i in reactivos]
                            data['reactivos'] = lista
                        if impugnacion is False:
                            return render(request, 'est_examencomplexivo/add_impugnacion.html', data)
                        else:
                            return HttpResponseRedirect('/est_configuracioncomplexivo?action=adm_detalleexamencomplexivo&id='+str(estudiante.id))
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                else:
                    raise Http404('Error: Página no encontrada')
            else:
                return HttpResponseRedirect('/')
        else:
            raise Http404('Error: Página no encontrada')