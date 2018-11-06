#!/bin/sh

image=$1
output_dir=$(realpath ${2:-$(pwd)/output})

if [ "$image" == "" ]
then
	echo bad usage
fi

mkdir -p \
      $output_dir/input/config \
      $output_dir/input/data/training \
      $output_dir/output/data \
      $output_dir/model

docker run -v $output_dir:/opt/ml -p 8080:8080 --rm ${image} serve
