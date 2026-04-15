from django.shortcuts import render
from .fuzzy_logic import calcular_triagem

def home(request):
    contexto = {}
    if request.method == 'POST':
        t = float(request.POST.get('temp'))
        o = float(request.POST.get('spo2'))
        d = float(request.POST.get('dor'))
        
        score = calcular_triagem(t, o, d)
        
        if score > 85: status, cor = "EMERGÊNCIA", "danger"
        elif score > 60: status, cor = "URGENTE", "warning"
        elif score > 30: status, cor = "POUCO URGENTE", "success"
        else: status, cor = "NÃO URGENTE", "primary"
        
        contexto = {'score': round(score, 2), 'status': status, 'cor': cor}
        
    return render(request, 'triagem.html', contexto)