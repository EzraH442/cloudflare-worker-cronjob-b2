FROM python:3

WORKDIR /usr/src/app

ENV env=prod

ARG bucketSourceId
ARG b2AppKey
ARG b2AppKeyId
ARG cfAccountId
ARG cfWorkerApi
ARG cfWorkerName

ENV bucketSourceId=${bucketSourceId}1
ENV b2AppKey=${b2AppKey}
ENV b2AppKeyId=${b2AppKeyId}
ENV cfAccountId=${cfAccountId}
ENV cfWorkerApi=${cfWorkerApi}
ENV cfWorkerName=${cfWorkerName}

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./b2AuthorizeCfWorker.py" ]