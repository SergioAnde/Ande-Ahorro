from flask import Flask, render_template_string, request
import math

app = Flask(__name__)

# --- BASE DE DATOS ---
electrodomesticos_db = {
    "heladera": 300, "congelador": 1500, "lavarropa": 1000, "plancha": 1000,
    "microondas": 1200, "televisor": 120, "computadora": 200, "ducha_electrica": 4400,
    "aire12000btu": 1500, "aire24000btu": 3000, "cocina_2hornallas": 3500,
    "horno": 2700, "estufa": 1200, "termocalefon": 1500
}

tarifas_punta = [(500, 669.17), (1000, 696.42), (999999, 721.68)]
tarifas_fuera_punta = [(500, 263.88), (1000, 274.62), (999999, 284.58)]

punta_verano = list(range(12,16)) + list(range(18,22))
punta_invierno = list(range(18,22))

# --- FUNCIONES ---
def obtener_precio(consumo_mensual, horario):
    lista = tarifas_punta if horario == "punta" else tarifas_fuera_punta
    for limite, precio in lista:
        if consumo_mensual <= limite:
            return precio
    return lista[-1][1]

def horas_desde_rango(rango_str):
    hi, mi, hf, mf = *map(int, rango_str.split("-")[0].split(":")), *map(int, rango_str.split("-")[1].split(":"))
    inicio, fin = hi + mi/60, hf + mf/60
    if fin <= inicio: fin += 24
    consumo_por_hora, hora_actual = {}, int(inicio)
    consumo_por_hora[hora_actual % 24] = 1 - (inicio - hora_actual)
    hora_actual += 1
    while hora_actual < int(fin):
        consumo_por_hora[hora_actual % 24] = 1
        hora_actual += 1
    consumo_por_hora[int(fin) % 24] = fin - int(fin)
    return {h: v for h, v in consumo_por_hora.items() if v > 0}

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        electrodomesticos_usuario = {}
        for nombre in electrodomesticos_db:
            cantidad = request.form.get(f"cantidad_{nombre}")
            rango = request.form.get(f"rango_{nombre}")
            if cantidad and int(cantidad) > 0:
                if nombre in ["heladera", "congelador"]:
                    consumo_por_hora = {h: 1 for h in range(24)}
                else:
                    consumo_por_hora = horas_desde_rango(rango)
                electrodomesticos_usuario[nombre] = {
                    "consumo_por_hora": consumo_por_hora,
                    "cantidad": int(cantidad)
                }

        factura_gs = float(request.form["factura"])
        temporada = request.form["temporada"].lower()
        punta = punta_verano if temporada == "verano" else punta_invierno
        domingos = [6, 13, 20, 27]

        perfil_horario = [0]*24
        for nombre, datos in electrodomesticos_usuario.items():
            potencia_kw = electrodomesticos_db[nombre] / 1000
            for h, fraccion in datos["consumo_por_hora"].items():
                perfil_horario[h % 24] += potencia_kw * fraccion * datos["cantidad"]

        consumo_mensual_kwh = sum(perfil_horario) * 30

        costo_mensual_actual = 0
        for dia in range(30):
            es_domingo = dia in domingos
            for h in range(24):
                horario = "fuera" if es_domingo else ("punta" if h in punta else "fuera")
                precio = obtener_precio(consumo_mensual_kwh, horario)
                costo_mensual_actual += perfil_horario[h] * precio

        perfil_opt = perfil_horario[:]
        for h in punta:
            if perfil_opt[h] > 0:
                for destino in range(24):
                    if destino not in punta:
                        perfil_opt[destino] += perfil_opt[h]
                        perfil_opt[h] = 0
                        break

        costo_dyn = 0
        for dia in range(30):
            es_domingo = dia in domingos
            for h in range(24):
                horario = "fuera" if es_domingo else ("punta" if h in punta else "fuera")
                precio = obtener_precio(consumo_mensual_kwh, horario)
                costo_dyn += perfil_opt[h] * precio

        consumoactual = [
            (50, 311.55), (150, 349.89), (300, 365.45),
            (500, 403.82), (1000, 420.27), (999999, 435.51)
        ]
        c1, c2, c3, c4, c5 = 50*311.55, 150*349.89, 300*365.45, 500*403.82, 1000*420.27

        if factura_gs <= c1:
            consumo_viejo = factura_gs / 311.55
        elif factura_gs <= c2:
            consumo_viejo = factura_gs / 349.89
        elif factura_gs <= c3:
            consumo_viejo = factura_gs / 365.45
        elif factura_gs <= c4:
            consumo_viejo = factura_gs / 403.82
        elif factura_gs <= c5:
            consumo_viejo = factura_gs / 420.27
        else:
            consumo_viejo = factura_gs / 435.51

        ahorro_pct = 100*(costo_mensual_actual - costo_dyn)/costo_mensual_actual if costo_mensual_actual else 0

        resultado = {
            "consumo": round(consumo_mensual_kwh, 1),
            "costo_actual": round(costo_mensual_actual, 0),
            "costo_opt": round(costo_dyn, 0),
            "ahorro": round(costo_mensual_actual - costo_dyn, 0),
            "ahorro_pct": round(ahorro_pct, 1),
            "consumo_viejo": round(consumo_viejo, 2)
        }

    return render_template_string("index.html", electrodomesticos=electrodomesticos_db, resultado=resultado)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
