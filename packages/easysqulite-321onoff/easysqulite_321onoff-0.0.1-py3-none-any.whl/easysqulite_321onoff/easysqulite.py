#easysqulite
import os
os.system('pip install sqlite3')
import sqlite3
def finish():
    conn.commit()
    conn.close()
def connect(databasename):
    global conn
    global c
    conn = sqlite3.connect(databasename.db)
    c = conn.cursor()
def maketable(tablename,columns):
    c.execute("CREATE TABLE {} ({})".format(tablename,columns))
    finish()
def inserttable(tablename,columns,values):
    c.execute("INSERT INTO {} ({}) VALUES ({})".format(tablename,columns,values))
    finish()
def deleteinput(tablename,columns,values):
    c.execute("DELETE FROM {} WHERE {} = {}".format(tablename,columns,values))
    finish()
def deletetable(tablename):
    c.execute("DROP TABLE {}".format(tablename))
    finish()
def checkiftableexists(tablename):
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(tablename))
    if c.fetchone() == None:
        return False
    else:
        return True
def checkifvalueexists(tablename,columns,values):
    c.execute("SELECT {} FROM {} WHERE {} = {}".format(columns,tablename,columns,values))
    if c.fetchone() == None:
        return False
    else:
        return True
def gettable(tablename):
    c.execute("SELECT * FROM {}".format(tablename))
    return c.fetchall()
def getcolumn(tablename,columns):
    c.execute("SELECT {} FROM {}".format(columns,tablename))
    return c.fetchall()
def cleardatabase(databasename):
    c.execute("DELETE FROM {}".format(databasename))
    finish()
def getrow(tablename,columns,values):
    c.execute("SELECT {} FROM {} WHERE {} = {}".format(columns,tablename,columns,values))
    return c.fetchone()
def getdatabase(databasename):
    c.execute("SELECT * FROM {}".format(databasename))
    return c.fetchall()

