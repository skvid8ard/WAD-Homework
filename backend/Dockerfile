FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt .

RUN pip install --upgrade pip

ENV CMAKE_ARGS="-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF"
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# RUN pip install llama-cpp-python --no-cache-dir --force-reinstall
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY alembic.ini .
COPY ./migrations ./migrations

COPY ./app ./app

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]