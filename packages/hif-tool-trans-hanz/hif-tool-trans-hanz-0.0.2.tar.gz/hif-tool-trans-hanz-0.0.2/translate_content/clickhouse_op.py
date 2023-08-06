import datetime
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import numpy as np



#本地
conf = {
    "user": "default",
    "password": "",
    "server_host": "123.56.158.232",
    "port": "8123",
    "db": "ctfx"
}
connection = 'clickhouse://{user}:{password}@{server_host}:{port}/{db}'.format(**conf)
engine = create_engine(connection, pool_size=100, pool_recycle=3600, pool_timeout=1000,
                       encoding='utf-8')  # 线程池瞎琢磨设的，不一定好
conn = engine.connect()  # 连上啦！！！

md = sqlalchemy.MetaData()

# 查询时参数用 【一天的时间】

start_date = "'" + str((datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")) + "'"
end_date = "'" + str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")) + "'"


def insert_df2database(datas, table_name):
    datas.to_sql(table_name, engine, if_exists='append', index=False)


# 从ctfx.cmp_appstore_comment拿数据
def get_data_from_cmp_forum_cmx_info():
    # 注释掉的sql为以后服务器上定时任务使用 每天扫描当日数据
    # sql = f"SELECT * FROM ctfx.cmp_facebook_info WHERE post_id in (SELECT max(post_id) from ctfx.cmp_facebook_info GROUP BY content) AND (part_date BETWEEN {start_date} AND {end_date})"
    sql = f"SELECT * from ctfx.cmp_forum_cmx_info "
    cursor = conn.execute(sql)
    datas = cursor.fetchall()
    data_list = [list(data) for data in datas]
    return data_list

if __name__ == '__main__':
    for data in get_data_from_cmp_forum_cmx_info():
        print(data)