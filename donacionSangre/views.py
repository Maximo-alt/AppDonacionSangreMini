from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Campana, Usuario, InscripcionCampana, TipoConsentimiento, ConsentimientoUsuario
from .forms import RegistroForm, CampanaForm
import time 

# Create your views here.

def es_admin(request):
    """Devuelve True si el usuario logueado tiene rol Administrador."""
    return request.session.get('usuario_rol') == 'Admin'

def index(request):
    campanas = Campana.objects.filter(estado='Activa')[:6]  # Próximas 6 campañas activas
    return render(request, 'campanasapp/index.html', {'campanas': campanas})

def campanas(request):
    campanas = Campana.objects.all()
    
    # Obtenemos los IDs de las campañas en las que está inscrito el usuario
    campanas_inscritas = []
    if request.session.get('usuario_id'):
        usuario_id = request.session['usuario_id']
        campanas_inscritas = list(
            InscripcionCampana.objects.filter(id_usuario_id=usuario_id)
            .values_list('id_campana_id', flat=True)
        )
    
    return render(request, 'campanasapp/campanas.html', {
        'campanas': campanas,
        'campanas_inscritas': campanas_inscritas,
    })

#registro
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.contrasena = make_password(form.cleaned_data['contrasena'])
            usuario.id_rol_id = 2  # Donante por defecto
            usuario.save()

            # Registrar los consentimientos aceptados
            nombres_consentimientos = [
                'Términos y Condiciones',
                'Política de Privacidad',
                'Datos Sensibles de Salud'
            ]
            tipos = TipoConsentimiento.objects.filter(nombre__in=nombres_consentimientos)
            for tipo in tipos:
                ConsentimientoUsuario.objects.create(
                    id_usuario=usuario,
                    id_tipo_consentimiento=tipo,
                    aceptado=True
                )

            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = RegistroForm()

    return render(request, 'campanasapp/registro.html', {'form': form})




def login_view(request):
    # ==========================================
    # 1. CONFIGURACIÓN DE SEGURIDAD (RATE LIMITING)
    # ==========================================
    MAX_INTENTOS = 3
    TIEMPO_BLOQUEO = 15  # 60 segundos (1 minuto) de bloqueo

    # Verificar si el usuario está bloqueado actualmente
    bloqueado_hasta = request.session.get('bloqueado_hasta', 0)
    if time.time() < bloqueado_hasta:
        tiempo_restante = int(bloqueado_hasta - time.time())
        messages.error(request, f'Demasiados intentos fallidos. Por seguridad, intenta de nuevo en {tiempo_restante} segundos.')
        return render(request, 'campanasapp/login.html')

    # ==========================================
    # 2. PROCESAMIENTO DEL FORMULARIO
    # ==========================================
    if request.method == 'POST':
        mail = request.POST.get('mail')
        contrasena = request.POST.get('contrasena')
        recordarme = request.POST.get('recordarme') # Checkbox de recordar

        try:
            usuario = Usuario.objects.select_related('id_rol').get(mail=mail)
            
            # --- CASO A: CONTRASEÑA CORRECTA ---
            if check_password(contrasena, usuario.contrasena):
                
                # 1. Reiniciamos el contador de intentos fallidos
                request.session['login_attempts'] = 0
                
                # 2. Guardamos los datos en la Session Cookie
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol'] = usuario.id_rol.nombre if usuario.id_rol else 'Donante'
                
                # 3. Creamos la respuesta
                response = redirect('index')
                
                # 4. Lógica de Cookie de Correo (Validando el Consentimiento)
                consentimiento_cookies = request.COOKIES.get('cookie_consent')
                
                if recordarme and consentimiento_cookies == 'accepted':
                    # Solo guardamos si marcó la casilla Y aceptó las cookies
                    response.set_cookie('correo_recordado', mail, max_age=60*60*24*7) # 7 días
                else:
                    # Si no marcó o no aceptó, nos aseguramos de borrar cualquier cookie previa
                    response.delete_cookie('correo_recordado')
                
                messages.success(request, f'¡Bienvenido de nuevo, {usuario.nombre}!')
                return response
                
            # --- CASO B: CONTRASEÑA INCORRECTA ---
            else:
                # Aumentamos el contador de intentos fallidos
                intentos = request.session.get('login_attempts', 0) + 1
                request.session['login_attempts'] = intentos

                if intentos >= MAX_INTENTOS:
                    # Bloqueamos la sesión
                    request.session['bloqueado_hasta'] = time.time() + TIEMPO_BLOQUEO
                    messages.error(request, 'Has excedido los 3 intentos permitidos. Cuenta bloqueada.')
                else:
                    intentos_restantes = MAX_INTENTOS - intentos
                    messages.error(request, f'Contraseña incorrecta. Te quedan {intentos_restantes} intentos.')

        # --- CASO C: EL CORREO NO EXISTE ---
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta registrada con ese correo.')

    # ==========================================
    # 3. RENDERIZADO (Si es GET o si hubo error en POST)
    # ==========================================
    return render(request, 'campanasapp/login.html')

