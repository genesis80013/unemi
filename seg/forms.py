import os
from django import forms
from django.forms.models import ModelForm, ModelChoiceField
from docutils.nodes import status

from seg.models import *
from datetime import datetime, date
from django.forms.widgets import DateTimeInput, CheckboxInput, FileInput

from seg.models import Provincia


class ExtFileField(forms.FileField):
    """
    * max_upload_size - a number indicating the maximum file size allowed for upload.
            500Kb - 524288
            1MB - 1048576
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    t = ExtFileField(ext_whitelist=(".pdf", ".txt"), max_upload_size=)
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de fichero o tamanno no permitido!")


class FixedForm(ModelForm):
    date_fields = []

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for f in self.date_fields:
            self.fields[f].widget.format = '%d-%m-%Y'
            self.fields[f].input_formats = ['%d-%m-%Y']


class PaisForm(forms.Form):
    nombre = forms.CharField(label=u'País', max_length=100, widget=forms.TextInput(attrs={'formwidth': '100'}))
    imagen = ExtFileField(label=u'Seleccione Imagen', help_text=u'Tamaño Maximo permitido 5Mb, en formato jpg',
                          ext_whitelist=(".jpg", ".png", ".docx",), max_upload_size=5242880, required=False,
                          widget=forms.FileInput(attrs={'formwidth': '100'}))
    estado = forms.BooleanField(label=u'Estado', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '100'}))


class FacturaForm(forms.Form):
    ruccliente = forms.CharField(label=u'Ruc o Cédula', max_length=15,
                                 widget=forms.TextInput(attrs={'class': 'imp-100'}))
    nombrecliente = forms.CharField(label=u'Cliente', max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'imp-100'}))

class TipoReactivoForm(forms.Form):
    nombre = forms.CharField(label=u'Nombre', required=True, max_length=100, widget=forms.TextInput(attrs={'formwidth': '100'}))
    estado = forms.BooleanField(label=u'Estado', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '100'}))

class FormatoReactivoForm(forms.Form):
    nombre = forms.CharField(label=u'Nombre', required=True, max_length=255, widget=forms.TextInput(attrs={'formwidth': '100'}))
    descripcion = forms.CharField(label=u'Descripción', max_length=2000, widget=forms.Textarea(attrs={'formwidth': '100', 'rows':'2'}),required=False)
    tiporeactivo = forms.ModelChoiceField(label=u'Tipo de reactivo', required=True, queryset=TipoReactivo.objects.filter(estado=True, status=True), widget=forms.Select(attrs={'formwidth': '100', 'class':'validate[required]'}))
    notamin = forms.IntegerField(label=u'Nota mínima', min_value=1, max_value=4, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantnota validate[required,custom[onlyNumberSp],min[1], max[4]]', 'idtipo': 'min'}))
    notamax = forms.IntegerField(label=u'Nota máxima', min_value=1, max_value=4, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantnota validate[required,custom[onlyNumberSp],min[1], max[4]]', 'idtipo': 'max'}))
    opcionesmin = forms.IntegerField(label=u'Opciones mínima', min_value=1, max_value=10, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantopciones validate[required,custom[onlyNumberSp],min[1], max[10]]', 'idtipo': 'min'}))
    opcionesmax = forms.IntegerField(label=u'Opciones máxima', min_value=1, max_value=10, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantopciones validate[required,custom[onlyNumberSp],min[1], max[10]]', 'idtipo': 'max'}))
    respuestasmin = forms.IntegerField(label=u'Respuestas mínima', min_value=1, max_value=10, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantrespuestas validate[required,custom[onlyNumberSp],min[1], max[10]]', 'idtipo': 'min'}))
    respuestasmax = forms.IntegerField(label=u'Respuestas máxima', min_value=1, max_value=10, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'cantrespuestas validate[required,custom[onlyNumberSp],min[1], max[10]]', 'idtipo': 'max'}))
    archivo = ExtFileField(label=u'Seleccione archivo', help_text=u'Tamaño Maximo permitido 5Mb, en formato docx', ext_whitelist=(".docx",), max_upload_size=5242880, required=False, widget=forms.FileInput(attrs={'formwidth': '50'}))
    estado = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiactivo'}))
    valiopciones = forms.BooleanField(label=u'¿Obligatorio acertar todas las respuestas?', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiopciones'}))

class TipoPreguntaReactivoForm(forms.Form):
    nombre = forms.CharField(label=u'Nombre', required=True, max_length=255, widget=forms.TextInput(attrs={'formwidth': '100'}))
    abreviatura = forms.CharField(label=u'Abreviatura', required=True, max_length=20, widget=forms.TextInput(attrs={'formwidth': '100', 'class': 'validate[required,custom[onlyLetterSp]]'}))
    activo = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiactivo'}))

class AreaReactivoForm(forms.Form):
    nombre = forms.CharField(label=u'Nombre', required=True, max_length=255, widget=forms.TextInput(attrs={'formwidth': '100'}))
    activo = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50'}))


class CronogramaPlanificacionForm(forms.Form):
    nombre = forms.CharField(label=u'Nombre', required=True, max_length=255, widget=forms.TextInput(attrs={'formwidth': '100'}))
    periodo = forms.ModelChoiceField(label=u'Período académico', required=True, queryset=Periodo.objects.filter(status=True, activo=True).order_by('-id'), widget=forms.Select(attrs={'formwidth': '100', 'class': 'validate[required] valiperiodo'}))
    inicio = forms.DateTimeField(label=u'Fecha de inicio', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainicio validate[required]', 'formwidth': '50'}))
    fin = forms.DateTimeField(label=u'Fecha de fin', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafin validate[required]', 'formwidth': '50'}))
    porcsimilitud = forms.DecimalField(label=u'Porcentaje similitud', min_value=1, max_value=100, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[required,custom[onlyNumberSp],min[1],max[100]]'}))
    tambateria = forms.IntegerField(label=u'Tamaño de bateria', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[required,custom[onlyNumberSp],min[1]] valibateria'}))
    iniciocord = forms.DateTimeField(label=u'Inicio coordinadores', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainiciocord validate[required]', 'formwidth': '50'}))
    fincord = forms.DateTimeField(label=u'Fin coordinadores', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafincord validate[required]', 'formwidth': '50'}))

tipos = [('0','----------'),
         ('carrera','CARRERA'),
         ('malla', 'MALLA')]

class AsignacionGrupoCoordinadorForm(forms.Form):
    cronograma = forms.ModelChoiceField(label=u'Cronograma', disabled='disabled', required=True, queryset=CronogramaPlanificacionExamen.objects.filter(status=True).order_by('-id'), widget=forms.Select(attrs={'formwidth': '100', 'class': 'cronograma'}))
    facultad = forms.ModelChoiceField(label=u'Facultad', required=True, queryset=GrupoFacultadExamen.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'facultad'}))
    carrera = forms.ModelChoiceField(label=u'Carrera', required=True, queryset=GrupoCarreraExamen.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'carrera'}))
    tipo = forms.ChoiceField(label=u'Tipo de Asignación', disabled='disabled', required=True, choices=tipos, widget=forms.Select(attrs={'formwidth': '100', 'class': 'tipo'}))
    malla = forms.ModelChoiceField(label=u'Malla', required=True, queryset=Malla.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'malla', 'multiple':''}))
    coordinador = forms.ModelChoiceField(label=u'Coordinador', required=True, queryset=CoordinadorCarrera.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'coordinador'}))
    formato = forms.ModelChoiceField(label=u'Formato', required=True, queryset=GrupoFormatoReactivo.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': ' formato'}))
    inicio = forms.DateTimeField(label=u'Fecha de inicio', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainicio ', 'formwidth': '50'}))
    fin = forms.DateTimeField(label=u'Fecha de fin', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafin ', 'formwidth': '50'}))
    tambateria = forms.IntegerField(label=u'Tamaño de bateria', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1]] valibateria'}))
    activoasignar = forms.BooleanField(label=u'Asignar docentes', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class':'valiasignar'}))

class AsignacionDocenteGeneralForm(forms.Form):
    formato = forms.ModelChoiceField(label=u'Formato', disabled=True, required=True, queryset=GrupoFormatoReactivo.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'formato'}))
    area = forms.ModelChoiceField(label=u'Area', required=True, queryset=ReactivoArea.objects.filter(status=True, activo=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect areaid'}))
    persona = forms.ModelChoiceField(label=u'Persona', queryset=Persona.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect personaid'}))
    inicio = forms.DateTimeField(label=u'Fecha de inicio', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainicio ', 'formwidth': '50'}))
    fin = forms.DateTimeField(label=u'Fecha de fin', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafin ', 'formwidth': '50'}))
    cantidad = forms.IntegerField(label=u'Cantidad de reactivos', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1]] valicantidad'}))
    activo = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiactivo'}))

class AsignacionDocenteEspecificoForm(forms.Form):
    formato = forms.ModelChoiceField(label=u'Formato', disabled=True, required=True, queryset=GrupoFormatoReactivo.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'validate[required] formato'}))
    malla = forms.ModelChoiceField(label=u'Malla', required=True, queryset=Malla.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect mallaid'}))
    ejeformativo = forms.ModelChoiceField(label=u'Eje formativo', required=True, queryset=EjeFormativo.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect ejeformativoid'}))
    asignatura = forms.ModelChoiceField(label=u'Asignatura', required=True, queryset=AsignaturaMalla.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect asignaturaid'}))
    materia = forms.ModelChoiceField(label=u'Materia', required=True, queryset=ProfesorMateria.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'materiaid'}))
    docente = forms.ModelChoiceField(label=u'Docente', queryset=Profesor.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect docenteid'}))
    inicio = forms.DateTimeField(label=u'Fecha de inicio', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainicio ', 'formwidth': '50'}))
    fin = forms.DateTimeField(label=u'Fecha de fin', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafin ', 'formwidth': '50'}))
    cantidad = forms.IntegerField(label=u'Cantidad de reactivos', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1]] valicantidad'}))
    activo = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiactivo'}))

class AsignacionDocenteEspecificoAleatForm(forms.Form):
    formato = forms.ModelChoiceField(label=u'Formato', required=True, queryset=GrupoFormatoReactivo.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'validate[required] formato'}))
    malla = forms.ModelChoiceField(label=u'Malla', required=True, queryset=Malla.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect mallaid'}))
    inicio = forms.DateTimeField(label=u'Fecha de inicio', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechainicio ', 'formwidth': '50'}))
    fin = forms.DateTimeField(label=u'Fecha de fin', required=False, initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechafin ', 'formwidth': '50'}))
    cantidad = forms.IntegerField(label=u'Cantidad de reactivos (profesor)', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1]] valicantidad'}))
    activo = forms.BooleanField(label=u'Activo', required=False,widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'valiactivo'}))

class CronogramaExamenForm(forms.Form):
    planificacion = forms.ModelChoiceField(label=u'Cronograma', queryset=CronogramaPlanificacionExamen.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect planificacionid validate[required]'}))
    carrera = forms.ModelChoiceField(label=u'Carrera', queryset=GrupoCarreraExamen.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect carreraid validate[required]'}))
    nombre = forms.CharField(label=u'Nombre', max_length=255, widget=forms.TextInput(attrs={'formwidth': '100', 'class':'validate[required]'}))
    fecha = forms.DateTimeField(label=u'Fecha', initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechaid validate[required]', 'formwidth': '50'}))
    activo = forms.BooleanField(label=u'Activo', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'activoid'}))

tipo_seleccion = [(1, u'ALEATORIO'), (2, u'RANGO')]
filtro_seleccion = [(1, u'COMPLETO'), (2, u'SECCION')]
tipoexamen = [(1, u'AVANZAR Y RETROCEDER'), (2, u'AVANZAR'), (3, u'TIEMPO')]

class GrupoExamenForm(forms.Form):
    grupo = forms.CharField(label=u'Grupo', max_length=255, widget=forms.TextInput(attrs={'formwidth': '50', 'class': 'validate[required]'}))
    aula = forms.CharField(label=u'Aula', max_length=255, widget=forms.TextInput(attrs={'formwidth': '50', 'class': 'validate[required]'}))
    fecha = forms.DateTimeField(label=u'Fecha', initial=datetime.now().strftime("%d-%m-%Y"), input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datetimepicker fechaid validate[required]', 'formwidth': '100'}))
    inicio = forms.TimeField(label=u'Inicio', input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'class':'inicio validate[required]', 'type':'time', 'formwidth': '50'}))
    fin = forms.TimeField(label=u'Fin', input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'class':'fin validate[required]', 'type':'time', 'formwidth': '50'}))
    cantidad = forms.IntegerField(label=u'Cantidad de preguntas', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '100', 'class': 'validate[custom[onlyNumberSp],min[1],required] valicantidad'}))
    tipo = forms.ChoiceField(label=u'Tipo de examen', required=True, choices=tipoexamen, widget=forms.Select(attrs={'formwidth': '50', 'class': 'tipoexamen', 'style':'width: 100%'}))
    minutos = forms.IntegerField(label=u'Tiempo de pregunta (minutos)', min_value=1, required=False, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1]] valitiempo'}))
    notamax = forms.DecimalField(label=u'Calificación de examen', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1],required] valinotamax'}))
    notamin = forms.DecimalField(label=u'Calificación de aprobación', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '50', 'class': 'validate[custom[onlyNumberSp],min[1],required] valinotamin'}))
    mostrar = forms.BooleanField(label=u'¿Mostrar detalle de examen?', required=False, widget=forms.CheckboxInput(attrs={'formwidth': '100', 'class': 'valiactivo'}))

class GrupoExamenConfiguracionForm(forms.Form):
    bateria = forms.ModelChoiceField(label=u'Bateria', required=False, queryset=BateriaCarrera.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect bateriacarrera', 'style':'width:100%'}))
    estudiante = forms.ModelChoiceField(label=u'Estudiantes', required=False, queryset=MatriculaTitulacion.objects.none(), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect estudiante', 'style':'width:100%', 'multiple':''}))
    tiposeleccion = forms.ChoiceField(label=u'Tipo de selección', required=True, choices=tipo_seleccion, widget=forms.Select(attrs={'formwidth': '50', 'class': 'tiposeleccion', 'style': 'width: 100%'}))
    filtroseleccion = forms.ChoiceField(label=u'Filtro de selección', required=True, choices=filtro_seleccion, widget=forms.Select(attrs={'formwidth': '50', 'class': 'filtroseleccion', 'style': 'width: 100%'}))

tipos_delegado = [(1, u'UPA'), (2, u'CARRERA')]

class DelegadoExamenForm(forms.Form):
    docente = forms.ModelChoiceField(label=u'Docente', required=False, queryset=Profesor.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect docente', 'style': 'width:100%'}))
    tipodelegado = forms.ChoiceField(label=u'Tipos de delegado', required=True, choices=tipos_delegado, widget=forms.Select(attrs={'formwidth': '100', 'class': 'tipodelegado', 'style': 'width: 100%'}))
    principal = forms.BooleanField(label=u'Principal', widget=forms.CheckboxInput(attrs={'formwidth': '50', 'class': 'principal'}))

tipo = [(1,u'Todos'),(2,u'None')]
class SimulacionExamenForm(forms.Form):
    carrera = forms.ModelChoiceField(label=u'Carrera', required=True, queryset=Carrera.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect carrera', 'style': 'width:100%'}))
    bateria = forms.ModelChoiceField(label=u'Bateria', required=False, queryset=Bateria.objects.filter(status=True), widget=forms.Select(attrs={'formwidth': '100', 'class': 'activaselect bateria', 'style': 'width:100%'}))
    seccion = forms.MultipleChoiceField(label=u'Sección', required=False, choices=tipo, widget=forms.Select(attrs={'formwidth': '100', 'class': 'seccion', 'style': 'width: 100%'}))
    cantidad = forms.IntegerField(label=u'Cantidad de preguntas', min_value=1, required=True, widget=forms.NumberInput(attrs={'formwidth': '100', 'class': 'validate[custom[onlyNumberSp],min[1],required] valicantidad'}))