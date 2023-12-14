FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies your Python script requires (if necessary)
# For example, if your script uses requests library:
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && echo "tr_TR.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen tr_TR.UTF-8 \
    && dpkg-reconfigure -f noninteractive locales \
    && /usr/sbin/update-locale LANG=tr_TR.UTF-8 \

# Run app.py when the container launches
CMD ["python", "app.py"]
