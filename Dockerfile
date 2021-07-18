FROM python:3.7-slim

RUN pip install pymongo
RUN pip install requests
RUN pip list

ADD Main.py /

ENTRYPOINT ["python3","/Main.py"]





