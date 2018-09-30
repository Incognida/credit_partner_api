# credit_partner_api
1. Python3.6 and PostgreSQL v10 is required
2. First of all, create database and user:
  sudo -i -u postgres
  createdb task_db
  createuser --interactive --pwprompt
  username should be 'task_user', password - '1'
  psql
  grant all privileges on database task_db to task_user;
3. virtualenv -p /usr/bin/python3.6 taskenv
4. source taskenv/bin/activate
5. pip install -r requirements
6. python clear_and_populate.py
7. celery -A task worker -l info
8. in new tab: ./manage.py runserver
