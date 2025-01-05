# Start from Ubuntu image
FROM ubuntu:latest

# Install dependencies (Node.js, npm)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Create a directory for the app
WORKDIR /app

# Copy the entire local project directory to the container
COPY . /app

# Install npm dependencies (requires package.json in the project root)
RUN npm install

# Install nodemon globally for live reloading
RUN npm install -g nodemon

# Expose the ports
EXPOSE 8000
EXPOSE 5173

# Start the app with nodemon for live reloading
CMD ["nodemon", "/app/data/gemini_dynamo"]