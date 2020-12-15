"""unemi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from unemi import settings
from django.conf.urls.static import static
from seg import views, login, pais, factura, adm_configuracioncomplexivo, cord_configuracioncomplexivo, doc_configuracioncomplexivo, est_configuracioncomplexivo, reporte
from templates import *

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^adm_configuracioncomplexivo$', adm_configuracioncomplexivo.view),
    url(r'^cord_configuracioncomplexivo$', cord_configuracioncomplexivo.view),
    url(r'^doc_configuracioncomplexivo$', doc_configuracioncomplexivo.view),
    url(r'^est_configuracioncomplexivo$', est_configuracioncomplexivo.view),
    url(r'^reporte$', reporte.view),
    url(r'^factura$', factura.view),
    url(r'^logout$', login.logout),
    url(r'^$', login.view)
]
