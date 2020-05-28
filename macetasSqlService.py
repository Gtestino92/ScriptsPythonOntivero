def getCodigoByTitulo(mysql):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT codigo, codigo_nuevo FROM LISTA_MACETAS''')
    result = cur.fetchall()
    return result