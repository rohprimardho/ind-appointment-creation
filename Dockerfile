FROM alpine:3.15

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python && python3 -m ensurepip && pip3 install --no-cache --upgrade pip setuptools 
ADD . .
RUN pip install -r requirements.txt  

CMD ["python", "run.py"]`
