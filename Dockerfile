FROM python:3.10-slim

WORKDIR app/

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY src ./src
COPY templates ./templates
COPY main.py ./main.py

EXPOSE 8000

CMD ["python", "main.py"]


