from mongoConnection import mongo
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def getPedidosEntregados():
    ontiveroDb = mongo.db
    dfPedidosFecha = getFechas(ontiveroDb)
    dfPedidos = getPedidos(ontiveroDb)
    dfPedidosByFormato = getPedidosByFormato(dfPedidos, dfPedidosFecha)
    plt.figure(figsize=(10,4))
    plt.plot(dfPedidosByFormato["OVA"])
    dfPedidosByFormato.to_excel("pedidosByFormato.xlsx")
    return [] 

def getPedidosByFormato(dfPedidos, dfPedidosFecha):
    dfPedidosFull = pd.merge(left=dfPedidos, right=dfPedidosFecha, how='left', left_index=True, right_index=True)
    dfPedidosFull.dropna(inplace=True)
    formatDict = getFormatDict()
    dfPedidosTransp = dfPedidosFull.T
    rowFechas = dfPedidosFull.iloc[:,-1]
    dfPedidosTransp.drop(dfPedidosTransp.tail(1).index, inplace = True)
    dfAux = pd.DataFrame(dfPedidosTransp.index.values)
    dfAux.columns = ['values']
    dfAux2 = pd.DataFrame(dfAux["values"].apply(lambda x: formatDict[x]))
    dfAux2 = dfAux2.set_index(dfPedidosTransp.index)
    dfPedidosTransp["formato"] = dfAux2
    dfPedidosTransp["fecha"] = pd.DataFrame(rowFechas)
    dfPedidosTransp.to_excel("transp.xlsx")
    dfPedidosFormato = dfPedidosTransp.groupby('formato').sum().T
    dfFechas = pd.DataFrame(rowFechas)
    dfFechas.columns = ['fecha']
    dfPedidosFormato["fecha"] = pd.to_datetime(dfFechas['fecha'], format="%d/%m/%Y")
    dfPedidosFormato.to_excel("beforeGroupFecha.xlsx")
    dfPedidosFormato = dfPedidosFormato.groupby('fecha').sum()
    dfPedidosFormato.dropna(inplace=True)
    print(dfPedidosFormato)
    return dfPedidosFormato
    
def getFormatDict():
    fileInfo = open("macetasInfo.xlsx", "rb")
    dfsInfo = pd.read_excel(fileInfo, header=0, sheet_name='info')
    dfsInfo = dfsInfo[["codigo nuevo","formato"]]
    dfsInfo.set_index("codigo nuevo", inplace = True) 
    return dfsInfo.T.to_dict('series')

def getFechas(db):
    pedidosInfo = db['pedidos_info']
    listPedidosInfo = list(pedidosInfo.find({}))
    dfPedidosInfo = pd.DataFrame(listPedidosInfo)
    dfPedidosFecha = dfPedidosInfo[['fecha_entrega','id_pedido']]
    dfPedidosFecha = dfPedidosFecha.dropna()
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