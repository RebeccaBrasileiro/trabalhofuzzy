import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def calcular_triagem(temp_val, spo2_val, dor_val, fc_val):
    # --- UNIVERSO DE DISCURSO ---
    temperatura = ctrl.Antecedent(np.arange(34, 43, 0.1), 'temperatura')
    oxigenio = ctrl.Antecedent(np.arange(80, 101, 1), 'oxigenio')
    dor = ctrl.Antecedent(np.arange(0, 11, 1), 'dor')
    frequencia = ctrl.Antecedent(np.arange(0, 221, 1), 'frequencia')
    prioridade = ctrl.Consequent(np.arange(0, 101, 1), 'prioridade')

    # --- FUNÇÕES DE PERTINÊNCIA (FUZZIFICAÇÃO) ---
    temperatura['normal'] = fuzz.trapmf(temperatura.universe, [34, 34, 36.5, 37.5])
    temperatura['febre'] = fuzz.trimf(temperatura.universe, [37, 38, 39.5])
    temperatura['alta'] = fuzz.trapmf(temperatura.universe, [39, 40, 42, 42])

    oxigenio['critico'] = fuzz.trapmf(oxigenio.universe, [80, 80, 88, 92])
    oxigenio['normal'] = fuzz.trapmf(oxigenio.universe, [90, 95, 100, 100])

    dor['leve'] = fuzz.trimf(dor.universe, [0, 0, 4])
    dor['moderada'] = fuzz.trimf(dor.universe, [3, 5, 7])
    dor['severa'] = fuzz.trapmf(dor.universe, [6, 8, 10, 10])

    frequencia['bradicardia'] = fuzz.trapmf(frequencia.universe, [0, 0, 40, 60])
    frequencia['normal'] = fuzz.trapmf(frequencia.universe, [55, 70, 90, 105])
    frequencia['taquicardia'] = fuzz.trimf(frequencia.universe, [100, 120, 145])
    frequencia['critica'] = fuzz.trapmf(frequencia.universe, [135, 160, 220, 220])

    prioridade['azul'] = fuzz.trimf(prioridade.universe, [0, 0, 30])
    prioridade['verde'] = fuzz.trimf(prioridade.universe, [25, 45, 65])
    prioridade['amarelo'] = fuzz.trimf(prioridade.universe, [60, 75, 85])
    prioridade['vermelho'] = fuzz.trapmf(prioridade.universe, [80, 90, 100, 100])

    # --- BASE DE REGRAS AMPLIADA (Hierarquia de Risco) ---
    regras = [
        # --- NÍVEL VERMELHO (EMERGÊNCIA) ---
        # Risco de morte imediato ou falência de órgãos
        ctrl.Rule(oxigenio['critico'], prioridade['vermelho']),
        ctrl.Rule(frequencia['critica'], prioridade['vermelho']),
        ctrl.Rule(temperatura['alta'] & (frequencia['taquicardia'] | dor['severa']), prioridade['vermelho']),
        ctrl.Rule(frequencia['bradicardia'] & oxigenio['critico'], prioridade['vermelho']),
        ctrl.Rule(dor['severa'] & oxigenio['critico'], prioridade['vermelho']),

        # --- NÍVEL AMARELO (URGENTE) ---
        # Sinais vitais instáveis, mas sem risco de morte imediato
        ctrl.Rule(temperatura['alta'] & oxigenio['normal'], prioridade['amarelo']),
        ctrl.Rule(temperatura['febre'] & frequencia['taquicardia'], prioridade['amarelo']),
        ctrl.Rule(frequencia['bradicardia'] & oxigenio['normal'], prioridade['amarelo']),
        ctrl.Rule(dor['severa'] & oxigenio['normal'], prioridade['amarelo']),
        ctrl.Rule(dor['moderada'] & frequencia['taquicardia'], prioridade['amarelo']),

        # --- NÍVEL VERDE (POUCO URGENTE) ---
        # Paciente sintomático, mas sinais vitais estáveis
        ctrl.Rule(temperatura['febre'] & frequencia['normal'] & oxigenio['normal'], prioridade['verde']),
        ctrl.Rule(dor['moderada'] & frequencia['normal'] & temperatura['normal'], prioridade['verde']),
        ctrl.Rule(temperatura['normal'] & frequencia['taquicardia'] & oxigenio['normal'] & dor['leve'], prioridade['verde']),

        # --- NÍVEL AZUL (NÃO URGENTE) ---
        # Todos os parâmetros dentro ou muito próximos da normalidade
        ctrl.Rule(temperatura['normal'] & oxigenio['normal'] & frequencia['normal'] & dor['leve'], prioridade['azul']),
        ctrl.Rule(temperatura['normal'] & oxigenio['normal'] & frequencia['normal'] & dor['moderada'], prioridade['verde']) 
    ]

    # --- SIMULAÇÃO ---
    triagem_ctrl = ctrl.ControlSystem(regras)
    simulador = ctrl.ControlSystemSimulation(triagem_ctrl)

    simulador.input['temperatura'] = temp_val
    simulador.input['oxigenio'] = spo2_val
    simulador.input['dor'] = dor_val
    simulador.input['frequencia'] = fc_val
    
    try:
        simulador.compute()
        return float(simulador.output['prioridade']), simulador
    except Exception:
        # Se cair num "limbo" de regras, retorna prioridade Verde por segurança
        return 45.0, None