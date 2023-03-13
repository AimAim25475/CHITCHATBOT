FROM deepset/haystack-gpu:latest

RUN apt-get update
ADD requirements.txt requirements.txt
RUN pip3 install --upgrade pip
# RUN pip install farm-haystack[all]
RUN pip3 install -r requirements.txt
COPY . /usr/src/app/

WORKDIR /usr/src/app/
CMD ["python3", "bot_api.py"]