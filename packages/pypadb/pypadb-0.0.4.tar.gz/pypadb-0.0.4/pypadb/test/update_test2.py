from typing import Optional

from pydantic import BaseModel

from conf.db_configurer import db_configurer
from decorator.delete import delete
from decorator.insert import insert
from decorator.update import update


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


@update('update test')
def ins_test():
    pass


@delete('delete from test where id=%(id)s')
def del_test(id: int):
    pass


if __name__ == '__main__':
    db_configurer \
        .set_host('localhost') \
        .set_user('root') \
        .set_password('123456') \
        .set_database('test') \
        .end()
    del_test(5)
