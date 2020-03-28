from flask import Flask
from resultPedidosMlibreMock import pedidos
app = Flask(__name__)

@app.route("/pedidosEntregadosML")
def pedidosEntregadosML():
    return str(pedidos)

if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 