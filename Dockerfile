FROM python:3.10-slim-buster AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Health check
HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1

# Create a new stage with Git installed
FROM python:3.10-slim-buster AS final

WORKDIR /app

# Copy the application files from the previous stage
COPY --from=build /app .

# Configure Git
RUN git config --global user.email "pavan.nayakanti@irissoftware.com"
RUN git config --global user.name "Pavan Nayakanti"

# Start the application
CMD ["python", "app.py"]
