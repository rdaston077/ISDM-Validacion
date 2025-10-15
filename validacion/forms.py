from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    fecha_pago = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Pago"
    )
    hora_pago = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora Pago"
    )
    fecha_vencimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Vencimiento"
    )
    hora_vencimiento = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora Vencimiento"
    )
    
    class Meta:
        model = Pago
        fields = [
            'referencia', 'monto', 'fecha_pago', 'hora_pago',
            'fecha_vencimiento', 'hora_vencimiento', 'estado',
            'metodo_pago', 'comision_porcentaje', 'estudiante_nombre',
            'concepto', 'comprobante', 'observaciones'
        ]