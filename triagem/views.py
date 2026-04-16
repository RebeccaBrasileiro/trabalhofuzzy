from django.shortcuts import render
from .fuzzy_logic import calcular_triagem

def home(request):
    contexto = {}
    if request.method == 'POST':
        # Captura as entradas do formulário
        t = float(request.POST.get('temp'))
        o = float(request.POST.get('spo2'))
        d = float(request.POST.get('dor'))
        
        # Executa a simulação e o cálculo (inferência e defuzzificação) [cite: 137, 187]
        score = calcular_triagem(t, o, d)
        
        # Mapeamento do score numérico para as cores de Manchester [cite: 228-234]
        if score > 85:
            status, cor, classe_css = "EMERGÊNCIA (Vermelho)", "danger", "text-white bg-danger"
        elif score > 60:
            status, cor, classe_css = "URGENTE (Amarelo)", "warning", "text-dark bg-warning"
        elif score > 30:
            status, cor, classe_css = "POUCO URGENTE (Verde)", "success", "text-white bg-success"
        else:
            status, cor, classe_css = "NÃO URGENTE (Azul)", "primary", "text-white bg-primary"
        
        contexto = {
            'score': round(score, 2), # O valor numérico derivado das regras 
            'status': status, 
            'cor': cor,
            'classe_css': classe_css
        }
        
    return render(request, 'triagem.html', contexto)