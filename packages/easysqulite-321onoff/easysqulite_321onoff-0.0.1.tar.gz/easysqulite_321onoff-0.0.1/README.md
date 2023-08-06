# Easy Squlite
A easy version of squlite for begginers
# Documentation
* = Requred Arguments
# Key
# !! Don't type the "*" !!
e.g. connect(databasename) *
format : command(args) 
## Required Perameters:
connect(databasename) *
## Commands:
maketable(tablename,columns) *
Creats a table in the database
TABLENAME is the name of the table and COLUMS is the type eg: number INTEGER

inserttable(tablename,columns,values) *
Used to insert data in the database

deleteinput(tablename,columns,values) *
Delete stuff from tables

deletetable(tablename) *
Delete Entire Tables

checkiftableexists(tablename) *
Check if a spesific table exists
TIP: This command returns True/False

checkifvalueexists(tablename,columns,values)
Checks if a value exists in a table 
TIP: This command returns true/false

gettable(tablename)
Returns the value(s) and columns of a entire table

getcolumn(tablename,columns)
Returns the value(s) of a column

cleardatabase(databasename)
Deletes a entire database

getdatabase(databasename)
Get all the stuff in a database
