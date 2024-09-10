# Use the slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev default-mysql-client && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Set the PATH environment variable to include the directory where mysqldump is located
ENV PATH="${PATH}:/usr/bin"

# Run the application using Python directly
CMD ["python", "app.py"]
