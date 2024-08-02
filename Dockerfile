FROM python:3.10.14

RUN apt update && apt install -y libhdf5-dev

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --dev --deploy --system

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
