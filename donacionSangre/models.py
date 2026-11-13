from django.db import models


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'region'

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_region = models.ForeignKey(Region, models.DO_NOTHING, db_column='id_region')

    class Meta:
        managed = False
        db_table = 'comuna'

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'rol'

    def __str__(self):
        return self.nombre


class TipoSangre(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'tipo_sangre'

    def __str__(self):
        return self.nombre


class TipoCentro(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tipo_centro'

    def __str__(self):
        return self.nombre


class TipoConsentimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    obligatorio = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'tipo_consentimiento'

    def __str__(self):
        return self.nombre


class CentroSalud(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    id_tipo_centro = models.ForeignKey(TipoCentro, models.DO_NOTHING, db_column='id_tipo_centro', blank=True, null=True)
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'centro_salud'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=255)
    rut = models.CharField(unique=True, max_length=12)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    mail = models.CharField(unique=True, max_length=150)
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)
    id_centro_salud = models.ForeignKey(CentroSalud, models.DO_NOTHING, db_column='id_centro_salud', blank=True, null=True)
    id_tipo_sangre = models.ForeignKey(TipoSangre, models.DO_NOTHING, db_column='id_tipo_sangre', blank=True, null=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre} ({self.mail})"


class Campana(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    id_centro_salud = models.ForeignKey(CentroSalud, models.DO_NOTHING, db_column='id_centro_salud', blank=True, null=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'campana'

    def __str__(self):
        return self.nombre


class ConsentimientoUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    id_tipo_consentimiento = models.ForeignKey(TipoConsentimiento, models.DO_NOTHING, db_column='id_tipo_consentimiento')
    fecha_aceptacion = models.DateTimeField(blank=True, null=True)
    aceptado = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'consentimiento_usuario'
        unique_together = (('id_usuario', 'id_tipo_consentimiento'),)


class InscripcionCampana(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    id_campana = models.ForeignKey(Campana, models.DO_NOTHING, db_column='id_campana')
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)
    asistio = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'inscripcion_campana'
        unique_together = (('id_usuario', 'id_campana'),)


class Donacion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    id_donante = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_donante')
    id_campana = models.ForeignKey(Campana, models.DO_NOTHING, db_column='id_campana', blank=True, null=True)
    id_centro_salud = models.ForeignKey(CentroSalud, models.DO_NOTHING, db_column='id_centro_salud', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donacion'


class Notificacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    leida = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'notificacion'