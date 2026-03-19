FROM python:3.11
RUN mkdir myapp
COPY . /myapp
WORKDIR myapp
RUN pip install -r requirements.txt
CMD ["/bin/bash"]
