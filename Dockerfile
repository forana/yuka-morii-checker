FROM python:3.8
RUN pip install pipenv

COPY main.py Pipfile Pipfile.lock ./
RUN pipenv install

CMD python main.py
