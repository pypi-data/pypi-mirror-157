SCRIPT_FILE=$0

NAMEAPP="/home/dorian/sylfen/screeningBuilding/src/webpage_monitoring.py"
SCRIPT_DIR=`(cd \`dirname ${SCRIPT_FILE}\`; pwd)`

. ${SCRIPT_DIR}/start_screenBuildingJob.sh $NAMEAPP
