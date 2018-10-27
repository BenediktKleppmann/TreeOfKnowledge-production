cd "C:\Users\owner\Documents\1 projects\2015-01-01 !! Tree of Knowledge\webservice"
venv\Scripts\activate
python manage.py runserver

REM deploy to heroku
REM cd <my git repository>
REM heroku create
REM heroku login
REM git remote -v

REM (optional) make sure that it will be pushed to the right heroku-repository (here we want it to be pushed to "thawing-inlet-61413")
REM heroku git:remote -a thawing-inlet-61413
git push heroku master
REM

REM setting up new webserver:
pip install -r requirements.txt

d281a794-83ac-4173-88a2-6ee7165dc25b