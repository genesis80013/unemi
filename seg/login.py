import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from seg.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import auth


def view(request):
    data = {}
    if request.method == 'POST':
        #codigo por post
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'login':
                user = request.POST['user']
                clave = request.POST['pass']
                vali = authenticate(username=user.lower(), password=clave)
                if vali:
                    request.session['user'] = User.objects.get(username__icontains=user)
                    return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")
                else:
                    return HttpResponse(json.dumps({"result": "error", "mensaje": 'Usuario o clave incorrecta.'}), content_type="application/json")

        else:
            return render(request, "login.html", data)
    else:
        #codigo por get
        if 'user' in request.session:
            data['title'] = u'Bienvenido al módulo examen complexivo'
            data['user'] = user = request.session['user']
            data['pais'] = Pais.objects.all()
            return render(request, "holamundo.html", data)
        else:
            return render(request, "login.html", data)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
