#!/bin/bash
#SBATCH --job-name={{name}}
#SBATCH --output=result.out
#

source myproj/bin/activate
srun {{command}}
