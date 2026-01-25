FROM python:3.11
CMD ["/bin/bash"]
RUN mkdir myapp
COPY . /myapp
