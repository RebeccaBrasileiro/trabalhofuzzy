import io
import base64
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from django.shortcuts import render
from .fuzzy_logic import calcular_triagem


def home(request):
    contexto = {}
    if request.method == "POST":
        try:
            # Captura dados
            t = float(request.POST.get("temp", 0))
            o = float(request.POST.get("spo2", 0))
            d = float(request.POST.get("dor", 0))
            fc = float(request.POST.get("fc", 0))

            print(f">>> Dados recebidos: Temp={t}, O2={o}, Dor={d}, FC={fc}")

            # Chama a lógica
            score, simulador, temperatura, oxigenio, dor, frequencia, prioridade = (
                calcular_triagem(t, o, d, fc)
            )
            print(f">>> Score calculado: {score}")

            # Mapeamento
            if score >= 80:
                status, cor, classe = (
                    "EMERGÊNCIA (Vermelho)",
                    "danger",
                    "text-white bg-danger",
                )
            elif score >= 60:
                status, cor, classe = (
                    "URGENTE (Amarelo)",
                    "warning",
                    "text-dark bg-warning",
                )
            elif score >= 30:
                status, cor, classe = (
                    "POUCO URGENTE (Verde)",
                    "success",
                    "text-white bg-success",
                )
            else:
                status, cor, classe = (
                    "NÃO URGENTE (Azul)",
                    "primary",
                    "text-white bg-primary",
                )

            # Gráfico
            uri_grafico = None
            graficos_pertinencia = []

            # Gera gráficos das funções de pertinência (sempre, independente do simulador)
            variaveis = [
                ("Temperatura", temperatura),
                ("Saturação O2", oxigenio),
                ("Dor", dor),
                ("Frequência Cardíaca", frequencia),
            ]
            for nome, var in variaveis:
                try:
                    var.view()
                    fig = plt.gcf()
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight")
                    buf.seek(0)
                    uri = "data:image/png;base64," + base64.b64encode(
                        buf.read()
                    ).decode("utf-8")
                    graficos_pertinencia.append({"titulo": nome, "imagem": uri})
                    plt.close(fig)
                except Exception as e:
                    print(f"Erro ao gerar gráfico de {nome}: {e}")

            if simulador:
                try:
                    # Gera a imagem do gráfico de saída
                    consequent = list(simulador.ctrl.consequents)[0]
                    consequent.view(sim=simulador)
                    fig = plt.gcf()
                    ax = fig.gca()

                    # Ajusta as cores dos rótulos do gráfico de prioridade
                    cores = {
                        "azul": "blue",
                        "verde": "green",
                        "amarelo": "yellow",
                        "vermelho": "red",
                        "crisp value": "black",
                    }
                    for line in ax.lines:
                        label = line.get_label()
                        if label in cores:
                            line.set_color(cores[label])
                            line.set_linewidth(2)

                    # Atualiza a legenda para ficar consistente com as cores
                    handles, labels = ax.get_legend_handles_labels()
                    ax.legend(handles, labels, frameon=True)

                    # Adiciona linha preta na prioridade defuzzificada
                    if ax is not None:
                        ax.axvline(score, color="black", linestyle="--", linewidth=2)
                        ax.text(
                            score,
                            0.05,
                            f"{round(score, 1)}%",
                            color="black",
                            fontsize=10,
                            fontweight="bold",
                            rotation=90,
                            va="bottom",
                            ha="right",
                        )
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight")
                    buf.seek(0)
                    uri_grafico = "data:image/png;base64," + base64.b64encode(
                        buf.read()
                    ).decode("utf-8")
                    plt.close(fig)
                except Exception as e_grafico:
                    print(f"Erro ao gerar gráfico: {e_grafico}")

            # DICIONÁRIO DE CONTEXTO (Garanta que esses nomes batem com o HTML)
            contexto = {
                "score": round(score, 2),
                "status": status,
                "cor": cor,
                "classe_css": classe,
                "grafico": uri_grafico,
                "graficos_pertinencia": graficos_pertinencia,
                "resultado_pronto": True,  # Chave de segurança para o HTML
            }

        except Exception as e:
            print(f"ERRO GERAL: {e}")
            contexto = {"erro": f"Ocorreu um erro: {e}"}

    return render(request, "triagem.html", contexto)
