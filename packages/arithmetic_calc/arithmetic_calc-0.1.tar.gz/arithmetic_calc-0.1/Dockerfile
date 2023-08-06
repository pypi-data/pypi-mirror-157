FROM python:3.8
WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY Arithmetic_calculator/ .
COPY tests/ .
CMD [ "python", "./Calculator.py" ] 