HOST='sylfenGastonFibre'
# HOST='sylfenGaston'
# VENV="/home/sylfen/.venv/venv_screeningBuilding"
VENV="/home/sylfen/.venv/v4_2_dorianUtils"
APP_PATH=$1

PATH_STARTJOB="/home/dorian/sylfen/toPushGaston/startjob.sh"
. $PATH_STARTJOB $HOST $VENV $APP_PATH
