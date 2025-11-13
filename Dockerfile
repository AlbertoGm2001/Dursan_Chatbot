FROM public.ecr.aws/lambda/python:3.11

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN yum -y update && \
    yum install -y \
     curl \
      gnupg2 \
      unixODBC \
      unixODBC-devel \
      gcc-c++ \
      make \
      tar \
      gzip \

      libpq-devel \
        postgresql17 \
        postgresql17-devel \
        make \
        && yum clean all




COPY requirements.txt .

RUN pip install --upgrade pip wheel setuptools
RUN pip install --only-binary=:all: numpy pandas pyarrow dask bokeh

RUN pip install -r requirements.txt





COPY scrap/ scrap/
COPY frontend/ frontend/
COPY lambda_scrap.py .

CMD ["lambda_scrap.handler"]