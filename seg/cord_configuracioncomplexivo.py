import json
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from seg.forms import *
from seg.models import *
from seg.views import *
from django.db import transaction
from django.http import Http404
from django.db.models import Sum
from random import sample
from seg.funciones import validarfechamayor, validarrangofechas
from seg.reportes import cord_reportbateriaexamen, cord_reportbateriaexamendetalle, cord_reportrevision

#@login_required(redirect_field_name='ret', login_url='/')
@transaction.atomic()
def view(request):
    data = {}
    data['permite_modificar'] = True
    if 'user' in request.session:
        if request.method == 'POST':
            if 'action' in request.POST:
                action = request.POST['action']
                if action == 'listar_asignaturas':
                    try:
                        if 'idmalla' in request.POST:
                            malla = Malla.objects.get(pk=int(request.POST['idmalla']))
                            asignaturas = list(AsignaturaMalla.objects.filter(status=True, malla= malla).values('id', 'asignatura__nombre', 'nivelmalla', 'nivelmalla__nombre', 'ejeformativo', 'ejeformativo__nombre').order_by('nivelmalla__nombre', 'asignatura__nombre'))
                            return JsonResponse({"result": "ok", "mensaje": asignaturas})
                        else:
                            transaction.set_rollback(True)
                            return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_materias':
                    try:
                        if 'idasignatura' in request.POST:
                            periodos = Periodo.objects.filter(status=True).order_by('-id')[:10]
                            lista = []
                            for p in periodos:
                                docentes = list(ProfesorMateria.objects.filter(status=True, materia__asignaturamalla=request.POST['idasignatura'], profesor__status=True, materia__nivel__periodo=p).values('id', 'materia_id', 'profesor_id', 'profesor__persona__nombres', 'profesor__persona__apellido1', 'profesor__persona__apellido2', 'materia__paralelomateria__nombre',))
                                if len(lista) == 0:
                                    lista = [{'idperiodo': p.id, 'periodo': p.nombre, 'docentes': docentes}]
                                else:
                                    lista.append({'idperiodo': p.id, 'periodo': p.nombre, 'docentes': docentes})
                            return JsonResponse({"result": "ok", "mensaje": lista})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_asignaciondocente':
                    try:
                        vali = request.POST['valilista']
                        if vali == '1':
                            lista = json.loads(request.POST['lista_items1'])
                            cronograma = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['asignacion']))
                            ban = validarrangofechas(cronograma.inicio, cronograma.fin, lista)
                            if ban:
                                for l in lista:
                                    if l['action'] != "del":
                                        inicio = datetime(int(l['inicio'].split('-')[2]), int(l['inicio'].split('-')[1]), int(l['inicio'].split('-')[0]))
                                        fin = datetime(int(l['fin'].split('-')[2]), int(l['fin'].split('-')[1]), int(l['fin'].split('-')[0]))
                                        cantidad = int(l['cantidad'])
                                        activo = l['activo']
                                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(l['idasignacion']))
                                        formato = GrupoFormatoReactivo.objects.get(pk=int(l['idformato']))
                                        if request.POST['tipo'] == 'general':
                                            persona = Persona.objects.get(pk=int(l['idpersona']))
                                            area = ReactivoArea.objects.get(pk=int(l['idarea']))
                                            if l['action'] == 'add':
                                                docente = AsignacionDocenteReactivo(nombre='', asignacion=asignacion, formato=formato, persona=persona, area=area, inicio=inicio, fin=fin, estadoinicial=False, estadofinal=False, revision=False, cantidad=cantidad, activo=activo)
                                                docente.save()
                                            elif l['action'] == 'edit':
                                                docente = AsignacionDocenteReactivo.objects.get(pk=int(l['id']))
                                                docente.activo = activo
                                                docente.inicio = inicio
                                                docente.fin = fin
                                                docente.cantidad = cantidad
                                                docente.save()
                                        else:
                                            docente = Profesor.objects.get(pk=int(l['iddocente']))
                                            asignatura = AsignaturaMalla.objects.get(pk=int(l['idasignatura']))
                                            if l['action'] == 'add':
                                                docente = AsignacionDocenteReactivo(nombre='', asignacion=asignacion, formato=formato, docente=docente, asignatura=asignatura, inicio=inicio, fin=fin, estadoinicial=False, estadofinal=False, revision=False, cantidad=cantidad, activo=activo)
                                                docente.save()
                                            elif l['action'] == 'edit':
                                                docente = AsignacionDocenteReactivo.objects.get(pk=int(l['id']))
                                                docente.activo = activo
                                                docente.inicio = inicio
                                                docente.fin = fin
                                                docente.cantidad = cantidad
                                                docente.save()
                                    else:
                                        docente = AsignacionDocenteReactivo.objects.get(pk=int(l['id']))
                                        docente.status = False
                                        docente.save()
                                        ban = ReactivoDocente.objects.filter(asignaciondocente=docente, status=True).exists()
                                        if ban:
                                            reactivos = ReactivoDocente.objects.filter(asignaciondocente=docente, status=True)
                                            for reactivo in reactivos:
                                                reactivo.status = False
                                                reactivo.save()
                                asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['asignacion']))
                                asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion=asignacion).aggregate(total=Sum('cantidad'))
                                if asignaciones['total'] >= asignacion.tamaniobateria:
                                    asignacion.estadoasignar = True
                                else:
                                    asignacion.estadoasignar = False
                                asignacion.save()
                                return JsonResponse({"result": "ok"})
                            else:
                                return JsonResponse({"result": "error", "mensaje": 'Error en fechas para docentes'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'Error al enviar los datos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_asignacionreactivoaleat':
                    try:
                        vali = AsignacionDocenteEspecificoAleatForm(request.POST)
                        if vali.is_valid():
                            malla = vali.cleaned_data['malla']
                            formato = vali.cleaned_data['formato']
                            asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['asignacion']))
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre!="GENERAL":
                                periodo = asignacion.periodo
                                materias = Materia.objects.filter(status=True, nivel__periodo=periodo, asignaturamalla__malla=malla)
                                for i in materias:
                                    asignatura = i.asignaturamalla
                                    docentes = ProfesorMateria.objects.filter(status=True, materia=i)
                                    for d in docentes:
                                        val = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion, docente=d.profesor, asignatura=asignatura).exists()
                                        if val is False:
                                            asignaciondocente = AsignacionDocenteReactivo(nombre='', asignacion=asignacion, formato=formato, docente=d.profesor, asignatura=asignatura, inicio=vali.cleaned_data['inicio'],fin=vali.cleaned_data['fin'], estadoinicial=False, estadofinal=False, revision=False, cantidad=vali.cleaned_data['cantidad'], activo=vali.cleaned_data['activo'])
                                            asignaciondocente.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_validardocente':
                    try:
                        if request.POST['valireactivo'] == '1':
                            vali = True
                            observacion = None
                        else:
                            vali = False
                            observacion = request.POST['observaciones']
                        reactivo = ReactivoDocente.objects.get(pk=int(request.POST['id']))
                        reactivo.estadofinal = vali
                        reactivo.observacion = observacion
                        reactivo.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                            transaction.set_rollback(True)
                            return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'vali_reactivos':
                    try:
                        if 'idasignacion' in request.POST:
                            asignacion = AsignacionDocenteReactivo.objects.get(pk=int(request.POST['idasignacion']))
                            count = ReactivoDocente.objects.filter(status=True, asignaciondocente=asignacion, estadofinal=False).count()
                            if count > 0:
                                return JsonResponse({"result": "ok", "mensaje": '0'})
                            else:
                                return JsonResponse({"result": "ok", "mensaje": '1'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'add_revisionreactivos':
                    try:
                        lista = json.loads(request.POST['lista_items1'])
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['id']))
                        for l in lista:
                            asig = AsignacionDocenteReactivo.objects.get(pk=int(l['idasignacion']))
                            asig.revision = l['estado']
                            asig.save()
                            if l['estado'] == True:
                                reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente=asig)
                                for r in reactivos:
                                    r.estadofinal = True
                                    r.save()
                        valis = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, revision=True, asignacion=asignacion).count()
                        total = AsignacionDocenteReactivo.objects.filter(status=True, activo=True, asignacion=asignacion).count()
                        if valis == total:
                            asignacion.estadorevision = True
                            asignacion.save()
                        else:
                            asignacion.estadorevision = False
                            asignacion.save()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_cantreactivoperiodo':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        if periodo.activo:
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignacion__periodo=periodo, asignaciondocente__revision=True).count()
                        else:
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente__asignacion__periodo=periodo, asignaciondocente__revision=True, asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera).count()
                        return JsonResponse({"result": "ok", "mensaje": reactivos})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'adm_reactivosperiodo':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        cantidad = int(request.POST['cant'])
                        if periodo.activo:
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignacion__periodo=periodo, asignaciondocente__revision=True)
                        else:
                            reactivos = ReactivoDocente.objects.filter(status=True, asignaciondocente__asignacion__periodo=periodo, asignaciondocente__revision=True, asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera)
                        lista = []
                        for r in reactivos:
                            atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=r).exclude(atributo=None).order_by('id').values('atributo__nombre', 'texto', 'archivo')
                            opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=r, atributo=None).order_by('id').values('texto','archivo')
                            item = {'reactivo': r.id, 'asignatura':r.asignaciondocente.asignatura.asignatura.nombre, 'tipopregunta': r.tipopregunta.nombre, 'aleatorio': r.aleatorio, 'nota': r.nota, 'atributos': list(atributos), 'opciones': list(opciones), 'vali': False}
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
                        return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_asignaturaperiodo':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        if periodo.activo:
                            asignaturas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('asignatura__asignatura__nombre', 'asignatura__asignatura').distinct()
                        else:
                            asignaturas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion__periodo=periodo, asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera).values('asignatura__asignatura__nombre', 'asignatura__asignatura').order_by('asignatura__asignatura').distinct('asignatura__asignatura')
                        lista = list(asignaturas)
                        return JsonResponse({"result": "ok", "mensaje": lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_totalreactivos':
                    try:
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        asignatura = Asignatura.objects.get(pk=int(request.POST['id']))
                        if asignacion.grupomalla:
                            asignatura = AsignaturaMalla.objects.get(status=True, asignatura=asignatura, malla=asignacion.grupomalla.malla)
                            if periodo.activo:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignatura=asignatura)
                            else:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True,
                                                                           asignaciondocente__asignacion__periodo=periodo,
                                                                           asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera,
                                                                           asignaciondocente__asignatura=asignatura)
                        else:
                            if periodo.activo:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignatura__asignatura=asignatura)
                            else:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True,
                                                                           asignaciondocente__asignacion__periodo=periodo,
                                                                           asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera,
                                                                           asignaciondocente__asignatura__asignatura=asignatura)
                        count = len(reactivos).__str__()
                        return JsonResponse({"result": "ok", "mensaje": count})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'listar_reactivosasigbateria':
                    try:
                        datos = sorted(json.loads(request.POST['lista_reactivos']))
                        lista = []
                        for d in datos:
                            reactivo = ReactivoDocente.objects.get(pk=int(d))
                            atributos = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo).exclude(atributo=None).order_by('id').values('atributo__nombre', 'texto', 'archivo')
                            opciones = DetalleReactivoDocente.objects.filter(status=True, reactivo=reactivo, atributo=None).order_by('id').values('texto','archivo')
                            item = {'reactivo': reactivo.id, 'asignatura':reactivo.asignaciondocente.asignatura.asignatura.nombre, 'tipopregunta': reactivo.tipopregunta.nombre, 'aleatorio': reactivo.aleatorio, 'nota': reactivo.nota, 'atributos': list(atributos), 'opciones': list(opciones), 'vali': False}
                            if len(lista) == 0:
                                lista = [item]
                            else:
                                lista.append(item)
                        return JsonResponse({"result":"ok", "mensaje":lista})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'adm_reactivosasignatura':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['idasig']))
                        asignatura = Asignatura.objects.get(pk=int(request.POST['id']))
                        periodo = Periodo.objects.get(pk=int(request.POST['idperiodo']))
                        cantidad = int(request.POST['cant'])
                        if asignacion.grupomalla:
                            asignatura = AsignaturaMalla.objects.get(status=True, asignatura=asignatura,  malla=asignacion.grupomalla.malla)
                            if periodo.activo:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignatura=asignatura).order_by('id')
                            else:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True,
                                                                           asignaciondocente__asignacion__periodo=periodo,
                                                                           asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera,
                                                                           asignaciondocente__asignatura=asignatura).order_by('id')
                        else:
                            if periodo.activo:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True, asignaciondocente__asignacion=asignacion, asignaciondocente__asignatura__asignatura=asignatura).order_by('id')
                            else:
                                reactivos = ReactivoDocente.objects.filter(status=True, estadofinal=True,
                                                                           asignaciondocente__asignacion__periodo=periodo,
                                                                           asignaciondocente__asignacion__grupocarrera__carrera=asignacion.grupocarrera.carrera,
                                                                           asignaciondocente__asignatura__asignatura=asignatura).order_by('id')
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
                elif action == 'edit_bateriaexamen':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['id']))
                        bateriacarrera = BateriaCarrera.objects.get(pk=int(request.POST['idbateria']))
                        tiporeactivo = TipoReactivo.objects.get(status=True, nombre="ESPECIFICO")
                        vali = request.POST['vali']
                        if vali == "1":
                            if bateriacarrera.revision == False:
                                datos = json.loads(request.POST['lista_items1'])
                                lista = []
                                for d in datos:
                                    if len(lista) == 0:
                                        lista = d['reactivos']
                                    else:
                                        lista.extend(d['reactivos'])
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
                                return JsonResponse({"result": "error", "mensaje": 'Bateria revisada, no se puede editar.'})
                        else:
                            return JsonResponse({"result": "error", "mensaje": u"Revisar la cantidad de reactivos."})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_bateriaexamenaleatorio':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.POST['id']))
                        bateriacarrera = BateriaCarrera.objects.get(pk=int(request.POST['idbateria']))
                        if bateriacarrera.revision == False:
                            tiporeactivo = TipoReactivo.objects.get(status=True, nombre="ESPECIFICO")
                            datos = json.loads(request.POST['lista_items1'])
                            lista = []
                            for d in datos:
                                if len(lista) == 0:
                                    lista = d['reactivos']
                                else:
                                    lista.extend(d['reactivos'])
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
                            return JsonResponse({"result": "error", "mensaje": 'Bateria revisada, no se puede editar.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                elif action == 'edit_bateriaestudiantes':
                    try:
                        vali = request.POST['vali']
                        if vali == "1":
                            estudiantes = json.loads(request.POST['lista_items1'])
                            periodo = Periodo.objects.get(pk=int(request.POST['periodo']))
                            for e in estudiantes:
                                if e['action'] == "add":
                                    bateriacarrera = BateriaCarrera.objects.get(pk=int(e['idbateria']))
                                    matricula = MatriculaTitulacion.objects.get(pk=int(e['idestudiante']))
                                    bateriaest = BateriaEstudiante(bateriacarrera=bateriacarrera, matricula=matricula, periodo=periodo)
                                    bateriaest.save()
                                elif e['action'] == 'edit':
                                    bateriacarrera = BateriaCarrera.objects.get(pk=int(e['idbateria']))
                                    bateriaest = BateriaEstudiante.objects.get(pk=int(e['id']))
                                    bateriaest.bateriacarrera = bateriacarrera
                                    bateriaest.save()
                                elif e['action'] == 'del':
                                    bateriaest = BateriaEstudiante.objects.get(pk=int(e['id']))
                                    bateriaest.status = False
                                    bateriaest.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error", "mensaje": 'Error al enviar los datos.'})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})
                else:
                    return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
            else:
                return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
        else:
            if 'action' in request.GET:
                action = request.GET['action']
                if action == 'adm_asignacionreactivo':
                    try:
                        return view_asignacionreactivo(request)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_asignacionreactivodetalle':
                    try:
                        a=1 ##programar aqui
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_asignaciondocente':
                    try:
                        if 'id' in request.GET:
                            data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=asignacion.periodo)
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre == "GENERAL":
                                data['asignaciones'] = asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion).order_by('-estadofinal', 'area__nombre', 'persona__apellido1', 'persona__apellido2', 'persona__nombres')
                            else:
                                data['asignaciones'] = asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion).order_by('-estadofinal', 'asignatura__malla', 'asignatura__nivelmalla', 'asignatura', 'docente__persona__apellido1', 'docente__persona__apellido2', 'docente__persona__nombres')
                            data['title'] = 'Asignaciones'
                            return render(request, "cord_examencomplexivo/ajax_detalleasignardocente.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_asignacionreactivo':
                    try:
                        if 'id' in request.GET:
                            data['periodo'] = periodo = Periodo.objects.get(activo=True, status=True)
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=periodo)
                            data['title'] = 'Asignacion de reactivos'
                            data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre == "GENERAL":
                                data['asignaciones'] = asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion).order_by('estadofinal','area__nombre', 'persona')
                            else:
                                data['asignaciones'] = asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion).order_by('estadofinal','asignatura__malla', 'asignatura__nivelmalla', 'asignatura', 'docente')
                            formato = GrupoFormatoReactivo.objects.get(status=True, grupocronograma__periodo=periodo, formatoreactivo__tiporeactivo=asignacion.formato.formatoreactivo.tiporeactivo)
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre == "GENERAL":
                                data['title2'] = ""
                                data['form'] = AsignacionDocenteGeneralForm(initial={'formato':formato,'activo':True, 'inicio': datetime.strftime(asignacion.inicio, "%d-%m-%Y"), 'fin': datetime.strftime(asignacion.fin, "%d-%m-%Y")})
                            else:
                                data['title2'] = asignacion.grupocarrera.carrera.nombre.capitalize()
                                data['form'] = AsignacionDocenteEspecificoForm(initial={'formato': formato, 'activo':True, 'inicio': datetime.strftime(asignacion.inicio, "%d-%m-%Y"), 'fin': datetime.strftime(asignacion.fin, "%d-%m-%Y")})
                                if asignacion.grupocarrera.activocarrera:
                                    data['mallas'] = mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=asignacion.grupocarrera).order_by('-malla__vigente')
                                else:
                                   data['mallas'] = [asignacion.grupomalla]
                            return render(request, "cord_examencomplexivo/add_asignacionreactivo.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_asignacionreactivoaleat':
                    try:
                        if 'id' in request.GET:
                            data['periodo'] = periodo = Periodo.objects.get(activo=True, status=True)
                            data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                            data['cronograma'] = cronograma = CronogramaPlanificacionExamen.objects.get(status=True, periodo=periodo)
                            data['title'] = 'Asignacion de reactivos'
                            formato = GrupoFormatoReactivo.objects.get(status=True, grupocronograma__periodo=periodo, formatoreactivo__tiporeactivo=asignacion.formato.formatoreactivo.tiporeactivo)
                            if asignacion.formato.formatoreactivo.tiporeactivo.nombre != "GENERAL":
                                data['title2'] = asignacion.grupocarrera.carrera.nombre.capitalize()
                                data['form'] = AsignacionDocenteEspecificoAleatForm(initial={'formato': formato, 'activo': True, 'inicio': datetime.strftime(asignacion.inicio, "%d-%m-%Y"), 'fin': datetime.strftime(asignacion.fin, "%d-%m-%Y")})
                                if asignacion.grupocarrera.activocarrera:
                                    data['mallas'] = mallas = GrupoCarreraMallaExamen.objects.filter(status=True, grupocarrera=asignacion.grupocarrera).order_by('-malla__vigente')
                                else:
                                    data['mallas'] = [asignacion.grupomalla]
                            return render(request, "cord_examencomplexivo/add_asignacionreactivoaleat.html", data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_revisionreactivo':
                    try:
                        data['title'] = 'Revisión de reactivos'
                        data['user'] = user = request.session['user']
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
                        return render(request, "cord_examencomplexivo/adm_revisionreactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_revisionreactivo':
                    try:
                        data['title'] = 'Revisión de reactivos'
                        data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        if asignacion.formato.formatoreactivo.tiporeactivo.nombre != "GENERAL":
                            asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion, activo=True).order_by('estadofinal','asignatura__malla','asignatura__nivelmalla','asignatura__asignatura','docente__persona__apellido1', 'docente__persona__apellido2', 'docente__persona__nombres')
                        else:
                            asignaciones = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion, activo=True).order_by('estadofinal', 'area', 'persona__apellido1', 'persona__apellido2', 'persona__nombres')
                        lista = []
                        for a in asignaciones:
                            total = ReactivoDocente.objects.filter(status=True, asignaciondocente=a).count()
                            if len(lista) == 0:
                                lista = [{'fila': a, 'total': total}]
                            else:
                                lista.append({'fila': a, 'total': total})
                        data['docentes'] = lista
                        return render(request, "cord_examencomplexivo/add_revisionreactivo.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'add_validardocente':
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
                        return render(request, "cord_examencomplexivo/edit_detallereactivo.html", data)
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
                            data['cronograma'] = CronogramaPlanificacionExamen.objects.get(status=True, periodo=Periodo.objects.get(activo=True))
                            if has_group(user, "UPA"):
                                especificos = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", grupocarrera__status=True)
                            elif has_group(user, "COORDINADOR"):
                                especificos = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", coordinador__persona=persona, grupocarrera__status=True)
                            lista = []
                            for p in especificos:
                                vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=p, tiporeactivo=p.formato.formatoreactivo.tiporeactivo).exists()
                                fecha = validarrangofecha(p.inicio, p.fin)
                                item = {'fila': p, 'existe': vali, 'activo': fecha}
                                if len(lista) == 0:
                                    lista = [item]
                                else:
                                    lista.append(item)
                            data['baterias'] = lista
                        return render(request, "cord_examencomplexivo/adm_bateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_bateriaexamen':
                    try:
                        data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        data['asignaturas'] = asignaturas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('asignatura__asignatura__nombre', 'asignatura__asignatura').distinct()
                        data['title'] = 'Bateria de ' + asignacion.grupocarrera.carrera.nombre.lower()
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        bateria = None
                        reactivos = []
                        if asignacion.grupocarrera.activocarrera:
                            vali = BateriaCarrera.objects.filter(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma).exists()
                            if vali:
                                bateria = BateriaCarrera.objects.get(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                                vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO").exists()
                                if vali:
                                    bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO")
                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignatura__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').distinct())
                        else:
                            vali = BateriaCarrera.objects.filter(status=True, malla=asignacion.grupomalla, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma).exists()
                            if vali:
                                bateria = BateriaCarrera.objects.get(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma, malla=asignacion.grupomalla)
                                vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO").exists()
                                if vali:
                                    bateriaexamen = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO")
                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignatura__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').distinct())
                        lista = []
                        count = 0
                        for r in reactivos:
                            listareactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignatura__asignatura=int(r['reactivo__asignaciondocente__asignatura__asignatura'])).values('reactivo_id'))
                            listareactivos = [i['reactivo_id'].__str__() for i in listareactivos]
                            count = count + len(listareactivos)
                            item = {'id': r['reactivo__asignaciondocente__asignatura__asignatura'], 'asignatura': r['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'reactivos': listareactivos}
                            if len(lista) == 0:
                                lista = [item]
                            else:
                                lista.append(item)
                        data['reactivos'] = lista
                        data['tamanio'] = count
                        data['bateria'] = bateria
                        return render(request, "cord_examencomplexivo/edit_bateria.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_bateriaexamenaleatorio':
                    try:
                        data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        data['asignaturas'] = asignaturas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('asignatura__asignatura__nombre', 'asignatura__asignatura').distinct()
                        data['title'] = 'Bateria de ' + asignacion.grupocarrera.carrera.nombre.lower()
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        bateria = None
                        reactivos = []
                        if asignacion.grupocarrera.activocarrera:
                            vali = BateriaCarrera.objects.filter(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma).exists()
                            if vali:
                                bateria = BateriaCarrera.objects.get(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                                vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO").exists()
                                if vali:
                                    bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO")
                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignacion__periodo', 'reactivo__asignaciondocente__asignacion__periodo__nombre').distinct())
                        else:
                            vali = BateriaCarrera.objects.filter(status=True, malla=asignacion.grupomalla, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma).exists()
                            if vali:
                                bateria = BateriaCarrera.objects.get(status=True, malla=asignacion.grupomalla, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                                vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO").exists()
                                if vali:
                                    bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO")
                                    reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignacion__periodo', 'reactivo__asignaciondocente__asignacion__periodo__nombre').distinct())
                        lista = []
                        count = 0
                        for r in reactivos:
                            listareactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignacion__periodo=int(r['reactivo__asignaciondocente__asignacion__periodo'])).values('reactivo_id'))
                            listareactivos = [i['reactivo_id'].__str__() for i in listareactivos]
                            count = count + len(listareactivos)
                            item = {'id': r['reactivo__asignaciondocente__asignacion__periodo'], 'asignatura': r['reactivo__asignaciondocente__asignacion__periodo__nombre'], 'reactivos': listareactivos}
                            if len(lista) == 0:
                                lista = [item]
                            else:
                                lista.append(item)
                        data['reactivos'] = lista
                        data['tamanio'] = count
                        data['bateria'] = bateria
                        return render(request, "cord_examencomplexivo/edit_bateriaaleatorio.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'view_bateriaexamen':
                    try:
                        data['user'] = request.session['user']
                        data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        data['asignaturas'] = asignaturas = AsignacionDocenteReactivo.objects.filter(status=True, revision=True, asignacion=asignacion).values('asignatura__asignatura__nombre', 'asignatura__asignatura').distinct()
                        data['title'] = 'Bateria de ' + asignacion.grupocarrera.carrera.nombre.lower() + ' para ' + asignacion.grupocarrera.grupofacultad.grupocronograma.nombre.lower()
                        bateria = BateriaCarrera.objects.get(status=True, carrera=asignacion.grupocarrera, bateria__cronograma=asignacion.grupocarrera.grupofacultad.grupocronograma)
                        vali = BateriaExamenComplexivo.objects.filter(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO").exists()
                        if vali:
                            data['bateriaexamen'] = bateriaexamen = BateriaExamenComplexivo.objects.get(status=True, coordinador=asignacion, bateriacarrera=bateria, tiporeactivo__nombre="ESPECIFICO")
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignatura__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').order_by('reactivo__asignaciondocente__asignatura__asignatura').distinct('reactivo__asignaciondocente__asignatura__asignatura'))
                            lista = [{'id':i['reactivo__asignaciondocente__asignatura__asignatura'],'asignatura': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'reactivos': BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignatura__asignatura=int(i['reactivo__asignaciondocente__asignatura__asignatura'])).count() } for i in reactivos]
                            data['reactivos'] = lista
                            data['tamanio'] = BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).count()
                            return render(request, 'cord_examencomplexivo/view_bateriaexamen.html', data)
                        else:
                            raise Http404('Error: Página no encontrada')
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'report_bateriaexamen':
                    try:
                        bateriaexamen = BateriaExamenComplexivo.objects.get(pk=int(request.GET['id']))
                        if 'idasig' in request.GET:
                            asignatura = AsignaturaMalla.objects.get(pk=int(request.GET['idasig']))
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignatura_id=int(request.GET['idasig'])).values('reactivo_id','reactivo__tipopregunta__nombre','reactivo__aleatorio','reactivo__nota').order_by('reactivo_id'))
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
                            return cord_reportbateriaexamendetalle(listado, asignatura.asignatura.nombre)
                        else:
                            reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).values('reactivo__asignaciondocente__asignatura__asignatura', 'reactivo__asignaciondocente__asignatura__asignatura__nombre').order_by('reactivo__asignaciondocente__asignatura__asignatura').distinct('reactivo__asignaciondocente__asignatura__asignatura'))
                            lista = [{'asignatura': i['reactivo__asignaciondocente__asignatura__asignatura__nombre'], 'reactivos': BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignatura__asignatura=int(i['reactivo__asignaciondocente__asignatura__asignatura'])).count() } for i in reactivos]
                            count = BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen).count()
                            malla = None
                            cronograma = bateriaexamen.bateriacarrera.bateria.cronograma.nombre
                            periodo = bateriaexamen.bateriacarrera.bateria.cronograma.periodo.nombre
                            coordinador = bateriaexamen.coordinador.coordinador.persona.nombres + " " + bateriaexamen.coordinador.coordinador.persona.apellido1 + " " + bateriaexamen.coordinador.coordinador.persona.apellido2
                            if bateriaexamen.bateriacarrera.malla:
                                malla = bateriaexamen.bateriacarrera.malla.malla.nombre
                            return cord_reportbateriaexamen(count, lista, bateriaexamen.bateriacarrera.carrera.carrera.nombre, bateriaexamen.bateriacarrera.carrera.carrera.nombre, malla, cronograma,periodo,coordinador)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_detallebateriaexamen':
                    try:
                        data['user'] = request.session['user']
                        data['bateria'] = bateriaexamen = BateriaExamenComplexivo.objects.get(pk=int(request.GET['id']))
                        data['asignatura'] = asignatura = AsignaturaMalla.objects.get(pk=int(request.GET['idasig']))
                        reactivos = list(BateriaDetalle.objects.filter(status=True, bateria=bateriaexamen, reactivo__asignaciondocente__asignatura_id=int(request.GET['idasig'])).values('reactivo_id', 'reactivo__tipopregunta__nombre', 'reactivo__aleatorio', 'reactivo__nota').order_by('reactivo_id'))
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
                        return render(request,'cord_examencomplexivo/adm_detallebateriaexamen.html',data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'adm_bateriaestudiantes':
                    try:
                        data['title'] = 'Cronograma de examen complexivo'
                        data['user'] = user = request.session['user']
                        data['cronograma'] = CronogramaPlanificacionExamen.objects.get(status=True, periodo=Periodo.objects.get(activo=True))
                        data['periodo'] = Periodo.objects.filter(status=True).order_by('-activo', '-id')
                        persona = Persona.objects.get(pk=int(user.id))
                        if has_group(user, "UPA"):
                            data['carreras'] = carreras = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", grupocarrera__status=True).order_by('grupocarrera__carrera__facultad', 'grupocarrera__carrera')
                        elif has_group(user, "COORDINADOR"):
                            data['carreras'] = carreras = AsignacionGrupoCoordinador.objects.filter(status=True, periodo=Periodo.objects.get(activo=True), formato__formatoreactivo__tiporeactivo__nombre="ESPECIFICO", coordinador__persona=persona, grupocarrera__status=True).order_by('grupocarrera__carrera__facultad', 'grupocarrera__carrera')
                        return render(request, "cord_examencomplexivo/adm_bateriaestudiantes.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'edit_bateriaestudiantes':
                    try:
                        data['title'] = 'Asignación de baterias'
                        data['asignacion'] = asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        actual = Periodo.objects.get(status=True, activo=True)
                        data['baterias'] = baterias = list(BateriaCarrera.objects.filter(status=True, revision=True , carrera__carrera=asignacion.grupocarrera.carrera).order_by('-bateria__periodo')[:10])
                        data['estudiantes'] = estudiantes = list(MatriculaTitulacion.objects.filter(status=True, alternativa__grupotitulacion__periodogrupo__periodo=actual, alternativa__carrera=asignacion.grupocarrera.carrera, estado=2, alternativa__tipotitulacion__mecanismotitulacion__mecanismotitulacion__nombre="EXAMEN COMPLEXIVO"))
                        data['actuales'] = actuales = list(BateriaEstudiante.objects.filter(status=True, periodo=actual, bateriacarrera__carrera__carrera=asignacion.grupocarrera.carrera))
                        return render(request, "cord_examencomplexivo/edit_bateriaestudiantes.html", data)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                elif action == 'report_revisionreactivo':
                    try:
                        asignacion = AsignacionGrupoCoordinador.objects.get(pk=int(request.GET['id']))
                        if asignacion.persona:
                            tipo = "area"
                            facultad = ""
                            carrera = ""
                        else:
                            tipo = "materia"
                            facultad = asignacion.coordinador.carrera.facultad.nombre
                            carrera = asignacion.coordinador.carrera.nombre
                        docentes = AsignacionDocenteReactivo.objects.filter(status=True, asignacion=asignacion)
                        lista = [{'asignacion': d, 'count': ReactivoDocente.objects.filter(status=True, asignaciondocente=d).count()} for d in docentes]
                        return cord_reportrevision(tipo, facultad, carrera,lista)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
                else:
                    raise Http404('Error: Página no encontrada')
            else:
                raise Http404('Error: Página no encontrada')
    else:
        return HttpResponseRedirect('/')