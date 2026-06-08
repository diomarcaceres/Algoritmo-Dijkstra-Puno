from flask import Flask, render_template, request, jsonify
import heapq
import math

app = Flask(__name__)

coords = {
    "Puno":                  (-15.8422, -70.0199),
    "Azángaro":              (-14.9097, -70.1942),
    "Carabaya":              (-14.0833, -69.9333),
    "Chucuito":              (-16.3833, -69.8167),
    "El Collao":             (-16.4028, -69.2261),
    "Huancané":              (-15.2058, -69.7547),
    "Lampa":                 (-15.3631, -70.3697),
    "Melgar":                (-14.8833, -70.5833),
    "Moho":                  (-15.3500, -69.4833),
    "San Antonio de Putina": (-14.9167, -69.8667),
    "San Román":             (-15.4994, -70.1336),
    "Sandia":                (-14.2833, -69.4167),
    "Yunguyo":               (-16.1972, -69.0861),
}

adyacencias = {
    "Puno":                  ["San Román", "Chucuito", "Huancané", "El Collao"],
    "San Román":             ["Puno", "Lampa", "Azángaro", "Huancané"],
    "Lampa":                 ["San Román", "Azángaro", "Melgar"],
    "Azángaro":              ["San Román", "Lampa", "Melgar", "Huancané", "San Antonio de Putina", "Carabaya"],
    "Melgar":                ["Lampa", "Azángaro", "Carabaya"],
    "Carabaya":              ["Azángaro", "Melgar", "Sandia"],
    "Sandia":                ["Carabaya", "San Antonio de Putina"],
    "San Antonio de Putina": ["Azángaro", "Sandia", "Huancané", "Moho"],
    "Huancané":              ["Puno", "San Román", "Azángaro", "San Antonio de Putina", "Moho"],
    "Moho":                  ["Huancané", "San Antonio de Putina", "Yunguyo"],
    "Yunguyo":               ["Moho", "El Collao"],
    "El Collao":             ["Puno", "Yunguyo", "Chucuito"],
    "Chucuito":              ["Puno", "El Collao"],
}

def haversine(c1, c2):
    R = 6371
    lat1, lon1 = c1; lat2, lon2 = c2
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def crear_grafo():
    grafo = {}
    for ciudad in adyacencias:
        grafo[ciudad] = {}
        for vecino in adyacencias[ciudad]:
            grafo[ciudad][vecino] = haversine(coords[ciudad], coords[vecino])
    return grafo

grafo = crear_grafo()

def dijkstra(inicio, fin):
    cola = [(0, inicio, [])]
    visitados = set()
    while cola:
        costo, nodo, camino = heapq.heappop(cola)
        if nodo in visitados:
            continue
        camino = camino + [nodo]
        visitados.add(nodo)
        if nodo == fin:
            return camino, round(costo, 1)
        for vecino, peso in grafo.get(nodo, {}).items():
            heapq.heappush(cola, (costo + peso, vecino, camino))
    return [], 0

@app.route("/")
def index():
    return render_template("index.html", ciudades=sorted(coords.keys()))

@app.route("/ruta", methods=["POST"])
def ruta():
    data = request.json
    inicio = data["inicio"]
    fin = data["fin"]
    camino, distancia = dijkstra(inicio, fin)
    ruta_coords = [{"lat": coords[n][0], "lng": coords[n][1], "nombre": n} for n in camino]
    return jsonify({
        "ruta": ruta_coords,
        "camino": camino,
        "distancia": distancia,
        "encontrado": len(camino) > 0
    })

if __name__ == "__main__":
    app.run(debug=True)