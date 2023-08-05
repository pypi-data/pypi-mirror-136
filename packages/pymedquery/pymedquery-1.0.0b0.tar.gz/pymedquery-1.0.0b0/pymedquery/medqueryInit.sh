#!/bin/bash

<<com
Prelim MedQuery CLI
~~~~~~~~~~~~~~~~~
This is a preliminery script for automatically authentification for
pyMedQuery users. 

The CLI will ask for username, password, cert file locations, move the cert files to folder in $HOME and
insert the setup in a rc file. The user will be set to work with pyMedQuery after running the script.

This is a one time thing per machine.

MedQuery CLI APP
~~~~~~~~~~~~~~~~
The idea is to write a .deb package that exposes
a CLI for -init database and export/upload. 

The init will function somewhat like this script only that it will
interact with restrictive user tables by bearer tokens and the CLI applications
permissions. 

The user will be asked to present the bearer token in the CLI where most of the steps beneath will
just run automatically as the password and username will be given and the cert files will be generated
and sent to the right folder.
com

# colors
ENDCOLOR="\e[0m"
LCYAN="\e[96m"
RED="\e[31m"
GREEN="\e[32m"
BGREEN="\e[1;32m"
WHITE="\e[97m"
BWHITE="\e[1;97m"


credentials_dir=~/medquery_credentials
BASHRC_PATH=~/.bashrc
ZSHRC_PATH=~/.zshrc
FISHRC_PATH=~/.fishrc

declare -a shellArray=($BASHRC_PATH, $ZSHRC_PATH, $FISHRC_PATH)

echo -e "${BWHITE}Welcome! This is pyMedQuery authentification assister.${ENDCOLOR}"
echo -e "${WHITE}Lets get you started${ENDCOLOR}"
read -p "$(echo -e ${LCYAN}Insert username${ENDCOLOR}: )" username
read -p "$(echo -e ${LCYAN}Insert password${ENDCOLOR}: )" password

echo -e "${BGREEN}Thank you ${username}, now lets set up your cert files${ENDCOLOR}"

if [ -d $credentials_dir ];
then
    echo -e "${GREEN}found ${credentials_dir}${ENDCOLOR}"
else
    while true; do
        read -p "$(echo -e ${LCYAN}couldnt find the default folder, would you like me to set up ${credentials_dir} for you \(y/n\)?${ENDCOLOR})" yn
            case $yn in
                [Yy*] ) mkdir $credentials_dir && echo -e "${GREEN}directory made!${ENDCOLOR}"; break;;
                [Nn*] ) read -p "$(echo -e ${LCYAN}please specify a dir name:${ENDCOLOR})" credentials_dir && mkdir -p ~/$credentials_dir; break;
            esac
    done
fi

cert=${credentials_dir}/${username}_client.crt
key=${credentials_dir}/${username}_client.key
ca=${credentials_dir}/ca.crt

declare -a fileArray=($(basename $cert), $(basename $key), $(basename $ca))

if [ -f $cert -a -f $key -a -f $ca ];
then
    echo "found all the necessary cert files"
else
   while true; do
       read -p "$(echo -e ${LCYAN}Would you like us to move the files from /Downloads to ${credentials_dir} \(y/n\)${ENDCOLOR})" yn
       case $yn in
           [Yy] ) for val in ${fileArray[@]}; do
               mv ~/Downloads/${val/%,/} ${credentials_dir}/${val/%,/}
           done && echo -e "${GREEN}Files were sucessfully moved!${ENDCOLOR}";
           break;;
           [Nn] ) "$(echo -e ${LCYAN}please move the files into ${credentials_dir}/ and rerun script${ENDCOLOR})"; exit;
        esac
    done
fi

# Missing minio credentials
declare -a primitiveDict=("MQUSER:${username}", "MQPWD:${password}", "PGSSLKEY:${key}", "PGSSLCERT:${cert}", "PGSSLROOTCERT:${ca}")

for shell in ${shellArray[@]}; 
do
    if [ -f ${shell/%,/} ]; then
        while true; do
            read -p "$(echo -e ${LCYAN}Do you want me to setup the environment variables in your rc file? \(y/n\)${ENDCOLOR})" yn
            case $yn in
                [Yy*] ) for envar in ${primitiveDict[@]}; do
                    key=$(echo ${envar/%,/} | cut -d ":" -f 1)
                    value=$(echo ${envar/%,/} | cut -d ":" -f 2)
                    echo "export ${key}='${value}'" >> ${shell/%,/}
                done && echo -e "${GREEN}The setup is now inserted into your rc file and will automatically reload.${ENDCOLOR}"; break;;
                [Nn*] ) echo "${LCYAN}please specify the environment variables in your rc file. See README for more details.${ENDCOLOR}";
                    break;;
            esac
        done
    fi
done

echo -e "${BGREEN} You are all set to start using pyMedQuery! :D"
echo -e "${BWHITE}Thank you for using the pyMedQuery assistant!${ENDCOLOR}"
