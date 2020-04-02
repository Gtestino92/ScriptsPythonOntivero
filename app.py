from flask import Flask, jsonify, request, Response
from resultPedidosMlibreMock import pedidos
from getPedidos import makePedidosFromXlsx
app = Flask(__name__)

@app.route("/pedidosEntregadosML", methods = ['POST'])
def pedidosEntregadosML():
    try:
        pedidosXlsxFile = request.files['pedidosEntregados']
        return str(makePedidosFromXlsx(pedidosXlsxFile))
    except(Exception):
        return Response(status=400)

if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 
