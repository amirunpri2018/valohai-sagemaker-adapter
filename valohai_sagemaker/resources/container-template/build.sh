#!/usr/bin/env bash

# This script shows how to build the Docker image and push it to ECR to be ready for use
# by SageMaker.

# The argument to this script is the image name. This will be used as the image on the local
# machine and combined with the account and region to form the repository name for ECR.
container_dir=$(dirname $(realpath $0))
name=$1
files=${@:2}


display_usage() {
    echo "Error: '$1': no such file or directory"
    echo "Usage: $0 <image-name> <train-script> [ <other paths to copy to model directory> ]"
    exit 1
}

extract_filenames() {
    local pair=$1
    local index=$2
    local array=()

    if [[ $pair = *":"* ]]
    then
        IFS=':' read -r -a array <<< "$pair"
    else
        local array=("$pair")
        local index=0
    fi

    echo "${array[$index]}"
}


if [ "$name" == "" ]
then
    echo bad name
    display_usage
fi

for file in $files
do
    if [ ! -e $(extract_filenames $file 0) ]
    then
        display_usage "$file"
    fi
done


for file in $files
do
    echo cp -r $(extract_filenames $file 0) ${container_dir}/model/$(extract_filenames $file 1)
done


# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)

fullname="${account}.dkr.ecr.${region}.amazonaws.com/${name}:latest"


# Get the train and serve scripts executable
chmod +x ${container_dir}/model/train
chmod +x ${container_dir}/model/serve


if [ $? -ne 0 ]
then
    exit 255
fi

# If the repository doesn't exist in ECR, create it.

aws ecr describe-repositories --repository-names "${name}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${name}" > /dev/null
fi

# Get the login command from ECR and execute it directly
$(aws ecr get-login --region ${region} --no-include-email)

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

cd ${container_dir}

docker build  -t ${name} .
ret=$?

if [ "$ret" != "0" ]
then
    echo "Docker could not build image"
    exit 255
fi

docker tag ${name} ${fullname}
ret=$?

if [ "$ret" != "0" ]
then
    echo "Docker could not tag image"
    exit 255
fi
