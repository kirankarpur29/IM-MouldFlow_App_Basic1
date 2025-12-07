FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for WeasyPrint and CadQuery/OpenCASCADE
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
# Note: Removed OpenGL dependencies (libgl1-mesa-glx, libglu1-mesa, libxmu6, libxi6)
# We no longer use CadQuery for STEP files - using lightweight text parsing instead

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
