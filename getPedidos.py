import pandas as pd
import datetime

file = open("ventas.xlsx", "rb")
fileInfo = open("macetasInfo.xlsx", "rb")
dictMeses = {
  "enero": "01",
  "febrero": "02",
  "marzo": "03",
  "abril": "04",
  "mayo": "05",
  "junio": "06",
  "julio": "07",
  "agosto": "08",
  "septiembre": "09",
  "octubre": "10",
  "noviembre": "11",
  "diciembre": "12"
}


## Leo archivos

dfs = pd.read_excel(file, header=1, sheet_name='Ventas AR')
dfsInfo = pd.read_excel(fileInfo, header=0, sheet_name='info')

dfs = dfs[["Nombre del comprador", "Apellido del comprador", "Título de la publicación",
    "Estado", "Fecha de venta", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]


## columna de nombre

dfs['nombre'] = dfs["Nombre del comprador"] + " " + dfs["Apellido del comprador"]

dfs = dfs[["nombre", "Título de la publicación",
    "Estado", "Fecha de venta", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]


## Obtengo codigoNew de cada venta

dfs['titulo'] = dfs["Título de la publicación"].str.split("- ", n = 3, expand = True)[3]

serieAux = dfs.loc[dfs["titulo"].isnull(), "Título de la publicación"]
frame = {'Título de la publicación': serieAux } 
dfAux = pd.DataFrame(frame)

dfs.loc[dfs["titulo"].isnull(), "titulo"] = dfAux["Título de la publicación"].str.split("- ", n = 2, expand = True)[2]

serieAux2 = dfs.loc[dfs["titulo"].isnull(), "Título de la publicación"]
frame2 = {'Título de la publicación': serieAux2 } 
dfAux2 = pd.DataFrame(frame2)

dfs.loc[dfs["titulo"].isnull(), "titulo"] = dfAux2["Título de la publicación"].str.split("- ", n = 1, expand = True)[1]

modelosList = []
for i, row in dfs.iterrows():
    titulo = row["titulo"]
    dfInfoAux = dfsInfo.loc[dfsInfo["Titulo"] == titulo, "codigo nuevo"]
    value = dfInfoAux.values[0]
    modelosList.append(value)

dfs['codigoNew'] = pd.DataFrame(modelosList)


## Obtengo fechaSolicitud

dfs["fechaSolicitudAux"] = dfs["Fecha de venta"].str.split(" de ", n = 3, expand = False)

fechasSolicitudList = []
for i, value in dfs["fechaSolicitudAux"].iteritems():
    dia = value[0] if (len(value[0]) == 2) else ("0" + value[0])
    mes = dictMeses[value[1]]
    anio = value[2][:4]
    fechasSolicitudList.append(dia + "/" + mes + "/" + anio)

dfs['fechaSolicitud'] = pd.DataFrame(fechasSolicitudList)


## Tiro ventas canceladas y pendientes

dfs.drop(dfs[ dfs['Estado'] == "Venta cancelada" ].index, inplace=True)
dfs.drop(dfs[ dfs['Estado'] == "Cancelaste la venta" ].index, inplace=True)
dfs.drop(dfs[ dfs['Estado'] == "Esperando disponibilidad de stock" ].index, inplace=True)


## Obtengo fecha de Entrega

def getFechaByArribo(descripcionEstado, fechaSolicitud):
    ##Llegó el 19 de julio
    if(descripcionEstado[:5]=="Llegó"):
        diaIsSingleDigit = (descripcionEstado[10] == " ")
        dia = ("0" + descripcionEstado[9]) if diaIsSingleDigit else descripcionEstado[9:11]
        mes = dictMeses[descripcionEstado[14:] if diaIsSingleDigit else descripcionEstado[15:]]
        anio = fechaSolicitud.split("/")[2]
        return dia + "/" + mes + "/" + anio
    else:
        return getFechaPasadoUnMes(fechaSolicitud)

def getFechaPasadoUnMes(fechaSolicitud):
    fechaVec = fechaSolicitud.split("/")
    dateSolicitud = datetime.datetime(int(fechaVec[2]), int(fechaVec[1]), int(fechaVec[0]))
    dateEntrega = dateSolicitud + datetime.timedelta(days=28) 
    return dateEntrega.strftime("%d") + "/" + dateEntrega.strftime("%m") + "/" + dateEntrega.strftime("%Y")

fechasEntregaList = []
for i, row in dfs.iterrows():
    estado = row["Estado"]
    fechaEntrega = ""
    if(estado=="Entregado"):
        fechaEntrega = getFechaByArribo(row["Descripción del estado"], row["fechaSolicitud"])
    elif(estado=="Venta concretada"):
        fechaEntrega = getFechaPasadoUnMes(row["fechaSolicitud"])
        print(fechaEntrega)
    fechasEntregaList.append(fechaEntrega)

dfs['fechaEntrega'] = pd.DataFrame(fechasEntregaList)

dfs = dfs[["nombre", "codigoNew",
    "Estado", "fechaSolicitud", "fechaEntrega", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]

dfs.to_excel("fileOutput.xlsx")  

file.close()

