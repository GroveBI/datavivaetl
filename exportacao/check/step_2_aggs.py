# -*- coding: utf-8 -*-
"""
    Check all data in SECEX tables
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    How to run: python -m exportacao.step_2_aggs
    
    If need to run just a specific check, run: python -m exportacao.step_2_aggs -m BRAID
    
    
    Running one by one:
    python -m exportacao.check.step_2_aggs -m all > allstep2exp.log
    python -m exportacao.check.step_2_aggs -m BRAID > BRAID.log
    python -m exportacao.check.step_2_aggs -m HSID > HSID.log
    python -m exportacao.check.step_2_aggs -m WLDID > WLDID.log
    
    YBPW - Is the only table that is not in this check script. We need to find a viable way to do this check in this hude table
    
"""


''' Import statements '''
import csv, sys, os, argparse, MySQLdb, time, bz2,click
from collections import defaultdict
from os import environ
from decimal import Decimal, ROUND_HALF_UP
from config import DATA_DIR,DATAVIVA_DB_USER,DATAVIVA_DB_PW,DATAVIVA_DB_NAME
from helpers import d, get_file, format_runtime,errorMessage,runCountQuery
import unittest

''' Connect to DB '''
db = MySQLdb.connect(host="localhost", user=DATAVIVA_DB_USER, passwd=DATAVIVA_DB_PW, db=DATAVIVA_DB_NAME)
db.autocommit(1)
cursor = db.cursor()



