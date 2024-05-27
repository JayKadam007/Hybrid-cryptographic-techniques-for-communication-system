FROM python:3-alpine3.15
ENV FLASK_RUN_HOST=0.0.0.0
WORKDIR /BE_Project
COPY . /BE_Project
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3000
CMD python3 ./app.py