FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0
ENV TERM=xterm
ENV PYTHONUNBUFFERED 1

# Install OpenSSH and set the password for root to "Docker!". In this example, "apt-get" is the install instruction for an Alpine Linux-based image.
COPY debian_sources.list /etc/apt/sources.list.d/
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopencv-dev \
    python3-opencv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt update -y && apt install -y \
    libsm6 \
    libxext6 \
    libxrender-dev


COPY sshd_config /etc/ssh/
#EXPOSE 2222 80
EXPOSE 8000
COPY ./app /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
