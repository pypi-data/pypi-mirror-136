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
ENDCOLOR="\033[0m"
LCYAN="\033[96m"
BG_BLACK="\033[0;40m"
RED="\033[31m"
GREEN="\033[32m"
BGREEN="\033[1;32m"
WHITE="\033[97m"
FWHITE="$(tput setaf 7)"
BWHITE="\033[1;97m"
RESET="$(tput sgr0)"

credentials_dir=~/medquery_credentials
downloads=~/Downloads
BASHRC_PATH=~/.bashrc
ZSHRC_PATH=~/.zshrc
FISHRC_PATH=~/.fishrc

declare -a shellArray=($BASHRC_PATH, $ZSHRC_PATH, $FISHRC_PATH)
echo -n ${BG_BLACK}
clear
echo  "${WHITE}Welcome! This is pyMedQuery authentification assister.${ENDCOLOR}"
echo  "${WHITE}Lets get you started${ENDCOLOR}"
read -p "$(echo ${LCYAN}Insert username${ENDCOLOR}: )" username
read -p "$(echo ${LCYAN}Insert password${ENDCOLOR}: )" password

echo "${BGREEN}Thank you ${username}, now lets set up your cert files${ENDCOLOR}"

if [ -d $credentials_dir ];
then
    echo "${GREEN}found ${credentials_dir}${ENDCOLOR}"
else
    while true; do
        read -p "$(echo ${LCYAN}couldnt find the default folder, would you like me to set up ${credentials_dir} for you \(y/n\)?${ENDCOLOR})" yn
            case $yn in
                [Yy*] ) mkdir $credentials_dir && echo "${GREEN}directory made!${ENDCOLOR}"; break;;
                [Nn*] ) read -p "$(echo  ${LCYAN}please specify a dir name:${ENDCOLOR})" credentials_dir && mkdir -p ~/$credentials_dir; break;
            esac
    done
fi

cert=${credentials_dir}/${username}_client.crt
key=${credentials_dir}/${username}_client.key
ca=${credentials_dir}/ca.crt

cert_dl=${downloads}/${username}_client.crt
key_dl=${downloads}/${username}_client.key
ca_dl=${downloads}/ca.crt

declare -a fileArray=($(basename $cert), $(basename $key), $(basename $ca))

if [ -f $cert -a -f $key -a -f $ca ];
then
    echo "found all the necessary cert files"
else
    if [ -f $cert_dl -a -f $key_dl -a -f $ca_dl ];
    then
        while true; do
           read -p "$(echo  ${LCYAN}Would you like me to copy over the files from /Downloads to ${credentials_dir} \(y/n\)${ENDCOLOR})" yn
           case $yn in
               [Yy] ) for val in ${fileArray[@]}; do
                   cp ~/Downloads/${val/%,/} ${credentials_dir}/${val/%,/}
               done && echo "${GREEN}Files were sucessfully moved!${ENDCOLOR}";
               break;;
               [Nn] ) "$(echo ${LCYAN}please move the files into ${credentials_dir}/ and rerun script${ENDCOLOR})"; exit;
            esac
        done
    else
        echo "${RED} Could not find all your credential cert or key files in the /Downloads folder. ${ENDCOLOR}"
        echo "${RED} Please make sure you have retrieved them.${ENDCOLOR}"
        echo "${WHITE} Restart the pymq-init when you have located your files ${ENDCOLOR}"
        exit 1
    fi
fi

# Missing minio credentials
declare -a primitiveDict=("MQUSER:${username}", "MQPWD:${password}", "PGSSLKEY:${key}", "PGSSLCERT:${cert}", "PGSSLROOTCERT:${ca}")

for shell in ${shellArray[@]}; 
do
    if [ -f ${shell/%,/} ]; then
        {
        while true; do
            read -p "$(echo ${LCYAN}Do you want me to setup the environment variables in your rc file? \(y/n\)${ENDCOLOR})" yn
            case $yn in
                [Yy*] ) for envar in ${primitiveDict[@]}; do
                    key=$(echo ${envar/%,/} | cut -d ":" -f 1)
                    value=$(echo ${envar/%,/} | cut -d ":" -f 2)
                    echo "export ${key}='${value}'" >> ${shell/%,/}
                done && echo "${GREEN}The setup is now inserted into your rc file and will automatically reload.${ENDCOLOR}"
                        echo "${BGREEN} You are all set to start using pyMedQuery! :D"; break;;
                [Nn*] ) echo "${LCYAN}please manually specify the environment variables in your rc file. See README for more details.${ENDCOLOR}";
                    break;;
            esac
        done 
        } || {
        echo "${RED} Could not find the rc file: Please make a rc file for your ${SHELL}. ${ENDCOLOR}"
        echo "${LCYAN} info: the supported rc files in the script are: bash, zsh, fish. ${ENDCOLOR}"
        exit 1
        }
    fi
done

echo "${BWHITE}Thank you for using the pyMedQuery assistant!${ENDCOLOR}"
