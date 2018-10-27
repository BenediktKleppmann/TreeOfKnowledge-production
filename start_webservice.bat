cd "C:\Users\owner\Documents\1 projects\2015-01-01 !! Tree of Knowledge\webservice"
venv\Scripts\activate
python manage.py runserver

REM deploy to heroku
REM cd <my git repository>
REM heroku create
REM heroku login
REM git remote -v
REM heroku git:remote -a thawing-inlet-61413
git push heroku master
REM

REM setting up new webserver:
pip install -r requirements.txt