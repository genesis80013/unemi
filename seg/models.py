from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from seg.funciones import ModeloBase

class Periodo(ModeloBase):
    nombre = models.CharField(default='', max_length=200, verbose_name=u'Nombre')
    inicio = models.DateField(verbose_name=u'Fecha inicio', null=True, blank=True)
    fin = models.DateField(verbose_name=u'Fecha fin', null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Periodo"
        verbose_name_plural = u"PeriodoS"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Periodo, self).save(*args, **kwargs)

class Pais(ModeloBase):
    nombre = models.CharField(default='Peru', max_length=100, verbose_name=u"Pais")
    estado = models.BooleanField(default=True, verbose_name=u"Estado")
    imagen = models.FileField(upload_to='pais/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

    def lista_provincia(self):
        return self.provincia_set.all()
       # return Provincia.objects.filter(pais=self)

    class Meta:
        verbose_name = u"Pais"
        verbose_name_plural = u"Paises"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Pais, self).save(*args, **kwargs)


class Provincia(ModeloBase):
    pais = models.ForeignKey(Pais, verbose_name=u'Pais')
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Provincia")

    def __str__(self):
        return u'%s - %s' % (self.pais, self.nombre)

    def lista_cantones (self):
        return self.canton_set.all()


    class Meta:
        verbose_name = u"Provincia"
        verbose_name_plural = u"Provincias"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Provincia, self).save(*args, **kwargs)


class Canton(ModeloBase):
    provincia = models.ForeignKey(Provincia, verbose_name=u'Provincia')
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Ciudad")

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Ciudad"
        verbose_name_plural = u"Ciudades"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Canton, self).save(*args, **kwargs)


class Factura(ModeloBase):
    nombrecliente = models.CharField(default='Peru', max_length=100, verbose_name=u"Producto")
    ruccliente = models.CharField(default='', max_length=15, verbose_name=u"Producto")

    def __str__(self):
        return u'%s - %s' % (self.nombrecliente, self.ruccliente)

    class Meta:
        verbose_name = u"Factura"
        verbose_name_plural = u"Facturas"
        ordering = ['nombrecliente']

    def save(self, *args, **kwargs):
        self.nombrecliente = self.nombrecliente.upper()
        super(Factura, self).save(*args, **kwargs)


class FacturaProducto(ModeloBase):
    factura = models.ForeignKey(Factura)
    producto = models.CharField(default='', max_length=100, verbose_name=u"Producto")
    cantidad = models.FloatField(default=0, verbose_name=u'Cantidad')
    precio = models.FloatField(default=0, verbose_name=u'Precio')

    def __str__(self):
        return u'%s - %s' % (self.factura, self.producto)

    class Meta:
        verbose_name = u"Factura Detalle"
        verbose_name_plural = u"Facturas Detalle"
        ordering = ['factura']
        unique_together = ('factura', 'producto')

    def save(self, *args, **kwargs):
        super(FacturaProducto, self).save(*args, **kwargs)


class Persona(ModeloBase):
    nombres = models.CharField(default='', max_length=30, verbose_name=u'Nombres', blank=False, null=False)
    apellido1 = models.CharField(default='', max_length=30, verbose_name=u'Apellido 1', blank=False, null=False)
    apellido2 = models.CharField(default='', max_length=30, verbose_name=u'Apellido 2', blank=False, null=False)
    cedula = models.CharField(default='', max_length=10, verbose_name=u'Cedula', blank=False, null=True)
    pasaporte = models.CharField(default='', max_length=15, verbose_name=u'Pasaporte', blank=True, null=True)

    def __str__(self):
        return u'%s %s %s' % (self.nombres, self.apellido1, self.apellido2)


class Profesor(ModeloBase):
    persona = models.ForeignKey(Persona, blank=False, null=False, verbose_name=u'Profesor')

    def __str__(self):
        return u'%s %s %s' % (self.persona.nombres, self.persona.apellido1, self.persona.apellido2)


