from flask import Flask, jsonify, request
from resultPedidosMlibreMock import pedidos
from getPedidos import makePedidosFromXlsx
app = Flask(__name__)

@app.route("/pedidosEntregadosML", methods = ['POST'])
def pedidosEntregadosML():
    pedidosXlsxFile = request.files['pedidosEntregados']
    return str(makePedidosFromXlsx(pedidosXlsxFile))
    
if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 