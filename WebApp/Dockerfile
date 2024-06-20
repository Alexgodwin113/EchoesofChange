FROM python:3.10

# Set  working directory 
WORKDIR /app

# Copy current directory 
COPY . /app

# Install packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Run Django migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000


# Run manage.py 
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
