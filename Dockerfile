FROM python:3.11

WORKDIR /unipoll-api

COPY ./requirements.txt /unipoll-api/requirements.txt

RUN pip install --no-cache-dir -r /unipoll-api/requirements.txt

COPY ./src/ /unipoll-api/

CMD ["uvicorn", "unipoll_api.app:app", "--host", "0.0.0.0", "--port", "8000"]