from flask import Flask, render_template, request

app = Flask(__name__)

# Página principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Datos del formulario
        horas_fuera_pico = float(request.form["horas_fuera_pico"])
        horas_pico = float(request.form["horas_pico"])
        consumo_por_hora = float(request.form["consumo_por_hora"])
        
        # Tarifas (ejemplo, ajusta con valores reales de ANDE)
        tarifa_pico = 700  # Gs/kWh en hora pico
        tarifa_fuera_pico = 350  # Gs/kWh fuera de pico

        # Consumo total
        consumo_total = (horas_pico + horas_fuera_pico) * consumo_por_hora

        # Costos
        costo_pico = horas_pico * consumo_por_hora * tarifa_pico
        costo_fuera_pico = horas_fuera_pico * consumo_por_hora * tarifa_fuera_pico
        costo_total = costo_pico + costo_fuera_pico

        return render_template("resultados.html",
                               horas_pico=horas_pico,
                               horas_fuera_pico=horas_fuera_pico,
                               consumo_total=consumo_total,
                               costo_total=costo_total,
                               costo_pico=costo_pico,
                               costo_fuera_pico=costo_fuera_pico)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