#log out
def logout_view(request):
    request.session.flush()  # Borra toda la sesión
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')

# C: Crear campaña
def campana_crear(request):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión para crear una campaña.')
        return redirect('login')
    
    if not es_admin(request):
        messages.error(request, 'Solo los administradores pueden crear campañas.')
        return redirect('campanas')

    if request.method == 'POST':
        form = CampanaForm(request.POST)
        if form.is_valid():
            campana = form.save(commit=False)
            campana.id_usuario_id = request.session['usuario_id']
            campana.save()
            messages.success(request, 'Campaña creada exitosamente.')
            return redirect('campanas')
    else:
        form = CampanaForm()

    return render(request, 'campanasapp/campana_form.html', {'form': form, 'accion': 'Crear'})


# U: Editar campaña 
def campana_editar(request, pk):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión.')
        return redirect('login')
    
    if not es_admin(request):
        messages.error(request, 'Solo los administradores pueden editar campañas.')
        return redirect('campanas')

    campana = get_object_or_404(Campana, pk=pk)

    if request.method == 'POST':
        form = CampanaForm(request.POST, instance=campana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaña actualizada correctamente.')
            return redirect('campanas')
    else:
        form = CampanaForm(instance=campana)

    return render(request, 'campanasapp/campana_form.html', {'form': form, 'accion': 'Editar'})


# D: Eliminar campaña
def campana_eliminar(request, pk):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión.')
        return redirect('login')
    
    if not es_admin(request):
        messages.error(request, 'Solo los administradores pueden eliminar campañas.')
        return redirect('campanas')

    campana = get_object_or_404(Campana, pk=pk)

    if request.method == 'POST':
        campana.delete()
        messages.success(request, 'Campaña eliminada correctamente.')
        return redirect('campanas')

    return render(request, 'campanasapp/campana_confirmar_eliminar.html', {'campana': campana})

def inscribirse_campana(request, pk):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión para inscribirte en una campaña.')
        return redirect('login')

    campana = get_object_or_404(Campana, pk=pk)
    usuario_id = request.session['usuario_id']

    # Verificar que la campaña esté activa o pendiente
    if campana.estado in ['Finalizada', 'Cancelada']:
        messages.error(request, f'No puedes inscribirte en "{campana.nombre}" porque está {campana.estado.lower()}.')
        return redirect('campanas')

    # Verificar si ya está inscrito
    if InscripcionCampana.objects.filter(id_usuario_id=usuario_id, id_campana=campana).exists():
        messages.warning(request, 'Ya estás inscrito en esta campaña.')
        return redirect('campanas')

    # Crear la inscripción
    InscripcionCampana.objects.create(
        id_usuario_id=usuario_id,
        id_campana=campana,
        asistio=False
    )
    messages.success(request, f'¡Te has inscrito en "{campana.nombre}"!')
    return redirect('campanas')

def desinscribirse_campana(request, pk):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión.')
        return redirect('login')

    campana = get_object_or_404(Campana, pk=pk)
    usuario_id = request.session['usuario_id']

    inscripcion = InscripcionCampana.objects.filter(
        id_usuario_id=usuario_id,
        id_campana=campana
    ).first()

    if inscripcion:
        inscripcion.delete()
        messages.success(request, f'Te has desinscrito de "{campana.nombre}".')
    else:
        messages.warning(request, 'No estabas inscrito en esta campaña.')

    return redirect('campanas')

def campana_detalle(request, pk):
    campana = get_object_or_404(
        Campana.objects.select_related('id_centro_salud', 'id_usuario'),
        pk=pk
    )

    # Saber si el usuario está inscrito
    inscrito = False
    if request.session.get('usuario_id'):
        inscrito = InscripcionCampana.objects.filter(
            id_usuario_id=request.session['usuario_id'],
            id_campana=campana
        ).exists()

    # Contar inscritos
    total_inscritos = InscripcionCampana.objects.filter(id_campana=campana).count()

    return render(request, 'campanasapp/campana_detalle.html', {
        'campana': campana,
        'inscrito': inscrito,
        'total_inscritos': total_inscritos,
    })