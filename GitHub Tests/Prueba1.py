from flask import Flask, render_template, request
import CoolProp.CoolProp as cp

app = Flask(__name__)

def convertir_unidades(valor, unidad_origen, unidad_destino):
    unidad_origen = unidad_origen.lower()
    unidad_destino = unidad_destino.lower()
    if unidad_origen == unidad_destino:
        return valor
    if unidad_origen in ['kpa', 'mpa', 'psi', 'bar', 'kg/cm²', 'mmhg']:
        if unidad_origen == 'kpa':
            valor = valor
        elif unidad_origen == 'mpa':
            valor = valor * 1000
        elif unidad_origen == 'psi':
            valor = valor / 0.1450377377
        elif unidad_origen == 'bar':
            valor = valor * 100
        elif unidad_origen == 'kg/cm²':
            valor = valor / 10.19716213
        elif unidad_origen == 'mmhg':
            valor = valor / 7.500615613

        if unidad_destino == 'kpa':
            return valor
        elif unidad_destino == 'mpa':
            return valor / 1000
        elif unidad_destino == 'psi':
            return valor * 6.89476
        elif unidad_destino == 'bar':
            return valor / 100
        elif unidad_destino == 'kg/cm²':
            return valor * 98.0665
        elif unidad_destino == 'mmhg':
            return valor * 7.50062
    elif unidad_origen in ['c', 'f', 'k']:
        if unidad_origen == 'c':
            valor = valor
        elif unidad_origen == 'f':
            valor = (valor - 32) * 5 / 9
        elif unidad_origen == 'k':
            valor = valor - 273.15

        if unidad_destino == 'c':
            return valor
        elif unidad_destino == 'f':
            return (valor * 9 / 5) + 32
        elif unidad_destino == 'k':
            return valor + 273.15
    return None

def calcular_propiedades(temp, presion, unidad_temp, unidad_presion):
    temp_k = convertir_unidades(temp, unidad_temp, 'C') + 273.15
    presion_pa = convertir_unidades(presion, unidad_presion, 'kPa') * 1000  # Convertir de kPa a Pa

    densidad, entalpia, entropia = cp.PropsSI(['D', 'H', 'S'], 'T', temp_k, 'P', presion_pa, 'Water')
    viscosidad = cp.PropsSI('V', 'T', temp_k, 'P', presion_pa, 'Water')  # Calcular la viscosidad

    return {
        "temp": convertir_unidades(temp_k - 273.15, 'C', unidad_temp),
        "v": 1 / densidad,  # Volumen específico es el inverso de la densidad
        "h": entalpia / 1000,    # Convertir de J/kg a kJ/kg
        "s": entropia / 1000,    # Convertir de J/kg·K a kJ/kg·K
        "viscosidad": viscosidad * 1000,  # Agregar la viscosidad
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    propiedades = None
    unidad_temp = None
    error = None

    if request.method == 'POST':
        unidad_temp = request.form.get('unidad_temp')
        temperatura_str = request.form.get('temperatura')
        unidad_presion = request.form.get('unidad_presion')
        presion_str = request.form.get('presion')

        if temperatura_str and presion_str:  # Verificar si los campos no están vacíos
            temperatura = float(temperatura_str)
            presion = float(presion_str)
        
            propiedades = calcular_propiedades(temperatura, presion, unidad_temp, unidad_presion)
        else:
            error = "Por favor, rellene todos los campos."

    return render_template('index.html', propiedades=propiedades, unidad_temp=unidad_temp, error=error)

if __name__ == "__main__":
    app.run(debug=True)