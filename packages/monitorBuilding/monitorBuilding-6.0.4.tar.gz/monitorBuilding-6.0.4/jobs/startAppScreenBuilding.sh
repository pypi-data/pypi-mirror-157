SCRIPT_FILE=$0

NAMEAPP="/home/dorian/sylfen/screeningBuilding/src/appScreeningBuildingDev.py"
SCRIPT_DIR=`(cd \`dirname ${SCRIPT_FILE}\`; pwd)`
# exit
. ${SCRIPT_DIR}/start_screenBuildingJob.sh $NAMEAPP
