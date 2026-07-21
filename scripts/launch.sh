#!/bin/bash
#SBATCH --job-name=listeria_pipeline
#SBATCH --mail-type=ALL
#SBATCH --mail-user=laureano.giordano@mi.unc.edu.ar
#SBATCH --partition=short
#SBATCH --cpus-per-task=64
#SBATCH --time=01:00:00
#SBATCH --output=logs/pipeline_%j.out
#SBATCH --error=logs/pipeline_%j.err


# 1. Cargar el perfil del sistema
source /home/lgiordano/miniforge3/etc/profile.d/conda.sh
conda activate snakemake

# Crear el directorio de logs si no existe
mkdir -p logs

# Ejecutar Snakemake
snakemake \
    --cores 64 \
    --resources mem_mb=256000 \
    --rerun-incomplete \
    --printshellcmds \
    --use-conda


