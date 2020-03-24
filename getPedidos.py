import pandas as pd
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

dfs = pd.read_excel(file, header=1, sheet_name='Ventas AR')
dfsInfo = pd.read_excel(fileInfo, header=0, sheet_name='info')

dfs = dfs[["Nombre del comprador", "Apellido del comprador", "Título de la publicación",
    "Estado", "Fecha de venta", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]

dfs['nombre'] = dfs["Nombre del comprador"] + " " + dfs["Apellido del comprador"]

dfs = dfs[["nombre", "Título de la publicación",
    "Estado", "Fecha de venta", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]


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

dfs["fechaEntregaAux"] = dfs["Fecha de venta"].str.split(" de ", n = 3, expand = False)

fechasEntregaList = []
for i, value in dfs["fechaEntregaAux"].iteritems():
    dia = value[0] if (len(value[0]) == 2) else ("0" + value[0])
    mes = dictMeses[value[1]]
    anio = value[2][:4]
    fechasEntregaList.append(dia + "/" + mes + "/" + anio)

dfs['fechaEntrega'] = pd.DataFrame(fechasEntregaList)

dfs.drop(dfs[ dfs['Estado'] == "Venta cancelada" ].index, inplace=True)
dfs.drop(dfs[ dfs['Estado'] == "Cancelaste la venta" ].index, inplace=True)

dfs = dfs[["nombre", "codigoNew",
    "Estado", "fechaEntrega", "Descripción del estado", 
    "Unidades", "Ingresos (ARS)"]]

dfs.to_excel("fileOutput.xlsx")  

file.close()
