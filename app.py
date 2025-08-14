from flask import Flask, render_template, request
import math

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    ahorro = None
    if request.method == 'POST':
        consumo_viejo = float(request.form['consumo_viejo'])
        consumo_mensual_kwh = float(request.form['consumo_mensual_kwh'])
        precio_punta = float(request.form['precio_punta'])
        precio_fuera_punta = float(request.form['precio_fuera_punta'])

        # Cálculo tarifa normal
        costo_normal = consumo_viejo * ((precio_punta + precio_fuera_punta) / 2)

        # Cálculo tarifa dinámica
        costo_dyn = consumo_mensual_kwh * ((precio_punta + precio_fuera_punta) / 2)

        # Ajuste de consumos para comparación justa
        diff_kwh = consumo_viejo - consumo_mensual_kwh
        precio_promedio = (precio_punta + precio_fuera_punta) / 2
        costo_dyn_ajustado = costo_dyn + diff_kwh * precio_promedio

        ahorro = round(costo_normal - costo_dyn_ajustado, 2)

    return render_template('index.html', ahorro=ahorro)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
