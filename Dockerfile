FROM python:3.11

WORKDIR /unipoll-api

COPY ./requirements.txt /unipoll-api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /unipoll-api/requirements.txt

COPY ./src /unipoll-api/src

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "80"]
