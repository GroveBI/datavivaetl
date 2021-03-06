# -*- coding: utf-8 -*-
"""
    Check all data in SECEX tables
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    How to run: python -m exportacao.step_4_sent -m all
    If need to run just a specific check, run: python -m exportacao.step_4_sent -m HS
    
    Running one by one:
    
    python -m exportacao.check.step_4_sent -m all -y all > step_4_sent.log
    python -m exportacao.check.step_4_sent -m HS -y all > HS.log
    python -m exportacao.check.step_4_sent -m Municipality -y all > Municipality.log 
    python -m exportacao.check.step_4_sent -m State -y all > State.log 
    python -m exportacao.check.step_4_sent -m WLD -y all > WLD.log     
    
    
"""


''' Import statements '''
import csv, sys, os, argparse, MySQLdb, time, bz2,click
from collections import defaultdict
from os import environ
from decimal import Decimal, ROUND_HALF_UP
from config import DATA_DIR,DATAVIVA_DB_USER,DATAVIVA_DB_PW,DATAVIVA_DB_NAME
from helpers import d, get_file, format_runtime,find_in_df,sql_to_df,read_from_csv
import pandas as pd
from pandas import DataFrame
import pandas.io.sql as psql
import unittest

''' Connect to DB '''
db = MySQLdb.connect(host="localhost", user=DATAVIVA_DB_USER, passwd=DATAVIVA_DB_PW, db=DATAVIVA_DB_NAME)
db.autocommit(1)
cursor = db.cursor()

def to_int(s):
    if s is None:
        return False
    try: 
        ret=int(s)
        return ret
    except ValueError:
        return False
    
    
    
