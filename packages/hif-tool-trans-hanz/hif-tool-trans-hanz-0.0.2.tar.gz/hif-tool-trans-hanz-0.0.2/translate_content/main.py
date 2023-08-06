import datetime
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

from utils.trans_utils import TraditionalToSimplified


pd.set_option('display.max_columns', None)#显示全部列
# pd.set_option('display.max_rows', None)#显示全部行
pd.set_option('max_colwidth',100)#设置每一行最大显示长度为100，默认为50

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





def main():
    # 从ctfx.cmp_appstore_comment拿数据
    sql = f"SELECT url,title,content,user_name,user_id,publish_time,tags,source,website,relation_site ,remark from ctfx.cmp_forum_cmx_info "
    cursor = conn.execute(sql)
    datas = cursor.fetchall()
    data_list = [list(data) for data in datas]
    for data in data_list:
        data.insert(3,TraditionalToSimplified(data[2]))
    pd_datas = pd.DataFrame(data = data_list,columns=['url','title','content', 'trans_content','user_name' ,'user_id' ,'publish_time' ,'tags' ,'source' ,'website' ,'relation_site' ,'remark' ])

    insert_df2database(pd_datas,table_name='translate_cmp_forum_cmx_info')
if __name__ == '__main__':

    main()
