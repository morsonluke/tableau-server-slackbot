#! /bin/bash

export REPORTING_USER="reporting"
export ADMIN_PASSWORD="reporting"
export INSTALL_FILE="/etc/tableau_installed"
export TAB_DIR="/tmp/tableau-installation"
export tableau_installer=""
if test -f "${INSTALL_FILE}"; then
  echo "Tableau was already installed on this server"
  exit 0
fi
yum -y update
yum -y install wget
setenforce 0
adduser reporting
echo reporting:reporting | chpasswd
usermod -G wheel reporting
echo "reporting  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
echo "Create Tableau installation directory"
sudo -u ${REPORTING_USER} mkdir -p ${TAB_DIR}
cd ${TAB_DIR}
echo "Download packages"
wget -P /tmp/tableau-installation https://downloads.tableau.com/esdalt/2020.2.3/tableau-server-2020-2-3.x86_64.rpm
wget -P /tmp/tableau-installation https://github.com/tableau/server-install-script-samples/raw/master/linux/automated-installer/packages/tableau-server-automated-installer-2019-1.noarch.rpm
echo "Install automated installer packages"
sudo yum -y install ./tableau-server-automated-installer-2019-1.noarch.rpm
echo "Set the hostname as static"
sudo  hostnamectl set-hostname $(hostname)
echo "Create secrets file"
cat <<EOT > secrets
tsm_admin_user="${REPORTING_USER}"
tsm_admin_pass="${ADMIN_PASSWORD}"
tableau_server_admin_user="${REPORTING_USER}"
tableau_server_admin_pass="${ADMIN_PASSWORD}"
EOT
sudo -u ${REPORTING_USER} gsutil cp -p gs://tableau_config_store/* .
tableau_installer=`ls | grep tableau-server | head -n 1`
echo "Running automated installer for tableau-server"
sudo -u ${REPORTING_USER} sudo /opt/tableau/tableau_server_automated_installer/automated-installer.20191.19.0321.1733/automated-installer -s ${TAB_DIR}/secrets -f ${TAB_DIR}/config.json -r ${TAB_DIR}/reg_templ.json --accepteula ${TAB_DIR}/${tableau_installer}
export TSM_PATH="/opt/tableau/tableau_server/packages/customer-bin.20202.20.0626.1424/tsm"
${TSM_PATH} login --username ${REPORTING_USER} --password ${ADMIN_PASSWORD}
touch ${INSTALL_FILE}