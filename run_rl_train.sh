#! /bin/bash

# usage: $ nohup bash run_rl_train.sh > outputs/output.log &

bash ~/bin/slack_notify.sh "started koikoi rl"
singularity exec --bind $HOME --nv /share/koikoi_organizers/koikoi_py3.8.17.sif \
    bash -c "source venv/bin/activate && python base_models/rl_train.py"
bash ~/bin/slack_notify.sh "<@U02BYAJ9CEM> finished koikoi rl"
