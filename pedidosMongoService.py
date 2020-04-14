from mongoConnection import mongo
import pandas as pd

def getPedidosEntregados():
    ontiveroDb = mongo.db
    pedidos = ontiveroDb['pedidos']
    pedidosInfo = ontiveroDb['pedidos_info']
    listPedidosInfo = list(pedidosInfo.find({}))
    dfPedidosInfo = pd.DataFrame(listPedidosInfo)
    pedidosFecha = dfPedidosInfo['fecha_entrega']
    pedidosFecha.dropna(inplace=True)
    print(pedidosFecha.head())
    listPedidos = list(pedidos.find({}))
    dfPedidos = pd.DataFrame(listPedidos)
    dfPedidos.drop('_id', axis=1, inplace=True)
    dfPedidos.set_index("id_pedido", inplace=True)
    dfPedidos.fillna(0, inplace=True)
    print(dfPedidos.head())
    return listPedidos