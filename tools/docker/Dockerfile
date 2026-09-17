# Dev image for the sldb/kgdb/pron worktrees: the dependencies live in the image, the three
# packages are installed editable from the mounted worktrees when a container starts, so
# what a suite imports is the branch under work and never the host's shared checkouts.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git make && rm -rf /var/lib/apt/lists/*
ARG UID=1000
RUN useradd -m -u ${UID} dev && mkdir /venv && chown dev /venv
USER dev
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install --no-cache-dir "setuptools>=68" wheel \
    "pydantic>=2" "markdown-it-py>=3.0" "mdit-py-plugins>=0.4" "linkify-it-py>=2.0" "jinja2>=3.1" \
    "PyYAML>=6" "click>=8.1" "networkx>=3.0" \
    jsonschema pytest==8.3.4 pytest-cov syrupy==6.1.1 ruff==0.14.0 mypy==1.14.1 types-PyYAML build
RUN git config --global --add safe.directory '*'
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
