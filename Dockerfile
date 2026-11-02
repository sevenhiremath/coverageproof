FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY coverageproof ./coverageproof
RUN pip install --no-cache-dir . && useradd --create-home app && mkdir /data && chown app /data
USER app
ENV COVERAGEPROOF_DB=/data/coverageproof.sqlite
# Loopback default; explicit deployment auth/isolated runner work is still needed.
CMD ["python", "-m", "uvicorn", "coverageproof.app:app", "--host", "127.0.0.1", "--port", "8000"]
