from flask import Flask, jsonify, request, Response
import traceback
import pandas as pd
from models.pedido import Pedido
from models.maceta import Maceta
from resultPedidosMlibreMock import pedidos
from getPedidosFromXlsx import makePedidosFromXlsx
from pedidosMongoService import getPedidosEntregados,getListRecomOrderByProb
from mongoConnection import mongo
from flask_mysqldb import MySQL
from macetasSqlService import getCodigoByTituloMlibre, getFormatoByCodigoNew
from exceptions.singularMatException import SingularMatException
from exceptions.noPedidosRegistradosException import NoPedidosRegistradosException

def createAppOntivero(config_object='settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    mongo.init_app(app)
    return app

app = createAppOntivero()
mysql = MySQL(app)

@app.route("/pedidosEntregadosML", methods = ['POST'])
def pedidosEntregadosML():
    try:
        pedidosXlsxFile = request.files['pedidosEntregados']
        # obtengo info de titulo y codigo nuevo
        codigosMacetasMlibre = getCodigoByTituloMlibre(mysql)
        return str(makePedidosFromXlsx(pedidosXlsxFile,codigosMacetasMlibre))
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)

@app.route("/getPedidosEntregadosDb", methods = ['GET'])
def getPedidosEntregadosDb():
    try:
        formatoByCodigoDict = getFormatoByCodigoNew(mysql)
        return str(getPedidosEntregados(formatoByCodigoDict))
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)


@app.route("/getRecomendaciones", methods = ['POST'])
def getCodigosRecomendacion():
    try:
        pedido = makePedidoByRequest(request)
        formatoByCodigoDict = getFormatoByCodigoNew(mysql)
        return str(getListRecomOrderByProb(pedido,formatoByCodigoDict))
    except SingularMatException as singMatE:
        return Response(status=singMatE.code)
    except NoPedidosRegistradosException as noPedidosE:
        return Response(status=noPedidosE.code)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)

def makePedidoByRequest(request):
    listadoMacetas = []
    for i in range(int(request.form["cantModelos"])):
        codigo = request.form["codigoNew" + str(i)]
        cantSolicitada = int(request.form["cantSolicitada" + str(i)])
        maceta = Maceta(codigo,cantSolicitada) 
        listadoMacetas.append(maceta)
    return Pedido(listadoMacetas,"")
     

if(__name__ == "__main__"):
    app.run(debug=True, port=4000) 
