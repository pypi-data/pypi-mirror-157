import os
import sys
import psycopg2 as pg
import pandas.io.sql as psql
import subprocess
import io
import tempfile

class YbConnector:
    """ A pytezza-esque connector to Yellowbrick. """
    def __init__(self,host,db,user,pw):
        """ """
        self.host = host
        self.db = db
        self.user = user
        self.pw = pw
        self.dry_run_mode = False
        self.connection=None
        self.connection=self.getConnection()
    
    def __del__(self):
        if self.connection:
            self.disconnect()
        return
    
    def _checkConnection(self,reconnect=False):
        """ When using psycopg2 interactively, it's not unusual for the db
            connection to become invalid due to idle timeout.  Before issuing
            a query, check the connection and optionally reconnect if needed.
        """
        try:
            self.connection.cursor().execute("select 1")
        except pg.Error as e:
            if reconnect:
                self.disconnect()
                self.connection=self.getConnection()
            else:
                raise Exception("Connection problem: %s"%e, sys.exc_info()[2])
        
    def getConnection(self):
        """ """
        try:
            return pg.connect(host=self.host,database=self.db,user=self.user,password=self.pw)
        except Exception as details:
            print("Error connecting using:",(self.host,self.db,self.user,self.pw))
            print(">>> ",details)
            sys.exit()
    
    def disconnect(self):
        """ """
        if self.connection:
            self.connection.close()
        return
    
    def query(self,query_to_run,withResults=False,withData=False,dryRun=False,dumpTo=None,dumpAppend=False,printQuery=False):
        """ Query Yellowbrick, optionally returning a dataframe of results. """
        self._checkConnection(reconnect=True)
        
        df=None
        if dumpTo:
            mode="a+" if dumpAppend else "w+"
            open(os.path.join(".",dumpTo),mode).write(query_to_run)
        
        if dryRun:
            print("This is a dry run.  Not submitting:\n")
            print(query_to_run)
            return
        
        if printQuery:
            print(query_to_run)
        
        #withResults and withData are identical; phasing out the withResults.
        #In case of a conflict, err on the side of returning data.
        withData=max(withResults,withData)
        
        #Connect and execute, with or without returning results.  If there's a problem
        #print the details, and always close the connection.
        try:
            if withData:
                df = psql.read_sql(query_to_run,self.connection)
            else:
                self.connection.cursor().execute(query_to_run)
                self.connection.commit()
        except Exception as d:
            print("There was an error while executing the SQL:")
            print(d)
            sys.exit()
        
        return df
    
    def tableExists(self,table):
        """ """
        (db,tbl)=table.split(".")
        q="""
            select count(*) as rc
            from information_schema.tables
            where upper(table_schema)=upper('{db}')
              and upper(table_name)=upper('{table}')
        """.format(db=db,table=tbl)
        d=self.query(q,withData=True)
        return d.rc[0]>0
    
    def tableRowCount(self,table):
        """ """
        q="""
            select count(*) as rc
            from {table}
        """.format(table=table)
        d=self.query(q,withData=True)
        return d.rc[0]
    
    
    
    def getDfDDL(self,src,ybTypes=None):
        """ """
        if not ybTypes:
            #If were weren't supplied types, guess them ourselves.
            ybTypes=self.getYbTypesFromDf(src)
            
        ddl = ""
        for i in range(len(src.columns)):
            #New DDL line for each element.  Trickiness to handle no-comma for last element.
            ddl+="    %s %s%s\n"%(src.columns[i],ybTypes[i],(i<len(src.columns)-1)*",")
            
        return ddl

    def dfToYb(self,src,target,distribute_on="random",clobber=False,ybTypes=None,verbose=False,ignoreLoadErrors=False):
        """ Given a pandas df, push that table to yellowbrick, optionally replace the existing table in yellowbrick.
            If ybTypes immutable is provided, use those types and to hell with the consequences.
            Otherwise, infer the types.
        """
        
        print("Loading %d rows and %d columns into %s."%(src.shape[0],src.shape[1],target))
        print("Here is a sample of the source data:\n%s\n"%src.head(5))
        
        if not ybTypes:
            #If were weren't supplied types, guess them ourselves.
            ybTypes=self.getYbTypesFromDf(src)
        
        if clobber:
            print("Dropping %s." %target)
            self.query("drop table if exists %s;"%target)
        
        maxbad="0"
        if ignoreLoadErrors:
            maxbad="-1"
        
        ddl = self.getDfDDL(src,ybTypes)
        
        dump=tempfile.mkstemp(".csv")[1]
        print("Dumping local data to %s." %dump)
        src.to_csv(dump,index=False,header=True,line_terminator="\n")
        print("Dumped %0.2fMB."%(os.path.getsize(dump)/1024/1024),verbose)
        
        self.query("""
            create table {fqtable} (
                {ddl}
            )
            ;
        """.format(fqtable=target,ddl=ddl),printQuery=True)
        
        os.environ["YBPASSWORD"]=self.pw
        cmd=r'"C:\Program Files\Yellowbrick Data\Client Tools\bin\ybload.exe" --host {pb.host} --username {pb.user} --dbname {pb.db} --max-bad-rows {maxbad} --csv-skip-header-line true --table {target} {src}'
        cmd=cmd.format(pb=self,maxbad=maxbad,target=target,src=dump)
        print("Running this now ===>",cmd)
        
        try:
            print(subprocess.call(cmd))
        except Exception as details:
            print("There was a problem running ybload.  Make sure it's installed, is on your PATH, and that Java is installed:\n{the_details}\n".format(the_details=details))
            sys.exit(1)
        
        lrows = self.tableRowCount(target)
        if len(src)==lrows:
            print("Looks good: We dumped %d rows, and then loaded %d rows." %(len(src),lrows))
        else:
            print("THERE MIGHT HAVE BEEN A PROBLEM LOADING!  Check the output.")
        
        return
    
    def getYbTypesFromDf(self,df):
        """ Try to map.  This is almost vulgar.
            Return a tuple the same size as dftypes."""
        default_yb = "varchar(255)"
        df2yb = {'int64':'bigint',
                 'int32':'bigint',
                 'float64':'float',
                 'float32':'float',
                 'object':'varchar(255)'}
        ybtypes = []
        for t in df.dtypes:
            ybtypes.append(df2yb.get(t.name,default_yb))
        return(tuple(ybtypes))



def test(timeouttest=False):
    """ """
    YB = YbConnector("ybr-06.eyc.com","dbo","wcole","Withiel1234!")
    tt = "abntstanl.cjl_test"
    if YB.tableExists(tt):
        print(tt,"already exists.  Dropping.")
        YB.query("drop table %s" %tt)
    
    YB.query("create table %s as select 1 one,current_timestamp as ts" %tt)
    print(YB.query("select * from %s"%tt,withData=True))
    
    if timeouttest:
        import time
        mins=12
        print(f"Make some tea.  This will run for {mins} minutes.")
        time.sleep(mins*60)
        print(YB.query("select current_timestamp",withData=True))
    

if __name__=="__main__":
    test()

