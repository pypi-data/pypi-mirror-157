set -x
# bash /home/work/run_train.sh bash /home/work/user-job-dir/pi-GAN-exp/exp/dev/nerf_inr/bash/run_v16_r128_grad96.sh
# bash exp/dev/nerf_inr/bash/run_v16_r128_grad96.sh False
# v2
# "bash $PROJ_NAME/tl2_lib/tl2/modelarts/scripts/run.sh 0 run"

# Env vars e.g.
# PROJ_NAME=CIPS-exp


#start_run=${1:-True}
number=${1:-0}
command=${2:-run}
#command=${2:-run_v2}
bucket=${3:-bucket-3690}
cuda_devices=${4:-0,1,2,3,4,5,6,7}


#curdir: /home/ma-user/modelarts/user-job-dir
pwd
ls -la

proj_root=$PROJ_NAME

############ copy code
cd $proj_root
## modelarts code
python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
  -s s3://$bucket/ZhouPeng/codes/$proj_root \
  -d ../$proj_root \
  -t copytree -b ../$proj_root/code.zip
## cache code
python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
  -s s3://$bucket/ZhouPeng/codes/$proj_root \
  -d /cache/$proj_root \
  -t copytree -b /cache/$proj_root/code.zip

cd /cache/$proj_root
pwd
############ Prepare envs
#cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
#cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://$bucket/ZhouPeng/pypi/torch182_cu101_py36 -d /cache/pypi -t copytree
        for filename in /cache/pypi/*.whl; do
            pip install $filename
        done
pip install -e tl2_lib
#pip install --no-cache-dir torch==1.8.2 torchvision==0.9.2
pip install --no-cache-dir easydict fvcore tensorboard tqdm opencv-python matplotlib scikit-video plyfile mrcfile pytorch-fid
pip install --no-cache-dir streamlit ninja
#pip install -e torch_fidelity_lib

############ copy results
#resume_dir=outdir/train_ffhq_r128_partial_grad-20210920_165510_097_grad96
#python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
#  -s s3://$bucket/ZhouPeng/results/$proj_root/$resume_dir \
#  -d /cache/$proj_root/results/$resume_dir -t copytree


export CUDA_VISIBLE_DEVICES=$cuda_devices
export TIME_STR=1
export PORT=12345
export PYTHONPATH=.:tl2_lib

python tl2_lib/tl2/modelarts/scripts/run.py \
  --tl_outdir=results/Run/run \
  --tl_command=$command \
  --tl_opts=root_obs s3://$bucket/ZhouPeng/ \
  --number=$number


