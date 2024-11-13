# Step 1: Use a lightweight Python image as a base
FROM python:3.12-slim

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Step 3: Set the working directory in the container
WORKDIR /app

# Step 4: Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the application code
COPY . .

# Step 6: Expose the port on which the app will run
EXPOSE 8080

# Step 7: Use Gunicorn as the production server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
