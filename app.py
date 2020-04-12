from flask import Flask, jsonify, request, Response
from resultPedidosMlibreMock import pedidos
from getPedidosFromXlsx import makePedidosFromXlsx
from pedidosMongoService import getPedidosEntregados
from mongoConnection import mongo

def createAppOntivero(config_object='settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    mongo.init_app(app)
    return app

app = createAppOntivero()

@app.route("/pedidosEntregadosML", methods = ['POST'])
def pedidosEntregadosML():
    try:
        pedidosXlsxFile = request.files['pedidosEntregados']
        return str(makePedidosFromXlsx(pedidosXlsxFile))
    except(Exception):
        return Response(status=400)

@app.route("/getPedidosEntregadosDb", methods = ['GET'])
def getPedidosEntregadosDb():
    try:
        return str(getPedidosEntregados())
    except(Exception):
        return Response(status=400)

if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 
