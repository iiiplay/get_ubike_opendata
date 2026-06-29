# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:10:17 2026

@author: USER
"""

import pandas as pd
import sqlite3
from datetime import datetime



def get_youbike_data():
    url="https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    df=pd.read_json(url)
    df1=df[df["act"]==1][["mday","sno","sarea","sna","ar","available_rent_bikes","available_return_bikes","latitude","longitude"]]

    return df1.values.tolist()


# 建立資料表
def create_table():
    sql="""
        create table if not exists taipei(
        mday text,
        sno int,
        sarea text,
        sna text,
        ar text,
        available_rent_bikes int,
        available_return_bikes int,
        latitude float,
        longitude float,
        
        primary key(sno,mday)
        )
    """
    
    conn=sqlite3.connect("ubike.db")
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()    



def write_to_db(values):
    sql="""
    insert or ignore into taipei values(?,?,?,?,?,?,?,?,?)
    """
    
    conn=sqlite3.connect("ubike.db")
    cursor=conn.cursor()
    cursor.executemany(sql,values)    
    count=cursor.rowcount
    conn.commit()
    conn.close()
    
    return count   



def run_job():
    create_table()
    values=get_youbike_data()
    count=write_to_db(values)

    print("-------------------------------------")
    print(datetime.now())
    print(f"共寫入{count}筆資料")



# 由 GitHub Actions 排程定時觸發，每次只跑一次
run_job()

