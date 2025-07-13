FROM python:3.12-slim

WORKDIR /home

COPY requirements.txt /home/src/

RUN pip install --upgrade pip
RUN pip install -r /home/src/requirements.txt

COPY src /home/src/
COPY static /home/static/
COPY media /home/media/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]