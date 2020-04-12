from mongoConnection import mongo

def getPedidosEntregados():
    pedidosDb = mongo.db
    print(pedidosDb)
    pedidos = pedidosDb['pedidos']
    listPedidos = list(pedidos.find({}))
    print(listPedidos)
    return listPedidos