import pymysql
from datetime import date, time


class Db():

    def __init__(self) -> None:
        """初始資料"""
        self.host = "localhost"
        self.port = 3306
        self.user = "root"
        self.pwd = ''
        self.database = 'WalkRecord'
        self.docheck = False
        self.__first_check()
        

    def __connect(self):
        """建立連結"""
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.pwd,
            database=self.database,
        )
        cursor = conn.cursor()
        return conn,cursor
    
    def __first_check(self):
        if self.docheck == False:
            self.docheck =True
            conn,cursor = self.__connect()
            self.__create_database(cursor)
            self.__create_table(cursor)
            conn.commit()
            # 關閉
            cursor.close()
            conn.close()
        else:
            pass

    def __create_database(self,cursor):
        # 建立資料庫
        create_db_query = "CREATE DATABASE IF NOT EXISTS WalkRecord"
        cursor.execute(create_db_query)

    def __create_table(self,cursor):
        # 建立資料表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS WalkRecord (
            編號 INT AUTO_INCREMENT PRIMARY KEY,
            地區 VARCHAR(255),
            日期 DATE,
            時間 TIME,
            人數 INT
        )
        """
        cursor.execute(create_table_query)

    def create_walk_record(self,area="MA212", record_date=date(2023,12,7), record_time = time(12,0), num_people=20):
        # 建立新的行走記錄
        
        try:
            conn,cursor = self.__connect()
            insert_query = """
        INSERT INTO WalkRecord (地區, 日期, 時間, 人數)
        VALUES (%s, %s, %s, %s)
        """
            cursor.execute(insert_query, (area, record_date, record_time, num_people))
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            print('動作完成，關閉連結')
            cursor.close()
            conn.close()
    
    def search_records_by_time(self,start_time, end_time):
    # 依照時間範圍搜尋行走記錄
        conn,cursor = self.__connect()
        select_query = """
        SELECT * FROM WalkRecord
        WHERE 時間 BETWEEN %s AND %s
        """
        start_time = time(start_time)
        end_time = time(end_time)
        cursor.execute(select_query, (start_time, end_time))
        records = cursor.fetchall()
        return records
        
def test():
    ob = Db()
    print('test1 insert')
    try:
        ob.create_walk_record()
        print('ok')
    except Exception as e:
        print('no ok') ; print(e)

    print('test2 select')
    try:
        d = ob.search_records_by_time(11,13)
        print(d)
        print('ok')
    except Exception as e:
        print('no ok') ; print(e)

    