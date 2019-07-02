FROM python:3.5-slim

WORKDIR /docker

COPY data_preprocessing /docker/data_preprocessing
COPY frontend /docker/frontend

RUN pip install requests==2.22.0
RUN pip install pandas==0.24.2

CMD ["python", "/docker/data_preprocessing/calculate_stats_for_postcodes.py"]