class Modalidad(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

class Nivel(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Nombre', blank=False, null=False)
    periodo = models.ForeignKey(Periodo, blank=False, default='', verbose_name=u'Periodo Lectivo')
    modalidad = models.ForeignKey(Modalidad, blank=False, default='', verbose_name=u'Modalidad')

    def __str__(self):
        return u'%s' % self.nombre

class Asignatura(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre


class Facultad(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre


class Carrera(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre', blank=False, null=False)
    facultad = models.ForeignKey(Facultad, blank=False, null=False, verbose_name=u'Facultad');

    def __str__(self):
        return u'%s' % self.nombre



class Malla(ModeloBase):
    vigente = models.BooleanField(default=True,  verbose_name=u'Vigente', blank=False, null=False)
    nombre = models.CharField(default='nombre', verbose_name=u'Nombre', blank=True, null=True, max_length=100)
    carrera = models.ForeignKey(Carrera, blank=False, null=False, verbose_name=u'Carrera')

    def __str__(self):
        return u'%s' % self.nombre

class NivelMalla(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre


class EjeFormativo(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre


class AsignaturaMalla(ModeloBase):
    asignatura = models.ForeignKey(Asignatura, blank=False, null=False, verbose_name=u'Asignatura')
    malla = models.ForeignKey(Malla, blank=False, null=False, verbose_name=u'Malla')
    optativa = models.BooleanField(default=False,  verbose_name=u'Optativa', blank=False, null=False)
    nivelmalla = models.ForeignKey(NivelMalla, default="", blank=False, null=False, verbose_name=u'Nivel Malla')
    ejeformativo = models.ForeignKey(EjeFormativo, blank=True, null=True, verbose_name=u"Eje Formativo")


class Paralelo(ModeloBase):
    nombre = models.CharField(default='', max_length=10, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

class Materia(ModeloBase):
    nivel = models.ForeignKey(Nivel, blank=False, null=False, verbose_name=u'Nivel')
    asignaturamalla = models.ForeignKey(AsignaturaMalla, blank=False, null=False, verbose_name=u'Asignatura Malla')
    paralelomateria = models.ForeignKey(Paralelo, blank=False, null=False, verbose_name=u'Paralelo Materia')
    inicio = models.DateTimeField(blank=False, null=False, verbose_name=u'Fecha inicio')
    final = models.DateTimeField(blank=False, null=False, verbose_name=u'Fecha final')

    def __str__(self):
        return u'%s' % self.asignaturamalla.asignatura

class ProfesorMateria(ModeloBase):
    profesor = models.ForeignKey(Profesor, blank=False, null=False, verbose_name=u'Profesor')
    materia = models.ForeignKey(Materia, blank=False, null=False, verbose_name=u'Materia')
    inicio = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha inicio')
    final = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha final')

    class Meta:
        verbose_name = u"ProfesorMateria"
        verbose_name_plural = u"ProfesorMaterias"
        ordering = ['materia']


class Sede(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Nombre', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre


class CoordinadorCarrera(ModeloBase):
    periodo = models.ForeignKey(Periodo, blank=False, null=False, verbose_name=u'Periodo lectivo')
    sede = models.ForeignKey(Sede, blank=False, null=False, verbose_name=u'Sede')
    carrera = models.ForeignKey(Carrera, blank=False, null=False, verbose_name=u'Carrera')
    modalidad = models.ForeignKey(Modalidad, blank=False, null=False, verbose_name=u'Modalidad')
    persona = models.ForeignKey(Persona, blank=False, null=False, verbose_name=u'Persona')

    def __str__(self):
        return u'%s' % self.persona

    class Meta:
        ordering = ['carrera__facultad']


ESTADOS_MATRICULA = (
    (1, u'PENDIENTE'),
    (8, u'PENDIENTE DE PAGO'),
    (2, u'MATRICULADO'),
    (3, u'RETIRADO'),
    (4, u'RECHAZADO'),
    (9, u'ANULADO '),
    (6, u'REPROBADO'),
    (5, u'ELIMINADO'),
    (7, u'APROBADO'),
)


class MecanismoTitulacion(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Nombre', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre


class GraduadoMecanismoTitulacion(ModeloBase):
    nombre = models.TextField(default='', verbose_name=u'Nombre')
    mecanismotitulacion = models.ForeignKey(MecanismoTitulacion, blank=True, null=True, verbose_name=u'Mecanismo')
    codigosniese = models.CharField(default='', max_length=2, verbose_name=u"Codigo SNIESE")

    def __str__(self):
        return u'%s' % self.nombre

class PeriodoGrupoTitulacion(ModeloBase):
    nombre = models.CharField(max_length=500, verbose_name=u'Periodo Titulacion')
    descripcion = models.CharField(max_length=1000, verbose_name=u'Observacion Periodo Titulacion')
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)
    creditomin = models.FloatField(default=0)
    creditomax = models.FloatField(default=0)
    horasmodelotitumin = models.IntegerField(default=0)
    horasmodelotitumax = models.IntegerField(default=0)
    porcentajeurkund = models.FloatField(blank=True, null=True, verbose_name=u"Porcentaje Plagio")
    porcientoaprobado = models.FloatField(default=0, verbose_name=u"Porcentaje de aprobacion a cumplir")
    nrevision = models.IntegerField(blank=True, null=True, default=2, verbose_name=u"Número")
    abierto = models.BooleanField(default=True, verbose_name=u"Periodo abierto")
    valortitulacion = models.FloatField(default=0, verbose_name=u'Valor titulacion')
    periodo = models.ForeignKey(Periodo, blank=True, null=True, verbose_name=u"Periodo")

    def __str__(self):
        return u'%s' % self.nombre


class GrupoTitulacion(ModeloBase):
    periodogrupo = models.ForeignKey(PeriodoGrupoTitulacion, blank=True, null=True)
    facultad = models.ForeignKey(Facultad, blank=True, null=True)
    nombre = models.CharField(max_length=500, verbose_name=u'Nombre Grupo')
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

class TipoTitulaciones(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Titulacion')
    codigo = models.CharField(max_length=100, verbose_name=u'Codigo')
    caracteristica = models.CharField(max_length=2000, verbose_name=u'Caracteristicas')
    mecanismotitulacion = models.ForeignKey(GraduadoMecanismoTitulacion, verbose_name=u"Mecanismo Titulación", blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

class AlternativaTitulacion(ModeloBase):
    grupotitulacion = models.ForeignKey(GrupoTitulacion, verbose_name=u'Grupo Titulacion', blank=True, null=True)
    tipotitulacion = models.ForeignKey(TipoTitulaciones, verbose_name=u'Tipo Titulacion', blank=True, null=True)
    alias = models.CharField(max_length=1000, verbose_name=u'Alias')
    horastotales = models.IntegerField(default=0, verbose_name=u'Horas Totales')
    creditos = models.FloatField(default=0, verbose_name=u'Creditos')
    horassemanales = models.IntegerField(default=0, verbose_name=u'Horas Semanales')
    cupo = models.IntegerField(default=0, verbose_name=u'Cupo')
    paralelo= models.CharField(max_length=10, verbose_name=u'Paralelo')
    fechamatriculacion = models.DateField(blank=True, null=True)
    fechamatriculacionfin = models.DateField(blank=True, null=True)
    fechaordinariainicio = models.DateField(blank=True, null=True)
    fechaordinariafin = models.DateField(blank=True, null=True)
    fechaextraordinariainicio = models.DateField(blank=True, null=True)
    fechaextraordinariafin = models.DateField(blank=True, null=True)
    fechaespecialinicio = models.DateField(blank=True, null=True)
    fechaespecialfin = models.DateField(blank=True, null=True)
    facultad = models.ForeignKey(Facultad, blank=True, null=True)
    carrera = models.ForeignKey(Carrera, verbose_name=u'Carrera', blank=True, null=True)

class Inscripcion(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Inscripcion')
    persona = models.ForeignKey(Persona, verbose_name=u'Persona', blank=True, null=True)
    carrera = models.ForeignKey(Carrera, verbose_name=u'Carrera', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

class InscripcionMalla(ModeloBase):
    nombre = models.CharField(max_length=100, verbose_name=u'Inscripcion')
    inscripcion = models.ForeignKey(Inscripcion, verbose_name=u'Inscripcion', blank=True, null=True)
    malla = models.ForeignKey(Malla, verbose_name=u'Malla', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

class MatriculaTitulacion(ModeloBase):
    alternativa = models.ForeignKey(AlternativaTitulacion, blank=True, null=True)
    inscripcion = models.ForeignKey(Inscripcion, blank=True, null=True)
    fechainscripcion = models.DateField(blank=True, null=True, verbose_name=u'Fecha de Inscripcion')
    estado = models.IntegerField(choices=ESTADOS_MATRICULA, default=1, verbose_name=u"Estado de Matricula")
    nota = models.FloatField(blank=True, null=True, verbose_name=u"Nota")

class TipoReactivo(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    estado = models.BooleanField(default=True, verbose_name=u'Estado', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre.upper()

    class Meta:
        verbose_name = u"TipoReactivo"
        verbose_name_plural = u"TipoReactivos"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(TipoReactivo, self).save(*args, **kwargs)

class FormatoReactivo(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    profesor = models.ForeignKey(Profesor, blank=False, null=False, verbose_name=u'Profesor')
    descripcion = models.CharField(default='', max_length=2000, verbose_name=u'Descripcion', blank=True, null=True)
    opcionesmin = models.IntegerField(default='1', verbose_name=u'Cantidad opciones minima', blank=False, null=False)
    opcionesmax = models.IntegerField(default='4', verbose_name=u'Cantidad opciones maxima', blank=False, null=False)
    respuestasmin = models.IntegerField(default='1', verbose_name=u'Cantidad respuestas minima', blank=False, null=False)
    respuestasmax = models.IntegerField(default='4', verbose_name=u'Cantidad respuestas maxima', blank=False, null=False)
    notamin = models.DecimalField(max_digits=4, decimal_places=2, null=False, blank=False, default='1.00',verbose_name=u'Nota Reactivo minima')
    notamax = models.DecimalField(max_digits=4, decimal_places=2,  null=False, blank=False, default='1.00',verbose_name=u'Nota Reactivo maxima')
    tiporeactivo = models.ForeignKey(TipoReactivo, blank=False, null=False, default='',verbose_name=u'Tipo reactivo')
    archivo = models.FileField(upload_to='archivo/%Y/%m/%d', blank=True, null=True)
    valiopciones = models.NullBooleanField(default=True, verbose_name=u'Vali opciones', blank=True, null=True)
    estado = models.BooleanField(default=True, verbose_name=u'Estado', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Formato"
        verbose_name_plural = u"Formatos"
        ordering = ['estado']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.descripcion = self.descripcion.upper()
        super(FormatoReactivo, self).save(*args, **kwargs)

class AtributoReactivo(ModeloBase):
    formatoreactivo = models.ForeignKey(FormatoReactivo, blank=False, null=False, verbose_name=u'Plantilla Reactivo')
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    detalle = models.CharField(default='', max_length=255, verbose_name=u'Detalle', blank=True, null=True)
    estuvisible = models.NullBooleanField(default=True,  verbose_name=u'Visible estudiante', blank=False, null=False)
    profvisible = models.NullBooleanField(default=True,  verbose_name=u'Visible profesor', blank=False, null=False)
    estado = models.NullBooleanField(default=True,  verbose_name=u'Estado', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Atributo"
        verbose_name_plural = u"Atributos"
        ordering = ['formatoreactivo', 'id']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.detalle = self.detalle.upper()
        super(AtributoReactivo, self).save(*args, **kwargs)

class TipoPreguntaReactivo(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    abreviatura = models.CharField(default='', max_length=20, verbose_name=u'Abreviatura', blank=False, null=False)
    activo = models.NullBooleanField(default=True, verbose_name=u'Activo', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"TipoPreguntaReactivo"
        verbose_name_plural = u"TipoPreguntaReactivos"
        ordering = ['activo', 'id']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.abreviatura = self.abreviatura.lower()
        super(TipoPreguntaReactivo, self).save(*args, **kwargs)

class CronogramaPlanificacionExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    periodo = models.ForeignKey(Periodo, blank=False, default='', verbose_name=u'Periodo')
    persona = models.ForeignKey(Persona, blank=False, null=False, verbose_name=u'Persona')
    inicio = models.DateTimeField(blank=False, null=False, verbose_name=u'Inicio')
    fin = models.DateTimeField(blank=False, null=False, verbose_name=u'Fin')
    porcsimilitud = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=5, verbose_name=u'Porcentaje de similitud')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"CronogramaPlanificacion"
        verbose_name_plural = u"CronogramaPlanificaciones"
        ordering = ['-periodo']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(CronogramaPlanificacionExamen, self).save(*args, **kwargs)

class GrupoFormatoReactivo(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupocronograma = models.ForeignKey(CronogramaPlanificacionExamen, blank=False, default='', verbose_name=u'Cronograma')
    formatoreactivo = models.ForeignKey(FormatoReactivo, blank=False, default='', verbose_name=u'Formato')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"GrupoFormatoReactivo"
        verbose_name_plural = u"GrupoFormatoReactivos"
        ordering = ['grupocronograma']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(GrupoFormatoReactivo, self).save(*args, **kwargs)

class GrupoFacultadExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupocronograma = models.ForeignKey(CronogramaPlanificacionExamen, blank=False, default='',verbose_name=u'Cronograma')
    facultad = models.ForeignKey(Facultad, blank=False, default='',verbose_name=u'Cronograma')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"GrupoFacultadExamen"
        verbose_name_plural = u"GrupoFacultadExamenes"
        ordering = ['grupocronograma']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(GrupoFacultadExamen, self).save(*args, **kwargs)

class GrupoCarreraExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupofacultad = models.ForeignKey(GrupoFacultadExamen, blank=False, default='', verbose_name=u'grupofacultad')
    carrera = models.ForeignKey(Carrera, blank=False, default='', verbose_name=u'carrera')
    activocarrera = models.NullBooleanField(default=False, verbose_name=u'activocarrera', blank=True, null=True)
    activomalla = models.NullBooleanField(default=False, verbose_name=u'activomalla', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"GrupoCarreraExamen"
        verbose_name_plural = u"GrupoCarreraExamenes"
        ordering = ['grupofacultad']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(GrupoCarreraExamen, self).save(*args, **kwargs)

class GrupoCarreraMallaExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupocarrera = models.ForeignKey(GrupoCarreraExamen, blank=False, default='', verbose_name=u'grupocarrera')
    malla = models.ForeignKey(Malla, blank=False, default='', verbose_name=u'malla')

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(GrupoCarreraMallaExamen, self).save(*args, **kwargs)

class AsignacionGrupoCoordinador(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupocarrera = models.ForeignKey(GrupoCarreraExamen, blank=True, null=True, default='', verbose_name=u'grupocarrera')
    grupomalla = models.ForeignKey(GrupoCarreraMallaExamen, blank=True, null=True, default='', verbose_name=u'grupomalla')
    coordinador = models.ForeignKey(CoordinadorCarrera, blank=True, null=True, default='', verbose_name=u'coordinador')
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='', verbose_name=u'periodo')
    persona = models.ForeignKey(Persona, blank=True, null=True, default='', verbose_name=u'persona')
    formato = models.ForeignKey(GrupoFormatoReactivo, blank=True, null=True, default='', verbose_name=u'formato')
    inicio = models.DateTimeField(blank=False, null=False, verbose_name=u'Inicio')
    fin = models.DateTimeField(blank=False, null=False, verbose_name=u'Fin')
    activoasignar = models.NullBooleanField(default=True, verbose_name=u'activo', blank=True, null=True)
    estadorevision = models.NullBooleanField(default=False, verbose_name=u'estadorevision', blank=True, null=True)
    estadoasignar = models.NullBooleanField(default=False, verbose_name=u'estadoasignar', blank=True, null=True)
    estadoinicial = models.NullBooleanField(default=True, verbose_name=u'estadoinicial', blank=False, null=False)
    estadofinal = models.NullBooleanField(default=False, verbose_name=u'estadofinal', blank=False, null=False)
    tamaniobateria = models.IntegerField(blank=True, null=True, verbose_name=u'Tamanio bateria')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"AsignacionGrupoCoordinador"
        verbose_name_plural = u"AsignacionGrupoCoordinadores"

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(AsignacionGrupoCoordinador, self).save(*args, **kwargs)

class AsignacionCoordinadorDocente(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    grupocarrera = models.ForeignKey(GrupoCarreraExamen, blank=True, null=True, default='', verbose_name=u'grupocarrera')
    coordinador = models.ForeignKey(CoordinadorCarrera, blank=True, null=True, default='', verbose_name=u'coordinador')
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='', verbose_name=u'periodo')
    persona = models.ForeignKey(Persona, blank=True, null=True, default='', verbose_name=u'persona')
    tiporeactivo = models.ForeignKey(TipoReactivo, blank=True, null=True, default='', verbose_name=u'tiporeactivo')
    inicio = models.DateTimeField(blank=False, null=False, verbose_name=u'Inicio')
    fin = models.DateTimeField(blank=False, null=False, verbose_name=u'Fin')
    activoasignar = models.NullBooleanField(default=True,  verbose_name=u'activo', blank=True, null=True)
    estadorevision = models.NullBooleanField(default=False,  verbose_name=u'estadorevision', blank=True, null=True)
    estadoasignar = models.NullBooleanField(default=False,  verbose_name=u'estadoasignar', blank=True, null=True)
    estadoinicial = models.NullBooleanField(default=True,  verbose_name=u'estadoinicial', blank=False, null=False)
    estadofinal = models.NullBooleanField(default=False,  verbose_name=u'estadofinal', blank=False, null=False)
    tamaniobateria = models.IntegerField(blank=True, null=True, verbose_name=u'Tamanio bateria')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"AsignacionCoordinadorDocente"
        verbose_name_plural = u"AsignacionCoordinadorDocentes"

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(AsignacionCoordinadorDocente, self).save(*args, **kwargs)

class ReactivoArea(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    activo = models.NullBooleanField(default=True, verbose_name=u'activo', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"ReactivoArea"
        verbose_name_plural = u"ReactivoAreas"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(ReactivoArea, self).save(*args, **kwargs)

class AsignacionDocenteReactivo(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'nombre', blank=False, null=False)
    asignacion = models.ForeignKey(AsignacionGrupoCoordinador, blank=True, null=True, default='', verbose_name=u'asignacion')
    formato = models.ForeignKey(GrupoFormatoReactivo, blank=True, null=True, default='', verbose_name=u'asignacion')
    docente = models.ForeignKey(Profesor, blank=True, null=True, default='', verbose_name=u'docente')
    asignatura = models.ForeignKey(AsignaturaMalla, blank=True, null=True, default='', verbose_name=u'asignatura')
    materia = models.ForeignKey(Materia, blank=True, null=True, default='', verbose_name=u'materia')
    persona = models.ForeignKey(Persona, blank=True, null=True, default='', verbose_name=u'persona')
    area = models.ForeignKey(ReactivoArea, blank=True, null=True, default='', verbose_name=u'area')
    inicio = models.DateTimeField(blank=False, null=False, verbose_name=u'inicio')
    fin = models.DateTimeField(blank=False, null=False, verbose_name=u'fin')
    estadoinicial = models.NullBooleanField(default=True, verbose_name=u'estadoinicial', blank=False, null=False)
    estadofinal = models.NullBooleanField(default=False, verbose_name=u'estadofinal', blank=False, null=False)
    revision = models.NullBooleanField(default=False, verbose_name=u'estadofinal', blank=False, null=False)
    cantidad = models.IntegerField(blank=False, default='10', verbose_name=u'cantidad')
    activo = models.NullBooleanField(default=False, verbose_name=u'activo', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"AsignacionDocenteReactivo"
        verbose_name_plural = u"AsignacionDocenteReactivos"
        ordering = ['asignacion']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(AsignacionDocenteReactivo, self).save(*args, **kwargs)

class ReactivoDocente(ModeloBase):
    asignaciondocente = models.ForeignKey(AsignacionDocenteReactivo, blank=True, null=True, default='', verbose_name=u'asignacion')
    tipopregunta = models.ForeignKey(TipoPreguntaReactivo, blank=True, null=True, default='', verbose_name=u'tipopregunta')
    aleatorio = models.NullBooleanField(default=True, verbose_name=u'opcionaleatorio', blank=True, null=True)
    nota = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, verbose_name=u'nota')
    estadoinicial = models.NullBooleanField(default=True, verbose_name=u'Estadoinicial', blank=True, null=True)
    estadofinal = models.NullBooleanField(default=False, verbose_name=u'Estadofinal', blank=True, null=True)
    observacion = models.CharField(default='', max_length=1000, verbose_name=u'observacion', blank=True, null=True)

    class Meta:
        verbose_name = u"Reactivo"
        verbose_name_plural = u"Reactivos"
        ordering = ['asignaciondocente']

    def __str__(self):
        nombre = self.asignaciondocente.formato.formatoreactivo.tiporeactivo.nombre.lower()
        if nombre == "general":
            return u'%s %s' % ('REACTIVO DE ',self.asignaciondocente.area.nombre)
        else:
            return u'%s %s' % ('REACTIVO DE ',self.asignaciondocente.asignatura.asignatura.nombre)

    def save(self, *args, **kwargs):
        super(ReactivoDocente, self).save(*args, **kwargs)

class DetalleReactivoDocente(ModeloBase):
    reactivo = models.ForeignKey(ReactivoDocente, blank=True, null=True, default='', verbose_name=u'reactivo')
    atributo = models.ForeignKey(AtributoReactivo, blank=True, null=True, default='', verbose_name=u'atributo')
    texto = models.TextField(blank=True, null=True, verbose_name=u'texto')
    archivo = models.FileField(upload_to='detallereactivodocente/%Y/%m/%d', blank=True, null=True, verbose_name=u'archivo')
    valorporcentual = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=2, verbose_name=u'valorporcentual')
    activo = models.NullBooleanField(null=True, blank=True, verbose_name=u'activo')

    class Meta:
        verbose_name = u"DetalleReactivoDocente"
        verbose_name_plural = u"DetalleReactivoDocentes"

    def save(self, *args, **kwargs):
        super(DetalleReactivoDocente, self).save(*args, **kwargs)

class Bateria(ModeloBase):
    cronograma = models.ForeignKey(CronogramaPlanificacionExamen, blank=True, null=True, default='',verbose_name=u'cronograma')
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='',verbose_name=u'periodo')

class BateriaCarrera(ModeloBase):
    bateria = models.ForeignKey(Bateria, blank=True, null=True, default='', verbose_name=u'bateria')
    carrera = models.ForeignKey(GrupoCarreraExamen, blank=True, null=True, default='', verbose_name=u'carrera')
    malla = models.ForeignKey(GrupoCarreraMallaExamen, blank=True, null=True, default='', verbose_name=u'malla')
    revision = models.NullBooleanField(default=False, verbose_name=u'revision', blank=True, null=True)

class BateriaExamenComplexivo(ModeloBase):
    bateriacarrera = models.ForeignKey(BateriaCarrera, blank=True, null=True, default='', verbose_name=u'bateriacarrera')
    coordinador = models.ForeignKey(AsignacionGrupoCoordinador, blank=True, null=True, default='', verbose_name=u'periodo')
    tiporeactivo = models.ForeignKey(TipoReactivo, blank=True, null=True, default='', verbose_name=u'tiporeactivo')
    revision = models.NullBooleanField(default=False, verbose_name=u'revision', blank=False, null=False)
    estadoinicial = models.NullBooleanField(default=False, verbose_name=u'estadoinicial', blank=False, null=False)
    estadofinal = models.NullBooleanField(default=False, verbose_name=u'estadofinal', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.bateriacarrera.carrera.carrera.nombre

    class Meta:
        verbose_name = u"BateriaExamenCompolexivo"
        verbose_name_plural = u"BateriasExamenCompolexivo"

    def save(self, *args, **kwargs):
        super(BateriaExamenComplexivo, self).save(*args, **kwargs)

class BateriaDetalle(ModeloBase):
    bateria = models.ForeignKey(BateriaExamenComplexivo, blank=True, null=True, default='', verbose_name=u'bateria')
    reactivo = models.ForeignKey(ReactivoDocente, blank=True, null=True, default='', verbose_name=u'reactivo')

    class Meta:
        verbose_name = u"BateriaDetalle"
        verbose_name_plural = u"BateriaDetalles"

    def save(self, *args, **kwargs):
        super(BateriaDetalle, self).save(*args, **kwargs)

class BateriaEstudiante(ModeloBase):
    bateriacarrera = models.ForeignKey(BateriaCarrera, blank=True, null=True, default='', verbose_name=u'bateriacarrera')
    matricula = models.ForeignKey(MatriculaTitulacion, blank=True, null=True, default='', verbose_name=u'matricula')
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='', verbose_name=u'periodo')

    def __str__(self):
        return u'%s' % self.matricula.inscripcion.persona

    class Meta:
        verbose_name = u"BateriaEstudiante"
        verbose_name_plural = u"BateriaEstudiantes"

    def save(self, *args, **kwargs):
        super(BateriaEstudiante, self).save(*args, **kwargs)

class CronogramaExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='', verbose_name=u'periodo')
    planificacion = models.ForeignKey(CronogramaPlanificacionExamen, blank=True, null=True, default='', verbose_name=u'planificacion')
    carrera = models.ForeignKey(GrupoCarreraExamen, blank=True, null=True, default='', verbose_name=u'carrera')
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'fecha')
    tiempo = models.IntegerField(blank=True, null=True, verbose_name=u'tiempo')
    activo = models.NullBooleanField(default=True, verbose_name=u'activo', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"CronogramaExamen"
        verbose_name_plural = u"CronogramaExamenes"

    def save(self, *args, **kwargs):
        super(CronogramaExamen, self).save(*args, **kwargs)

TIPOS_SELECCION = (
    (1, u'ALEATORIO'),
    (2, u'RANGO'),
    (3, u'AREA-MATERIA'),
)
TIPOS_EXAMEN = (
    (1, u'AVANZAR Y RETROCEDER'),
    (2, u'AVANZAR'),
    (2, u'TIEMPO'),
)

class GrupoExamen(ModeloBase):
    nombre = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    aula = models.CharField(default='', max_length=255, verbose_name=u'Nombre', blank=False, null=False)
    cronogramaexamen = models.ForeignKey(CronogramaExamen, blank=True, null=True, default='', verbose_name=u'cronogramaexamen')
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'fecha')
    inicio = models.TimeField(blank=True, null=True, verbose_name=u'inicio')
    fin = models.TimeField(blank=True, null=True, verbose_name=u'inicio')
    minutos = models.IntegerField(blank=True, null=True, verbose_name=u'tiempo')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'cantidad')
    notamin = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, verbose_name=u'notamin')
    notamax = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2, verbose_name=u'notamax')
    tiposeleccion = models.IntegerField(choices=TIPOS_SELECCION, blank=True, null=True, verbose_name=u"Tipo de seleccion")
    tipoexamen = models.IntegerField(choices=TIPOS_EXAMEN, blank=True, null=True, default=1, verbose_name=u"Tipo de examen")
    activo = models.NullBooleanField(default=True, verbose_name=u'activo', blank=True, null=True)

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Grupoexamen"
        verbose_name_plural = u"Grupoexamenes"

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.aula = self.aula.upper()
        super(GrupoExamen, self).save(*args, **kwargs)

TIPOS_ALEATORIO = (
    (1, u'COMPLETO'),
    (2, u'SECCION'),
)

class GrupoExamenConfiguracion(ModeloBase):
    grupoexamen = models.ForeignKey(GrupoExamen, blank=True, null=True, default='', verbose_name=u'grupoexamen')
    bateria = models.ForeignKey(BateriaCarrera, blank=True, null=True, default='', verbose_name=u'bateria')
    tiposeleccion = models.IntegerField(choices=TIPOS_SELECCION, blank=True, null=True, default=1, verbose_name=u"Tipo de seleccion")
    filtroseleccion = models.IntegerField(choices=TIPOS_ALEATORIO, blank=True, null=True, default=1, verbose_name=u"Filtro de seleccion")

    class Meta:
        verbose_name = u"GrupoExamenConfiguracion"
        verbose_name_plural = u"GrupoExamenConfiguraciones"

    def save(self, *args, **kwargs):
        super(GrupoExamenConfiguracion, self).save(*args, **kwargs)

class GrupoConfiguracion(ModeloBase):
    grupoexamenconfiguracion = models.ForeignKey(GrupoExamenConfiguracion, blank=True, null=True, default='', verbose_name=u'grupoexamenconfiguracion')
    tiporeactivo = models.ForeignKey(TipoReactivo, blank=True, null=True, verbose_name=u'tiporeactivo')
    area = models.ForeignKey(ReactivoArea, blank=True, null=True, default='', verbose_name=u'area')
    asignatura = models.ForeignKey(AsignaturaMalla, blank=True, null=True, default='', verbose_name=u'asignatura')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'cantidad')
    rangoinicio = models.IntegerField(blank=True, null=True, verbose_name=u'rangoinicio')
    rangofin = models.IntegerField(blank=True, null=True, verbose_name=u'rangofin')
    aleatorio = models.NullBooleanField(blank=True, null=True, verbose_name=u'aleatorio')

    class Meta:
        verbose_name = u"GrupoConfiguracion"
        verbose_name_plural = u"GrupoConfiguraciones"

    def save(self, *args, **kwargs):
        super(GrupoConfiguracion, self).save(*args, **kwargs)

class GrupoExamenEstudiante(ModeloBase):
    grupoexamenconfiguracion = models.ForeignKey(GrupoExamenConfiguracion, blank=True, null=True, default='', verbose_name=u'grupoexamenconfiguracion')
    grupoexamen = models.ForeignKey(GrupoExamen, blank=True, null=True, default='', verbose_name=u'grupoexamen')
    estudiante = models.ForeignKey(MatriculaTitulacion, blank=True, null=True, default='', verbose_name=u'estudiante')
    estadoinicial = models.NullBooleanField(blank=True, null=True, default=False, verbose_name=u'estadoinicial')
    estadofinal = models.NullBooleanField(blank=True, null=True, default=False, verbose_name=u'estadofinal')
    observacion = models.CharField(default='', max_length=500, null=True, blank=True, verbose_name=u'Nombre')
    activo = models.NullBooleanField(default=False, verbose_name=u'activo', blank=True, null=True)

    class Meta:
        verbose_name = u"GrupoExamenEstudiante"
        verbose_name_plural = u"GrupoExamenEstudiantes"
        ordering = ['estudiante__inscripcion__persona__apellido1','estudiante__inscripcion__persona__apellido2','estudiante__inscripcion__persona__nombres']

    def save(self, *args, **kwargs):
        super(GrupoExamenEstudiante, self).save(*args, **kwargs)

TIPOS_DELEGADO = (
    (1, u'UPA'),
    (2, u'CARRERA'),
)

class GrupoExamenDelegado(ModeloBase):
    grupoexamen = models.ForeignKey(GrupoExamen, blank=True, null=True, default='', verbose_name=u'grupoexamen')
    docente = models.ForeignKey(Profesor, blank=True, null=True, default='', verbose_name=u'docente')
    principal = models.NullBooleanField(default=True, verbose_name=u'activo', blank=True, null=True)
    tipodelegado = models.IntegerField(choices=TIPOS_DELEGADO, blank=True, null=True, default=1, verbose_name=u"Tipo de delegado")

    def __str__(self):
        return u'%s' % self.grupoexamen.nombre

    class Meta:
        verbose_name = u"GrupoExamenDelegado"
        verbose_name_plural = u"GrupoExamenDelegados"

    def save(self, *args, **kwargs):
        super(GrupoExamenDelegado, self).save(*args, **kwargs)

class EstudianteExamenReactivo(ModeloBase):
    grupoexamenestudiante = models.ForeignKey(GrupoExamenEstudiante, blank=True, null=True, default='', verbose_name=u'grupoexamenestudiante')
    bateriadetalle = models.ForeignKey(BateriaDetalle, blank=True, null=True, default='', verbose_name=u'bateriadetalle')
    estado = models.NullBooleanField(default=None, verbose_name=u'estado', blank=True, null=True)
    revision = models.NullBooleanField(default=False, verbose_name=u'revision', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(EstudianteExamenReactivo, self).save(*args, **kwargs)

class DetalleEstudianteExamen(ModeloBase):
    reactivo = models.ForeignKey(EstudianteExamenReactivo, blank=True, null=True)
    opcion = models.ForeignKey(DetalleReactivoDocente, blank=True, null=True)
    emparejamiento = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(DetalleEstudianteExamen, self).save(*args, **kwargs)

class SimulacionExamen(ModeloBase):
    matricula = models.ForeignKey(MatriculaTitulacion, blank=True, null=True)
    bateriacarrera = models.ForeignKey(BateriaCarrera, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'cantidad')

    def save(self, *args, **kwargs):
        super(SimulacionExamen, self).save(*args, **kwargs)

class SimulacionExamenReactivo(ModeloBase):
    simulacion = models.ForeignKey(SimulacionExamen, blank=True, null=True)
    detallebateria = models.ForeignKey(BateriaDetalle, blank=True, null=True)
    estado = models.NullBooleanField(default=None, verbose_name=u'estado', blank=True, null=True)

class SimulacionDetalle(ModeloBase):
    reactivo = models.ForeignKey(SimulacionExamenReactivo, blank=True, null=True)
    opcion = models.ForeignKey(DetalleReactivoDocente, blank=True, null=True)
    emparejamiento = models.CharField(max_length=100, blank=True, null=True)

class ImpugnacionExamen(ModeloBase):
    periodo = models.ForeignKey(Periodo, blank=True, null=True, default='', verbose_name=u'periodo')
    examen = models.ForeignKey(CronogramaExamen, blank=True, null=True, default='', verbose_name=u'examen')
    grupoexamenestudiante = models.ForeignKey(GrupoExamenEstudiante, blank=True, null=True, default='', verbose_name=u'grupoexamenestudiante')
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=u'fecha')
    estado = models.NullBooleanField(default=None, verbose_name=u'estado', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(ImpugnacionExamen, self).save(*args, **kwargs)

class ImpugnacionDetalle(ModeloBase):
    impugnacion = models.ForeignKey(ImpugnacionExamen, blank=True, null=True, default='', verbose_name=u'impugnacion')
    area = models.ForeignKey(ReactivoArea, blank=True, null=True, default='', verbose_name=u'area')
    asignatura = models.ForeignKey(AsignaturaMalla, blank=True, null=True, default='', verbose_name=u'asignatura')
    reactivo = models.ForeignKey(EstudianteExamenReactivo, blank=True, null=True, default='', verbose_name=u'reactivo')

    def save(self, *args, **kwargs):
        super(ImpugnacionDetalle, self).save(*args, **kwargs)
