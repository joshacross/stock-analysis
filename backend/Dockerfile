FROM python:3.13-slim

WORKDIR /app

# Install uv globally
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

EXPOSE 8888

# Run through uv so the synced environment is used.
CMD ["uv", "run", "main.py"]