import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import JsonResponse
from seg.forms import PaisForm
from seg.models import *
from django.db import transaction


# @login_required(redirect_field_name='ret', login_url='/')
@transaction.atomic()
def view(request):
    data = {}
    data['permite_modificar'] = True
    if request.method == 'POST':
        if 'user' in request.session:
            if 'action' in request.POST:
                action = request.POST['action']
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
                                    if ext != 'jpeg' or ext != 'jpg' or ext != 'png': return JsonResponse({"result": "error", "mensaje": 'No es un archivo valido.'})
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
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})

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
                        return JsonResponse({"result": "error","mensaje": 'Ocurrio un problema contacte con el administrador. %s' % ex})

                elif action == 'del_pais':
                    try:
                        pais = Pais.objects.get(pk=int(request.POST['id']))
                        pais.delete()
                        return JsonResponse({"result": "ok"})
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"result": "error", "mensaje": 'Ocurrio un problema contacte con el administrador.'})

                return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
        else:
            return JsonResponse({"result": "session"})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add_pais':
                try:
                    data['title'] = u'Agregar Pais'
                    data['form'] = PaisForm(initial={'estado': True})
                    return render(request, "add_pais.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit_pais':
                try:
                    data['title'] = u'Editar Pais'
                    data['pais'] = pais = Pais.objects.get(pk=int(request.GET['id']))
                    data['form'] = PaisForm(initial={'nombre': pais.nombre,
                                                     'estado': pais.estado})
                    return render(request, "add_pais.html", data)
                except Exception as ex:
                    pass

            elif action == 'del_pais':
                try:
                    data['title'] = u'Eliminar Pais'
                    data['pais'] = Pais.objects.get(pk=int(request.GET['id']))
                    return render(request, "del_pais.html", data)
                except Exception as ex:
                    pass
