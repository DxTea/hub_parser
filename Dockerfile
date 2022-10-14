FROM python:3.10.2


WORKDIR /usr/src/hub_parser

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt


COPY . /usr/src/hub_parser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]