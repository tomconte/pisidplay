FROM python:2.7-onbuild

RUN apt-get update && apt-get install -y sidplay

WORKDIR /app
COPY . /app

ENV PORT 8080
EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["app.py"]
