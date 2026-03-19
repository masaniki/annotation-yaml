FROM python:3.11
CMD ["/bin/bash"]
RUN mkdir myapp
COPY . /myapp
RUN cd myapp
RUN pip install -r requirements.txt
