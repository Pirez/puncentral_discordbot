FROM python:3.8-slim

WORKDIR /code

EXPOSE 5001

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY / .

CMD ["gunicorn"  , "-b", "0.0.0.0:5001", "listen:app"]