from mongoConnection import mongo
import pandas as pd

def getPedidosEntregados():
    ontiveroDb = mongo.db
    dfPedidosFecha = getFechas(ontiveroDb)
    dfPedidos = getPedidos(ontiveroDb)
    dfPedidosFull = pd.merge(left=dfPedidos, right=dfPedidosFecha, how='left', left_index=True, right_index=True)
    dfPedidosFull.dropna(inplace=True)
    print(dfPedidosFull)
    return []

def getFechas(db):
    pedidosInfo = db['pedidos_info']
    listPedidosInfo = list(pedidosInfo.find({}))
    dfPedidosInfo = pd.DataFrame(listPedidosInfo)
    dfPedidosFecha = dfPedidosInfo[['fecha_entrega','id_pedido']]
    dfPedidosFecha.dropna(inplace=True)
    dfPedidosFecha.set_index("id_pedido", inplace=True)
    dfPedidosFecha.columns=['fecha']
    return dfPedidosFecha

def getPedidos(db):
    pedidos = db['pedidos']
    listPedidos = list(pedidos.find({}))
    dfPedidos = pd.DataFrame(listPedidos)
    dfPedidos.drop('_id', axis=1, inplace=True)
    dfPedidos.set_index("id_pedido", inplace=True)
    dfPedidos.fillna(0, inplace=True)
    return dfPedidos