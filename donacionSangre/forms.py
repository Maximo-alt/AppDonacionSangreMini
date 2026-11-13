import re
from django import forms
from .models import Usuario, Comuna, TipoSangre, Campana, CentroSalud


# validador rut 
def validar_rut(rut):
    """
    Valida el formato y dígito verificador de un RUT chileno.
    Formatos aceptados: 12345678-9, 12.345.678-9, 12345678-K
    """
    rut = rut.replace('.', '').replace(' ', '').upper()

    # Formato: 7-8 dígitos, guion, dígito verificador (0-9 o K)
    if not re.match(r'^\d{7,8}-[\dK]$', rut):
        return False

    cuerpo, dv = rut.split('-')
    dv = dv.upper()

    # Algoritmo módulo 11
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2

    resto = suma % 11
    dv_esperado = 11 - resto
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)

    return dv == dv_esperado


# registro de usuario
class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label='Contraseña',
        min_length=6
    )
    contrasena_confirmar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'}),
        label='Confirmar contraseña'
    )

    # consentimientos obligatorios
    acepta_terminos = forms.BooleanField(
        required=True,
        label='Acepto los Términos y Condiciones',
        error_messages={'required': 'Debes aceptar los Términos y Condiciones para registrarte.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    acepta_privacidad = forms.BooleanField(
        required=True,
        label='Acepto la Política de Privacidad y Tratamiento de Datos',
        error_messages={'required': 'Debes aceptar la Política de Privacidad para registrarte.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    acepta_datos_salud = forms.BooleanField(
        required=True,
        label='Autorizo el tratamiento de mis datos sensibles de salud',
        error_messages={'required': 'Debes autorizar el tratamiento de datos de salud para registrarte.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'rut', 'mail', 'direccion', 'id_comuna', 'id_tipo_sangre', 'id_centro_salud']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.cl'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'id_comuna': forms.Select(attrs={'class': 'form-control'}),
            'id_tipo_sangre': forms.Select(attrs={'class': 'form-control'}),
            'id_centro_salud': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_comuna'].queryset = Comuna.objects.all().order_by('nombre')
        self.fields['id_tipo_sangre'].queryset = TipoSangre.objects.all().order_by('nombre')
        self.fields['id_centro_salud'].required = False
        self.fields['direccion'].required = False
        # Hacer obligatorios los campos clave
        self.fields['nombre'].required = True
        self.fields['rut'].required = True
        self.fields['mail'].required = True
        self.fields['id_comuna'].required = True
        self.fields['id_tipo_sangre'].required = True

    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip()

        # Validar formato y dígito verificador
        if not validar_rut(rut):
            raise forms.ValidationError(
                'El RUT ingresado no es válido. Verifica el formato (ej: 12345678-9) y el dígito verificador.'
            )

        # Normalizar (sin puntos)
        rut_normalizado = rut.replace('.', '').upper()

        # Verificar unicidad
        if Usuario.objects.filter(rut=rut_normalizado).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con este RUT.')

        return rut_normalizado

    def clean_mail(self):
        mail = self.cleaned_data.get('mail', '').strip().lower()

        if Usuario.objects.filter(mail__iexact=mail).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con este correo.')

        return mail

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get('contrasena')
        pass2 = cleaned_data.get('contrasena_confirmar')
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


# form campaña
class CampanaForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Finalizada', 'Finalizada'),
        ('Cancelada', 'Cancelada'),
        ('Pendiente', 'Pendiente'),
    ]

    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado'
    )

    class Meta:
        model = Campana
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'estado', 'id_centro_salud']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la campaña'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'id_centro_salud': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_centro_salud'].queryset = CentroSalud.objects.all().order_by('nombre')
        self.fields['id_centro_salud'].required = False
        self.fields['fecha_fin'].required = False