FROM python:3.9-slim
WORKDIR /tests

ARG USER_ID
ARG GROUP_ID

RUN groupadd -g ${GROUP_ID} tests && \
    useradd -l -u ${USER_ID} -g tests tests

RUN apt-get update && apt-get --yes upgrade

COPY ./requirements.txt /tests/requirements.txt
RUN pip install -r /tests/requirements.txt --no-cache-dir

COPY . /tests

USER tests
CMD python utils/wait_for_services.py && pytest
