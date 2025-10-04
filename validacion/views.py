from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")

def bitacora(request):
    return render(request, "bitacora.html")

def conciliacion(request):
    return render(request, "conciliacion.html")
