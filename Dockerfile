FROM python:3.10-slim-buster

WORKDIR /root

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    libdbus-1-dev \
    libdbus-glib-1-dev \
    libgirepository1.0-dev \
    gir1.2-glib-2.0 \
    && rm -rf /var/lib/apt/lists/*

COPY . /root

RUN python -m venv /root/venv

RUN /root/venv/bin/pip install --upgrade pip setuptools wheel

RUN /root/venv/bin/pip install cython

RUN /root/venv/bin/pip install PyYAML

RUN /root/venv/bin/pip install --no-cache-dir -r /root/requirements.txt

RUN echo '#!/bin/bash\ncd /root\n/root/venv/bin/python main.py' > /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

ENTRYPOINT ["/root/entrypoint.sh"]
