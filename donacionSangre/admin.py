from django.contrib import admin
from .models import (
    Region, Comuna, Rol, TipoSangre, TipoCentro, TipoConsentimiento,
    CentroSalud, Usuario, Campana, ConsentimientoUsuario,
    InscripcionCampana, Donacion, Notificacion
)


# ACCIONES PERSONALIZADAS


def marcar_como_finalizada(modeladmin, request, queryset):
    """Acción masiva para cambiar el estado de varias campañas a la vez."""
    queryset.update(estado='Finalizada')

marcar_como_finalizada.short_description = "Marcar campañas seleccionadas como Finalizadas"


# INLINES (Vistas anidadas)

class InscripcionCampanaInline(admin.TabularInline):
    """Permite ver y editar las inscripciones directamente dentro de la campaña."""
    model = InscripcionCampana
    extra = 0  # No muestra filas vacías por defecto
    readonly_fields = ('fecha_inscripcion',)  # La fecha no se edita a mano


# REGISTRO DE MODELOS EN EL ADMIN

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_region')
    list_filter = ('id_region',)
    search_fields = ('nombre',)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(TipoSangre)
class TipoSangreAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(TipoCentro)
class TipoCentroAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


@admin.register(TipoConsentimiento)
class TipoConsentimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'obligatorio')
    list_filter = ('obligatorio',)


@admin.register(CentroSalud)
class CentroSaludAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_tipo_centro', 'id_comuna')
    list_filter = ('id_tipo_centro', 'id_comuna')
    search_fields = ('nombre', 'direccion')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'rut', 'mail', 'id_rol', 'id_tipo_sangre')
    list_filter = ('id_rol', 'id_tipo_sangre')
    search_fields = ('nombre', 'rut', 'mail')


@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'id_centro_salud')
    list_filter = ('estado', 'id_centro_salud')
    search_fields = ('nombre',)
    inlines = [InscripcionCampanaInline]  # <-- Aquí se conecta el Inline
    actions = [marcar_como_finalizada]    # <-- Aquí se conecta la Acción


@admin.register(ConsentimientoUsuario)
class ConsentimientoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario', 'id_tipo_consentimiento', 'fecha_aceptacion', 'aceptado')
    list_filter = ('aceptado', 'id_tipo_consentimiento')


@admin.register(InscripcionCampana)
class InscripcionCampanaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario', 'id_campana', 'fecha_inscripcion', 'asistio')
    list_filter = ('asistio', 'id_campana')
    readonly_fields = ('fecha_inscripcion',)


@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'estado', 'id_donante', 'id_campana', 'id_centro_salud')
    list_filter = ('estado', 'id_centro_salud')
    search_fields = ('id_donante__nombre',) # Búsqueda avanzada por nombre del donante


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario', 'mensaje', 'tipo', 'fecha', 'leida')
    list_filter = ('leida', 'tipo')