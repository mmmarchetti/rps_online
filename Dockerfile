FROM python:3.8

ENV HOME /root

WORKDIR /root

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u server.py