class ExportSent(unittest.TestCase):   
        
    def test_HS(self,year):
        print "Entering in checkHS" 
    
        dfDV = sql_to_df("SELECT s.hs_id as id,sum(export_val) as val,sum(import_val) as valimport FROM secex_ymp s where s.hs_id_len=6 and s.month=0 and s.year="+str(year)+" group by 1;",db)
    
        dfSent = read_from_csv("dados\exportacao\sent\MDIC_"+str(year)+".csv",delimiter="|")
        dfGroup = dfSent.groupby(dfSent.columns[10])
    
        total=0
        for hs in dfDV['id']:
            hsid= str(hs).zfill(6)   
            hsshort=hsid[2:6]
            hsint=to_int(hsshort)
            if not hsint: #not isinstance(hs,int):
                continue
    
            valDV = dfDV[(dfDV['id']==hsid)]['val'].values[0]
            try: 
                if valDV and str(valDV)<>'nan':
                    valCSV= sum(dfGroup.get_group(hsint)[dfSent.columns[9]])
            except: 
                total=total+1
                print "Not found in CSV a value for "+str(hsint)+" / "+str(hsshort)+" (original hs "+hs+") - Exports of value  "+ str(valDV)+ " in the year "+str(year)
                continue
             
            valCSV=to_int(valCSV)        
            valDV=to_int(valDV)
            if valCSV and valDV and valDV!=valCSV:
                total=total+1
                txt= "ERROR in HS ("+str(year)+"): "+str(hsint)+" / "+str(hs)+" - Value in CSV "+ str(valCSV)+ " <> Value in DV "+str(valDV) + " - Difference: "+str(valCSV - valDV)
                print txt
            else:
                txt="OK"
                #print txt
        self.assertEqual(total, 0)
       
    def test_Municipality(self,year,size,column):
        print "Entering in checkBRA" 
    
        dfDV = sql_to_df("SELECT a.id_mdic as id,sum(export_val) as val,sum(import_val) as valimport FROM secex_ymb s,attrs_bra a where s.bra_id_len="+str(size)+" and  a.id=s.bra_id and s.month=0 and s.year="+str(year)+" group by 1;",db)
    
        dfSent = read_from_csv("dados\exportacao\sent\MDIC_"+str(year)+".csv",delimiter="|")
        dfGroup = dfSent.groupby(dfSent.columns[column])
    
        total=0
        for mdic in dfDV['id']:        
            mdicid=to_int(mdic)
            if not mdicid: #not isinstance(hs,int):
                continue
            
            valDV = dfDV[(dfDV['id']==mdicid)]['val'].values[0]
            try: 
                if valDV and str(valDV)<>'nan':
                    valCSV= dfGroup.get_group(mdicid)[dfSent.columns[9]].sum()
            except:
                total=total+1
                print "Not found in CSV a value for "+str(mdic)+" - (original bra "+str(mdic)+")  Exports of value  "+ str(valDV)+ " in the year "+str(year)
                continue
             
            valCSV=to_int(valCSV)        
            valDV=to_int(valDV)
            if valCSV and valDV and  valDV!=valCSV:
                total=total+1
                txt= "ERROR in BRA ("+str(year)+"): "+str(mdic)+" / "+str(mdicid)+" - Value in CSV "+ str(valCSV)+ " <> Value in DV "+str(valDV) + " - Difference: "+str(valCSV - valDV)
                print txt
            else:
                txt="OK"
                
        self.assertEqual(total, 0)
        
       
    def test_WLD(self,year):
        print "Entering in checkWLD" 
    
        dfDV = sql_to_df("SELECT a.id_mdic as id,sum(export_val) as val ,sum(import_val) as valimport FROM secex_ymw s,attrs_wld a where s.wld_id_len=5 and  a.id=s.wld_id and s.month=0 and s.year="+str(year)+" group by 1;",db)
    
        dfSent = read_from_csv("dados\exportacao\sent\MDIC_"+str(year)+".csv",delimiter="|")
        dfGroup = dfSent.groupby(dfSent.columns[2])
    
        total=0
        for mdic in dfDV['id']:        
            mdicid=to_int(mdic)
            if not mdicid: #not isinstance(hs,int):
                continue
            
            valDV = dfDV[(dfDV['id']==mdicid)]['val'].values[0]
            try:
                if valDV and str(valDV)<>'nan': 
                    valCSV= dfGroup.get_group(mdic)[dfSent.columns[9]].sum()
                if valCSV==False or valCSV is None:
                    print "ALOOOO"+valCSV
            except:
                total=total+1
                print "Not found in CSV a value for "+str(mdic)+" - (original wld "+str(mdic)+")  Exports of value  "+ str(valDV)+ " in the year "+str(year)
                continue
             
            valCSV=to_int(valCSV)        
            valDV=to_int(valDV)
            if valCSV and valDV and  valDV!=valCSV:
                total=total+1
                txt= "ERROR in WLD ("+str(year)+"): "+str(mdic)+" / "+str(mdicid)+" - Value in CSV "+ str(valCSV)+ " <> Value in DV "+str(valDV) + " - Difference: "+str(valCSV - valDV)
                print txt
            else:
                txt="OK"
       
        self.assertEqual(total, 0)
            
            
    
   
        
@click.command()
@click.option('-m', '--method', prompt='Method', help='chosse a specific method to run: HS , Municipality , State , WLD',required=False)
@click.option('-y', '--year', prompt='Year', help='chosse a year to run : 2000 to 2014 or all',required=False)
#@click.argument('method', type=click.Path(exists=True))
def main(method,year):
    if not year:
        year=2000
        
    elif year=='all':
        for y in (2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013):
            runMethodYear(method,y)
            
        return
    
    runMethodYear(method,year)    
        
        
       

def runMethodYear(method,year):
    cls=ExportSent()
    if not method or method=='all':
        cls.test_HS(year)
        cls.test_WLD(year)
        cls.test_Municipality(year,8,5) 
        cls.test_Municipality(year,2,3) 
    elif method=="HS":
        cls.test_HS(year)     
    elif method=="Municipality":
        cls.test_Municipality(year,8,5) 
    elif method=="State":
        cls.test_Municipality(year,2,3)
    elif method=="WLD":
        cls.test_WLD(year)  
                                                
if __name__ == "__main__":
    start = time.time()
    
    total_error=0
    msg_error=[]
    
    main()
    
    print; print;
    print "---------------------------"
    print "SUMMARY"
    print "---------------------------"
    print "Total erros found: "+str(total_error)
    print "Erros messages:"
    print     msg_error
    
    
    total_run_time = time.time() - start
    print; print;
    print "Total runtime: " + format_runtime(total_run_time)
    print; print;