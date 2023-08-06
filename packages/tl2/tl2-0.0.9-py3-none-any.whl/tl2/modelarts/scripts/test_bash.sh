

gpu=$1
#echo `pwd`
export PYTHONPATH=./:./tl2_lib
#which python
export MKL_THREADING_LAYER=
python -c "from tl2.modelarts.scripts import test_bash; \
  test_bash.TestingUnit().test_resnet(gpu='$gpu')"
#python -m tl2.modelarts.scripts.test_bash $gpu





