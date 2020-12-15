import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import JsonResponse
from seg.forms import PaisForm, FacturaForm
from seg.models import *
from django.db import transaction


@transaction.atomic()
def view(request):
    data = {}
    if request.method == 'POST':
        if 'user' in request.session:
            if 'action' in request.POST:
                action = request.POST['action']
                if action == 'add_factura':
                    try:
                        vali = FacturaForm(request.POST)
                        if vali.is_valid():
                            factura = Factura(ruccliente=vali.cleaned_data['ruccliente'],
                                              nombrecliente=vali.cleaned_data['nombrecliente'])
                            factura.save()
                            datos = json.loads(request.POST['lista_items1'])
                            for p in datos:
                                det = FacturaProducto(factura=factura,
                                                      producto=p['producto'],
                                                      precio=p['precio'],
                                                      cantidad=p['cantidad'])
                                det.save()
                            return JsonResponse({"result": "ok"})
                        else:
                            return JsonResponse({"result": "error",
                                                 "mensaje": 'datos erroneos en el formulario.'})
                    except Exception as ex:
                        transaction.get_rollback()
                        return JsonResponse({"result": "error",
                                             "mensaje": 'Ocurrio un problema contacte con el administrador.'})

        else:
            return JsonResponse({"result": "session"})
            # return HttpResponseRedirect("/")
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add_factura':
                data['title'] = u'Agregar Factura'
                data['form'] = FacturaForm()
                return render(request, "factura/add_factura.html", data)

            if action == 'edit_pais':
                data['title'] = u'Editar Pais'
                data['pais'] = pais = Pais.objects.get(pk=int(request.GET['id']))
                data['form'] = PaisForm(initial={'nombre': pais.nombre,
                                                 'estado': pais.estado})
                return render(request, "add_pais.html", data)
        else:
            data['user'] = request.session['user']
            data['factura'] = Factura.objects.all()
            return render(request, "factura.html", data)