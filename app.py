from flask import Flask, jsonify, request, Response
from models.pedido import Pedido
from models.maceta import Maceta
from resultPedidosMlibreMock import pedidos
from getPedidosFromXlsx import makePedidosFromXlsx
from pedidosMongoService import getPedidosEntregados,getListRecomOrderByProb
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

@app.route("/getRecomendaciones", methods = ['POST'])
def getCodigosRecomendacion():
    try:
        pedido = makePedidoByRequest(request)
        return str(getListRecomOrderByProb(pedido))
    except(Exception):
       return Response(status=400)

def makePedidoByRequest(request):
    listadoMacetas = []
    for i in range(len(int(request.data("cantModelos")))):
        codigo = request.data("codigoNew" + i)
        cantSolicitada = int(request.data("cantSolicitada" + i))
        listadoMacetas.append(Maceta(codigo,cantSolicitada))
    return Pedido(listadoMacetas,"")
     

if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 
