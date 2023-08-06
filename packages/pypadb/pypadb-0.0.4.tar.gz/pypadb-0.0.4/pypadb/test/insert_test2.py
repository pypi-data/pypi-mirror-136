import re
from typing import Optional

from pydantic import BaseModel

from conf.db_configurer import db_configurer
from decorator.insert import insert


class User(BaseModel):
    id: Optional[int]
    account: str
    stuffs: list = []


class Stuff(BaseModel):
    user_id: int
    name: str
    count: int


class Test(BaseModel):
    id: Optional[int]
    content: str


@insert('insert into test(content)')
def ins_test(wow):
    pass


if __name__ == '__main__':
    db_configurer \
        .set_host('localhost') \
        .set_user('root') \
        .set_password('123456') \
        .set_database('test') \
        .end()
    print(ins_test([Test(content='wow'), Test(content='123456')]))
    a = re.findall(r'[(](.*?)[)]', 's987f(123456))123')
    print(a)
