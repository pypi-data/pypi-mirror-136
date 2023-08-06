import pymysql
from pymysql.cursors import DictCursor

if __name__ == '__main__':
    # db_configurer.DbConfigurer().end()
    # connection_pool.connection()
    database = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        database='test'
    )
    cursor = database.cursor(DictCursor)
    cursor.execute('insert into test(content) value(%s),(%s)' % ('123', '345'))
    print(database.insert_id())
    database.commit()
    a, _ = 1, 2
    print(_)
