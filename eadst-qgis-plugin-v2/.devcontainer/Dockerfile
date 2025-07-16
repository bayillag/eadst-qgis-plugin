FROM qgis/qgis:latest
USER root
RUN useradd -m vscode && apt-get update && apt-get install -y --no-install-recommends python3-pip git && apt-get clean && rm -rf /var/lib/apt/lists/*
USER vscode
