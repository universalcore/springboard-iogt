pip="${VENV}/bin/pip"

cd "${INSTALLDIR}/${REPO}/"

$pip install -e "${INSTALLDIR}/${REPO}/"

springboard="${VENV}/bin/springboard"

$springboard bootstrap
