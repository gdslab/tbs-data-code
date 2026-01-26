FROM continuumio/miniconda3

WORKDIR /app

# 1. 환경 설정 파일 복사
COPY environment.yml .

# 2. conda-forge에서 mamba 설치 후 환경 구축 (훨씬 빠르고 정확함)
RUN conda install -n base -c conda-forge mamba -y && \
    mamba env create -f environment.yml && \
    conda clean -afy

# 3. 쉘 설정
SHELL ["conda", "run", "-n", "tbs_paper", "/bin/bash", "-c"]

COPY . .

# 4. 실행 (환경 이름 'tbs_paper' 확인)
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "tbs_paper", "python", "main.py"]
