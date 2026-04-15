import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def calcular_triagem(temp_val, spo2_val, dor_val):
    # 1. Definição das variáveis (Antecedents e Consequent) [cite: 55, 56, 149-152]
    temperatura = ctrl.Antecedent(np.arange(34, 43, 0.1), 'temperatura')
    oxigenio = ctrl.Antecedent(np.arange(80, 101, 1), 'oxigenio')
    dor = ctrl.Antecedent(np.arange(0, 11, 1), 'dor')
    
    # Saída: Prioridade de 0 a 100 (Manchester)
    prioridade = ctrl.Consequent(np.arange(0, 101, 1), 'prioridade')

    # 2. Funções de Pertinência [cite: 57, 158-162]
    temperatura['fria'] = fuzz.trapmf(temperatura.universe, [34, 34, 35, 36])
    temperatura['normal'] = fuzz.trimf(temperatura.universe, [35.5, 36.5, 37.5])
    temperatura['febre'] = fuzz.trimf(temperatura.universe, [37, 38, 39])
    temperatura['alta'] = fuzz.trapmf(temperatura.universe, [38.5, 40, 42, 42])

    oxigenio['critico'] = fuzz.trapmf(oxigenio.universe, [80, 80, 88, 92])
    oxigenio['normal'] = fuzz.trapmf(oxigenio.universe, [90, 95, 100, 100])

    dor['leve'] = fuzz.trimf(dor.universe, [0, 0, 4])
    dor['moderada'] = fuzz.trimf(dor.universe, [3, 5, 7])
    dor['severa'] = fuzz.trapmf(dor.universe, [6, 8, 10, 10])

    # Saída Manchester [cite: 319-321]
    prioridade['azul'] = fuzz.trimf(prioridade.universe, [0, 0, 25])
    prioridade['verde'] = fuzz.trimf(prioridade.universe, [20, 40, 60])
    prioridade['amarelo'] = fuzz.trimf(prioridade.universe, [50, 70, 85])
    prioridade['vermelho'] = fuzz.trapmf(prioridade.universe, [80, 90, 100, 100])

    # 3. Base de Regras (Simulando o especialista) [cite: 6, 96, 323]
    regra1 = ctrl.Rule(oxigenio['critico'], prioridade['vermelho'])
    regra2 = ctrl.Rule(temperatura['alta'] & dor['severa'], prioridade['vermelho'])
    regra3 = ctrl.Rule(temperatura['normal'] & dor['leve'] & oxigenio['normal'], prioridade['azul'])
    regra4 = ctrl.Rule(temperatura['febre'] | dor['moderada'], prioridade['amarelo'])

    # 4. Simulação [cite: 59, 60, 129]
    triagem_ctrl = ctrl.ControlSystem([regra1, regra2, regra3, regra4])
    simulador = ctrl.ControlSystemSimulation(triagem_ctrl)

    simulador.input['temperatura'] = temp_val
    simulador.input['oxigenio'] = spo2_val
    simulador.input['dor'] = dor_val
    
    simulador.compute() # Máquina de Inferência [cite: 7, 137]
    return simulador.output['prioridade'] # Defuzzificação [cite: 8, 139]