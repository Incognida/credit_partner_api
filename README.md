# credit_partner_api
1. Python3.6, PostgreSQL v10, rabbitmq-server are required
2. First of all, create database and user:
 * sudo -i -u postgres
 * createdb task_db
 * createuser --interactive --pwprompt
 * username should be 'task_user', password - '1'
 * psql
 * grant all privileges on database task_db to task_user;
3. virtualenv -p /usr/bin/python3.6 taskenv
4. source taskenv/bin/activate
5. cd credit_partner_api/
6. pip install -r requirements
7. python clear_and_populate.py
8. celery -A task worker -l info
9. in new tab: ./manage.py runserver
10. Sign in at `http://localhost:8000/sign_in/`

You can checkout endpoints and examples by visiting `http://localhost:8000/docs/`


* Sign in as partner:
```json
{
    "username": "p1",
    "password": "123qwe123"
}
```
* Sign in as creditor:
```json
{
    "username": "c1",
    "password": "123qwe123"
}
```