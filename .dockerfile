FROM python:3.12.1

WORKDIR /morning-star-web-scraping

COPY ./morning-star-web-scraping

RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]