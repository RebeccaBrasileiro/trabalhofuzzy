import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def calcular_triagem(temp_val, spo2_val, dor_val):
    # 1. Definição do Universo de Discurso [cite: 55, 56, 153-156]
    # Temperatura: de 34 a 42 graus
    temperatura = ctrl.Antecedent(np.arange(34, 43, 0.1), 'temperatura')
    # Oxigênio: de 80% a 100%
    oxigenio = ctrl.Antecedent(np.arange(80, 101, 1), 'oxigenio')
    # Dor: escala de 0 a 10
    dor = ctrl.Antecedent(np.arange(0, 11, 1), 'dor')
    
    # Saída: Prioridade (Manchester) de 0 a 100 [cite: 227]
    prioridade = ctrl.Consequent(np.arange(0, 101, 1), 'prioridade')

    # 2. Funções de Pertinência (Fuzzificação) [cite: 5, 57, 158-162]
    # Usamos 4 números (trapmf) nas extremidades para cobrir faixas contínuas de risco [cite: 254, 257]
    temperatura['normal'] = fuzz.trapmf(temperatura.universe, [34, 34, 36.5, 37.5])
    temperatura['febre'] = fuzz.trimf(temperatura.universe, [37, 38, 39])
    temperatura['alta'] = fuzz.trapmf(temperatura.universe, [38.5, 40, 42, 42])

    oxigenio['critico'] = fuzz.trapmf(oxigenio.universe, [80, 80, 88, 92])
    oxigenio['normal'] = fuzz.trapmf(oxigenio.universe, [90, 95, 100, 100])

    dor['leve'] = fuzz.trimf(dor.universe, [0, 0, 4])
    dor['moderada'] = fuzz.trimf(dor.universe, [3, 5, 7])
    dor['severa'] = fuzz.trapmf(dor.universe, [6, 8, 10, 10])

    # Conjuntos de Saída [cite: 318-321]
    prioridade['azul'] = fuzz.trimf(prioridade.universe, [0, 0, 30])
    prioridade['verde'] = fuzz.trimf(prioridade.universe, [25, 45, 65])
    prioridade['amarelo'] = fuzz.trimf(prioridade.universe, [60, 75, 85])
    prioridade['vermelho'] = fuzz.trapmf(prioridade.universe, [80, 90, 100, 100])

    # 3. Base de Regras Fuzzy (Ajustada para Cobertura Total) [cite: 6, 96, 169-173]
    # Usamos o operador | (OU) para garantir que as regras sejam disparadas mais facilmente [cite: 178]
    regra1 = ctrl.Rule(oxigenio['critico'], prioridade['vermelho'])
    regra2 = ctrl.Rule(temperatura['alta'] | dor['severa'], prioridade['vermelho'])
    regra3 = ctrl.Rule(temperatura['normal'] | oxigenio['normal'], prioridade['azul'])
    regra4 = ctrl.Rule(temperatura['febre'] | dor['moderada'], prioridade['amarelo'])

    # 4. Montagem e Simulação do Sistema [cite: 59, 60, 129]
    triagem_ctrl = ctrl.ControlSystem([regra1, regra2, regra3, regra4])
    simulador = ctrl.ControlSystemSimulation(triagem_ctrl)

    # Entrada de dados (Inputs) [cite: 136]
    simulador.input['temperatura'] = temp_val
    simulador.input['oxigenio'] = spo2_val
    simulador.input['dor'] = dor_val
    
    # 5. Processamento e Defuzzificação com Proteção contra Erros [cite: 8, 137, 187]
    try:
        simulador.compute()
        return simulador.output['prioridade']
    except KeyError:
        # Caso nenhum conjunto seja ativado (valor fora do esperado), retorna um padrão seguro
        return 25.0