#!/bin/bash

storage_account='hvsc'
storage_key='dgvR+Z3qoY0sRYjHfOkWDMG7oSrBjLoBgVE4DhAkaRtSjORjBajJc+ddWS4z47N9RV6JWg9UO5Bh0R5Xkek9Gw=='
storage_container='hvsc'

# Download, unzip and upload the HVSC archive to an Azure Storage account.

hvsc='HVSC_68-all-of-them.zip'

# Download
if [ ! -f ${hvsc} ]
then
    wget http://www.prg.dtu.dk/HVSC/${hvsc}
fi

# Unzip
if [ ! -d C64Music ]
then
    unzip -qq ${hvsc}
    unzip -qq C64Music.zip
fi

# Upload
az storage blob upload-batch --account-name ${storage_account} \
    --account-key ${storage_key} \
    --source C64Music \
    --destination ${storage_container}

# Delete
if [ $? -eq 0 ]
then
    rm -rf C64Music C64Music.zip
fi