class ExportAggs(unittest.TestCase):

    '''
    BRA_ID

    * excluding on air products (bra_id xx)
    * length with size 2 cant be compered with others.. values from state exports are different than municipality
    ** this can be used only to compare imports
    * To compare 7 with 2,8 necessary to use table attrs_bra_pr
    '''    
    def test_BRA_ID(self):
    
        print "Entering in checkBRA_ID"
        total=0
        
        # YMB: Check aggs 2 with 4 (2,7,8)
        sql="SELECT * FROM secex_ymb as b where left(bra_id,2)<>'xx' and b.bra_id_len=2 and \
        b.import_val  <> \
            (SELECT sum(import_val) FROM secex_ymb \
            where bra_id_len=8 and left(bra_id,2)=b.bra_id and month=b.month  and year=b.year \
            group by left(bra_id,2))"  
        total+=runCountQuery('checkBRA_ID', 'secex_ymb', sql,cursor,count=True)   
    
    
        
        #YMBP - bra_id 2 x 4
        sql="SELECT * FROM secex_ymbp as b \
            where left(bra_id,2)<>'xx' and b.bra_id_len=2 and \
            b.import_val  <> \
                (SELECT sum(import_val)  FROM secex_ymbp  \
                        where bra_id_len=8 and left(bra_id,2)=b.bra_id \
                        and hs_id=b.hs_id and year=b.year and month=b.month \
                        group by left(bra_id,2),hs_id_len,year)"
        total+=runCountQuery('checkBRA_ID', 'secex_ymbp', sql,cursor,count=True) 
    
        #YMBW
        sql="SELECT * FROM secex_ymbw as b \
            where left(bra_id,2)<>'xx' and b.bra_id_len=2 and \
            b.import_val  <> \
                (SELECT sum(import_val)  FROM secex_ymbw  \
                        where bra_id_len=8 and left(bra_id,2)=b.bra_id \
                        and wld_id=b.wld_id and year=b.year and month=b.month \
                        group by left(bra_id,2),wld_id_len,year)    "
        total+=runCountQuery('checkBRA_ID', 'secex_ymbw', sql,cursor,count=True) 
        
        self.assertEqual(total, 0)
                    
    '''
        BRA_ID x Planning Regions
    '''
    def test_BRA_IDPR(self):    
        total=0
        
        #YB 
        sql="SELECT count(*) FROM secex_ymb as b where left(bra_id,2)<>'xx' and b.bra_id_len=7 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
            (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymb s, attrs_bra_pr p \
            where p.bra_id = s.bra_id and p.pr_id = b.bra_id and s.bra_id_len=8 and \
                left(s.bra_id,4)=b.bra_id  and s.year=b.year and s.month=b.month group by left(s.bra_id,4))"
        total+=runCountQuery('checkBRA_IDPR', 'secex_ymb', sql,cursor,count=True) 
    
            
        #YBP - bra_id 2 x 4
        sql="SELECT count(*) FROM secex_ymbp as b \
            where left(bra_id,2)<>'xx' and b.bra_id_len=4 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                (SELECT concat(CAST(s.import_val AS CHAR),CAST(s.export_val AS CHAR )) FROM secex_ymbp s, attrs_bra_pr p   \
                        where p.bra_id = s.bra_id and  p.pr_id = b.bra_id and s.bra_id_len=8 and left(s.bra_id,4)=b.bra_id \
                        and s.hs_id=b.hs_id and s.year=b.year and s.month=b.month \
                        group by left(s.bra_id,4),s.hs_id_len,year)"
        total+=runCountQuery('checkBRA_IDPR', 'secex_ymbp', sql,cursor,count=True) 
        
    
        #YBW
        sql="SELECT count(*) FROM secex_ymbw as b \
            where left(bra_id,2)<>'xx' and b.bra_id_len=4 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                (SELECT concat(CAST(s.import_val AS CHAR),CAST(s.export_val AS CHAR )) FROM secex_ymbw s, attrs_bra_pr p   \
                        where p.bra_id = s.bra_id and p.pr_id = b.bra_id and s.bra_id_len=8 and left(s.bra_id,4)=b.bra_id \
                        and s.wld_id=b.wld_id and s.year=b.year and s.month=b.month \
                        group by left(s.bra_id,4),s.wld_id_len,s.year)    "
        
        self.assertEqual(total, 0)
    
        #YBPW ??
    
    def test_HS_ID(self):
        print "Entering in checkHS_ID"
        total=0
        
        aggsP = [(2, 6)]#2,6  [(2, 4),(4, 6)]
        for aggs in aggsP:    
            
            # YP: Check HS aggs 2 with 4
            sql="SELECT count(*) FROM secex_ymp as b where b.hs_id_len="+str(aggs[0])+" and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                   (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymp \
                where hs_id_len="+str(aggs[1])+" and left(hs_id,"+str(aggs[0])+")=b.hs_id and month=b.month  and year=b.year \
                group by left(hs_id,"+str(aggs[0])+"))" 
            total+=runCountQuery('checkHS_ID', 'secex_ymp:'+str(aggs[0])+":"+str(aggs[1]), sql,cursor,count=True) 
                
            
            # YBP: Check HS aggs 2 with 4
            sql="SELECT count(*) FROM secex_ymbp as b where b.hs_id_len="+str(aggs[0])+" and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                   (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymbp \
                where hs_id_len="+str(aggs[1])+" and left(hs_id,"+str(aggs[0])+")=b.hs_id and bra_id=b.bra_id and month=b.month and year=b.year \
                group by left(hs_id,"+str(aggs[0])+"),bra_id_len,year)"   
            total+=runCountQuery('checkHS_ID', 'secex_ymbp:'+str(aggs[0])+":"+str(aggs[1]), sql,cursor,count=True) 
                        
    
            # YPW: Check HS aggs 2 with 4
            sql="SELECT count(*) FROM secex_ympw as b where b.hs_id_len="+str(aggs[0])+" and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                   (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ympw \
                where hs_id_len="+str(aggs[1])+" and left(hs_id,"+str(aggs[0])+")=b.hs_id and wld_id=b.wld_id and month=b.month  and year=b.year \
                group by left(hs_id,"+str(aggs[0])+"),wld_id_len,year)"  
            
            total+=runCountQuery('checkHS_ID', 'secex_ympw:'+str(aggs[0])+":"+str(aggs[1]), sql,cursor,count=True) 
    
            # YBPW: Check HS aggs 2 with 4
            sql="SELECT count(*) FROM secex_ymbpw as b where b.hs_id_len="+str(aggs[0])+" and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
                   (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymbpw \
                where hs_id_len="+str(aggs[1])+" and left(hs_id,"+str(aggs[0])+")=b.hs_id and bra_id=b.bra_id and wld_id=b.wld_id and month=b.month  and year=b.year \
                group by left(hs_id,"+str(aggs[0])+"),wld_id_len,bra_id_len,year)"           
            #runCountQuery('checkHS_ID', 'secex_ymbpw:'+str(aggs[0])+":"+str(aggs[1]), sql,cursor,count=True) 
            
        self.assertEqual(total, 0)
        
    
    def test_WLD_ID(self):
        
        print "Entering in checkWLD_ID"
        total=0
        # YMW: Check WLD aggs 2 with 5
        sql="SELECT count(*) FROM secex_ymw as b where b.wld_id_len=2 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
               (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymw \
            where wld_id_len=5 and left(wld_id,2)=b.wld_id and month=b.month  and year=b.year \
            group by left(wld_id,2))"    
        total+=runCountQuery('checkWLD_ID', 'secex_ymw', sql,cursor,count=True)
            
    
        # YMBW: Check WLD aggs 2 with 5
        sql="SELECT count(*) FROM secex_ymbw as b where b.wld_id_len=2 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
               (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymbw \
            where wld_id_len=5 and left(wld_id,2)=b.wld_id and bra_id=b.bra_id and month=b.month  and year=b.year \
            group by left(wld_id,2),bra_id_len,year)"   
        total+=runCountQuery('checkWLD_ID', 'secex_ymbw', sql,cursor,count=True) 
    
        # YMPW:  Check WLD aggs 2 with 5
        sql="SELECT count(*) FROM secex_ympw as b where b.wld_id_len=2 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
               (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ympw \
            where wld_id_len=5 and left(wld_id,2)=b.wld_id and hs_id=b.hs_id and month=b.month  and year=b.year \
            group by left(hs_id,2),hs_id_len,year)"   
        total+=runCountQuery('checkWLD_ID', 'secex_ympw', sql,cursor,count=True)     
                
        #YMPBW Check WLD aggs 2 with 5
        sql="SELECT count(*) FROM secex_ymbpw as b where b.wld_id_len=2 and concat(CAST(b.import_val AS CHAR),CAST(b.export_val AS CHAR )) <> \
               (SELECT concat(CAST(import_val AS CHAR),CAST(export_val AS CHAR )) FROM secex_ymbpw \
            where wld_id_len=5 and left(wld_id,2)=b.wld_id and hs_id=b.hs_id and bra_id=b.bra_id and month=b.month  and year=b.year \
            group by left(wld_id,2),bra_id_len,hs_id_len,year)"   
        #runCountQuery('checkWLD_ID', 'secex_ymbpw', sql,cursor,count=True) 
        
        self.assertEqual(total, 0)

@click.command()
@click.option('-m', '--method', prompt='Method', help='chosse a specific method to run: BRAID , HSID ,WLDID ',required=False)
def main(method):
    cExp=ExportAggs()
    if not method or method=='all':
        cExp.test_BRA_ID()
        cExp.test_HS_ID()
        cExp.test_WLD_ID()  
    elif method=="BRAID":
        cExp.test_BRA_ID()        
    elif method=="HSID":
        cExp.test_HS_ID()
    elif method=="WLDID":
        cExp.test_WLD_ID()

if __name__ == "__main__":
    start = time.time()
    
    main()
    
    total_run_time = time.time() - start
    print; print;
    print "Total runtime: " + format_runtime(total_run_time)
    print; print;