FROM python:3.9-slim

# Install dependencies for Chromium and Puppeteer
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    libgconf-2-4 \
    libnss3 \
    libx11-xcb1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libnspr4 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    ca-certificates \
    chromium \
    --no-install-recommends && \
    apt-get clean

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Set the working directory
WORKDIR /home/appuser/app

# Create the session-data directory and set permissions
RUN mkdir -p /home/appuser/app/session-data && \
    chown -R appuser:appuser /home/appuser/app

# Copy the wait-for-db.sh script and set permissions
COPY wait-for-db.sh /home/appuser/app/
RUN chmod +x /home/appuser/app/wait-for-db.sh

# Switch to the appuser
USER appuser

# Set Puppeteer environment variables
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install Python dependencies
COPY requirements.txt /home/appuser/app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package.json /home/appuser/app/
RUN npm install

# Copy the rest of the application
COPY . /home/appuser/app/

COPY insert_now.py /home/appuser/app/

# Ensure alembic is in the PATH
ENV PATH="/home/appuser/.local/bin:$PATH"

# Expose ports for Flask and Node.js
EXPOSE 5000
EXPOSE 3000

# Start the application
CMD ["/home/appuser/app/wait-for-db.sh", "sh", "-c", "alembic -c migrations/alembic.ini upgrade head && node /home/appuser/app/whatsapp-web.js & python /home/appuser/app/run.py"]