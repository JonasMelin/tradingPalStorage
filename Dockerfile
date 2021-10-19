FROM python:3.7-slim

RUN pip install pymongo==3.12.0
RUN pip install requests==2.25.1
RUN pip install pytz==2020.5
RUN pip list

ADD Main.py /

ENTRYPOINT ["python3","/Main.py"]





