# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Install system-level dependencies, including build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# 5. Install uv and sync dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv sync

# 6. Set the PATH for the final CMD
ENV PATH="/root/.local/bin:${PATH}"

# 7. Copy the rest of your application code into the container
COPY ./dataexploration ./dataexploration

# 8. Copy the environment file
COPY .env .

# 9. Expose the port the app runs on
EXPOSE 8000

# 10. Define the command to run your app
# 9. Expose the port the app runs on
EXPOSE 8000

# 10. Define the command to run your app using `uv run`
CMD ["uv", "run", "uvicorn", "dataexploration.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]