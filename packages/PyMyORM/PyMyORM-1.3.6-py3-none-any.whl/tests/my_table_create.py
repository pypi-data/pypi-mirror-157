from pymyorm.database import Database
from config import db


if __name__ == '__main__':

    fp = open('sql/t_user.sql', 'r', encoding='utf-8')
    sql = fp.read()
    fp.close()

    Database.connect(**db)
    Database.execute(sql)
