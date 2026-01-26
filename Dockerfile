FROM continuumio/miniconda3

WORKDIR /app

# 1. 
COPY environment.yml .

# 2. 
RUN conda install -n base -c conda-forge mamba -y && \
    mamba env create -f environment.yml && \
    conda clean -afy

# 3. 
SHELL ["conda", "run", "-n", "tbs_paper", "/bin/bash", "-c"]

COPY . .

# 4.
CMD ["bash"]
