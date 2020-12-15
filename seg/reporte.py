from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import Http404
from seg.models import *
from seg.reportes import *
import json

#@login_required(redirect_field_name='ret', login_url='/')
@transaction.atomic()
def view(request):
    data = {}
    data['permite_modificar'] = True
    if request.method == 'POST':
        if 'user' in request.session:
            if 'action' in request.POST:
                action = request.POST['action']
                if action == 'adm_reportexamen':
                    try:
                        examen = CronogramaExamen.objects.get(pk=int(request.POST['id']))
                        facultad = examen.carrera.carrera.facultad.nombre
                        carrera = examen.carrera.carrera.nombre
                        datos = json.loads(request.POST['lista'])
                        if request.POST['extension'] == "pdf":
                            return adm_pdfreportexamen(facultad, carrera, datos)
                        elif request.POST['extension'] == 'xlsx':
                            return adm_csvreportexamen(facultad,carrera,datos)
                        else:
                            return adm_docreportexamen(facultad, carrera,datos)
                    except Exception as ex:
                        raise Http404('Error: Consulte con el administrador.')
            else:
                raise Http404('Error: Consulte con el administrador.')
        else:
            raise Http404('Error: Consulte con el administrador.')
    else:
        raise Http404('Error: Consulte con el administrador.')