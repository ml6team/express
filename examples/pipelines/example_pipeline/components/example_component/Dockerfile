FROM python:3.7-slim

# install requirements
COPY requirements.txt /
RUN python3.7 -m pip install --no-cache-dir -r requirements.txt

# Copy over src-files of the component
COPY src /src

# TODO: ADD EXTRA FILES HERE IF NEEDED!

# Set the working directory to the source folder
WORKDIR /src

ENTRYPOINT ["python", "main.py"]