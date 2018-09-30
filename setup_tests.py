import sys
import subprocess
import psycopg2
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'task.settings'
django.setup()
from core.models import Form, Offer, Proposal
from utils import User


def delete_db():
    conn_string = "host='localhost' " \
                  "dbname='task_db' user='task_user' password='1'"
    try:
        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(0)
    except:
        print("Unable to connect to the database.")

    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT table_schema,table_name"
            " FROM information_schema.tables"
            " WHERE table_schema = 'public'"
            " ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print(f"dropping table: {row[1]}")
            cur.execute(f"drop table {row[1]} cascade")
        cur.close()
        conn.close()
    except:
        print(f"Error {sys.exc_info()[1]}")


if __name__ == '__main__':
    print('deleting migrations')
    subprocess.Popen(["find", ".", "-path", "*/migrations/*.py", "-not",
                      "-name", "__init__.py", "-delete"]).wait()
    subprocess.Popen(
        ["find", ".", "-path", "*/migrations/*.pyc", "-delete"]).wait()
    print('deleted migrations')
    delete_db()
    subprocess.Popen(['python', 'manage.py', 'makemigrations']).wait()
    subprocess.Popen(['python', 'manage.py', 'migrate']).wait()

    for i in range(3):
        user = User.objects.create(username=f"p{i + 1}", role='partner')
        user.set_password("123qwe123")
        user.save()
    for i in range(3):
        user = User.objects.create(username=f"c{i + 1}", role='creditor')
        user.set_password("123qwe123")
        user.save()
    form_data = {
        'user_id': 1,
        'name': 'n1',
        'surname': 's1',
        'patronymic': 'p1',
        'phone_number': '9994958508',
        'passport_number': '123',
        'rating': 1
    }
    offer_data = {
        'user_id': 4,
        'description': 'd1',
        'min_rating': 1,
        'max_rating': 5,
    }
    Form.objects.create(**form_data)

    form_data['rating'] = 9
    Form.objects.create(**form_data)

    form_data['rating'] = 3
    Form.objects.create(**form_data)

    Offer.objects.create(**offer_data)

    offer_data['user_id'] = 5
    offer_data['min_rating'] = 4
    offer_data['max_rating'] = 6
    Offer.objects.create(**offer_data)

    offer_data['user_id'] = 4
    offer_data['min_rating'] = 8
    offer_data['max_rating'] = 10
    Offer.objects.create(**offer_data)

    print("Finished")
