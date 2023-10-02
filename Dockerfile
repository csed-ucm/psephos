FROM python:3.11-alpine

WORKDIR /unipoll-api

COPY ./pyproject.toml /unipoll-api/pyproject.toml

COPY ./src/ /unipoll-api/src/

RUN pip install build

RUN python -m build

FROM python:3.11-alpine

WORKDIR /unipoll-api

COPY --from=0 /unipoll-api/dist/*.tar.gz .

RUN tar -xf unipoll-api-*.tar.gz --strip-components=1

RUN pip install .

ENTRYPOINT [ "unipoll-api" ]