# Use an official lightweight Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first (better for caching layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Set environment variables (Optional)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Command to run the Flask app
CMD ["python", "app.py"]
