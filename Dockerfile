FROM python:3.7-slim


RUN pip install pymongo==3.12.0
RUN pip install requests==2.25.1
RUN pip install pytz==2020.5
RUN pip install Flask==2.1.0
RUN pip list

ADD MetricHandler.py DbAccess.py RestServer.py tables.py /

ENTRYPOINT ["python3","/RestServer.py"]


#Package            Version
#------------------ ---------
#certifi            2022.9.24
#chardet            4.0.0
#click              8.1.3
#Flask              2.1.0
#idna               2.10
#importlib-metadata 5.0.0
#itsdangerous       2.1.2
#Jinja2             3.1.2
#MarkupSafe         2.1.1
#pip                22.0.4
#pymongo            3.12.0
#pytz               2020.5
#requests           2.25.1
#setuptools         57.5.0
#typing_extensions  4.4.0
#urllib3            1.26.12
#Werkzeug           2.2.2
#wheel              0.37.1
#zipp               3.9.0



