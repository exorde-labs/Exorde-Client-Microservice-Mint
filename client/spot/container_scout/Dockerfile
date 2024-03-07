FROM python:3.10-slim as base

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir aiohttp docker 

FROM base as with_code

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./src/* /usr/src/app
# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["python3.10", "/usr/src/app/app.py"]
