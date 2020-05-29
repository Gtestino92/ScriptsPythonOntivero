from mongoConnection import mongo
from pymongo import MongoClient
from models.pedido import Pedido
from models.maceta import Maceta
import pandas as pd
import numpy as np
import re
from matplotlib import pyplot as plt
from ml.logRegGradDesc import getProbCompraEstimation

def getListRecomOrderByProb(pedidoSolicitado):
    ontiveroDb = mongo.db
    pedidos = ontiveroDb['pedidos']
    query = {"$or": []}
    for i in range(len(pedidoSolicitado.listadoMacetas)):
        query["$or"].append({pedidoSolicitado.listadoMacetas[i].codigo : { "$exists": True }})
    listPedidos = list(pedidos.find(query))

    ## obtengo lista codigos que no están en pedidoSolicitado (buscar excel)
    dfsInfo = getDfInfo()
    dfsProbByCod = dfsInfo[["codigo nuevo"]]
    dfsProbByCod.columns = ["codigoNew"]

    for maceta in pedidoSolicitado.listadoMacetas:
        dfsProbByCod = dfsProbByCod.drop(dfsProbByCod[dfsProbByCod["codigoNew"]==maceta.codigo].index)
    dfsProbByCod = dfsProbByCod.reset_index(drop=True) ##reseteo indices luego del drop

    ## para cada uno busco la prob y armo otra columna en el df
    probsList = []
    hVals = getHMatrix(pedidoSolicitado.listadoMacetas,listPedidos)
    xVals = getXVals(pedidoSolicitado)
    for i, row in dfsProbByCod.iterrows():
        codNew = row["codigoNew"]
        yVec = getYVec(codNew,listPedidos)
        if(yVec.sum()==0):
            prob = 0
        elif(yVec.sum()==len(yVec)):
            prob = 1
        else:
            prob = getProbCompraEstimation(hVals,yVec,xVals)
        probsList.append(prob)

    dfsProbByCod['probRec'] = pd.DataFrame(probsList)

    ## ordeno el df y paso a lista los codigos
    dfsProbByCod.sort_values(by=['probRec'], inplace=True, ascending=False)
    return dfsProbByCod["codigoNew"].to_json(orient = "records")

def getHMatrix(listadoMacetas,listPedidos):
    vecPedidosMat = []
    for pedido in listPedidos:
        vecCantByModelo = []
        for maceta in listadoMacetas:
            cod = maceta.codigo
            if(cod in pedido):
                cant = pedido[cod]
            else:
                cant=0
            vecCantByModelo.append(cant)
        vecPedidosMat.append(vecCantByModelo) 
    return np.matrix(vecPedidosMat)

def getYVec(codNew,listPedidos):
    yVec = []
    for pedido in listPedidos:
        if(codNew in pedido):
            value = 1
        else:
            value=0
        yVec.append(value)
    return np.matrix(yVec).T

def getXVals(pedidoSolicitado):
    xVals = []
    for maceta in pedidoSolicitado.listadoMacetas:
        xVals.append(maceta.cantidad)
    return np.array(xVals)
    
def getDfInfo():
    ## MODIFICAR PARA QUE CONSULTE A LISTA_MACETAS
    fileInfo = open("macetasInfo.xlsx", "rb")
    return pd.read_excel(fileInfo, header=0, sheet_name='info')

def getPedidosEntregados():
    ontiveroDb = mongo.db
    dfPedidosFecha = getFechas(ontiveroDb)
    dfPedidos = getPedidos(ontiveroDb)
    formatByCod = getFormatByCod()
    dfPedidosByFormato = getPedidosByFormato(dfPedidos, dfPedidosFecha, formatByCod)

    plt.figure(figsize=(10,4))
    listFormatos = pd.DataFrame(formatByCod).T.formato.unique()
    dfPedidosByFormato.to_excel("pedidosByFormato.xlsx")

    dfPedidosByTrimestre = dfPedidosByFormato.resample('3m').sum()
    print(dfPedidosByTrimestre.index)
    print(pd.infer_freq(dfPedidosByTrimestre.index))
    for formato in listFormatos:
        plt.plot(dfPedidosByTrimestre[formato])
        
    plt.legend(listFormatos)
    plt.show()
    dfPedidosByTrimestre.to_excel('pedidosByMes.xlsx')
    return [] 

def getPedidosByFormato(dfPedidos, dfPedidosFecha, formatDict):
    dfPedidosFull = pd.merge(left=dfPedidos, right=dfPedidosFecha, how='left', left_index=True, right_index=True)
    dfPedidosFull.dropna(inplace=True)
    
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
    return dfPedidosFormato
    
def getFormatByCod():
    dfsInfo = getDfInfo()
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