
def getCodigoByTituloMlibre(mysql):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT nombre_publicacion, codigo_nuevo FROM codigos_mlibre''')
    result = cur.fetchall()
    return resultSQLToDict(result)

def resultSQLToDict(sqlRes):
    #{k:v for t in a for k,v in t.items()}
    return {elem['nombre_publicacion']:elem['codigo_nuevo'] for elem in sqlRes}
   