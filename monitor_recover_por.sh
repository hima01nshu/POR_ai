#!/bin/bash

# Function to read the config file
read_config() {
    local section=$1
    local key=$2
    awk -F'=' -v section="[$section]" -v key="$key" '
        $0 ~ section {
            found_section = 1
        }
        found_section && $0 ~ key {
            gsub(/^[ \t]+|[ \t]+$/, "", $2)  # Trim leading and trailing spaces
            print $2
            exit
        }' "$CONFIG_FILE"
}

# Function to search for file in S3 recursively
search_s3_file() {
    echo "Searching for $FILENAME in S3 bucket $S3_BUCKET..."
    matches=$(aws s3 ls s3://$S3_BUCKET/ --recursive | grep "$FILENAME")

    if [ -z "$matches" ]; then
        echo "File $FILENAME not found in S3 bucket."
        exit 1
    else
        echo "File found at:"
        echo "$matches"

        # Ask user to choose the correct file if multiple matches are found
        file_list=($(echo "$matches" | awk '{print $4}'))
        if [ ${#file_list[@]} -gt 1 ]; then
            echo "Multiple files found. Please choose the file you want to recover:"
            select opt in "${file_list[@]}"; do
                if [ -n "$opt" ]; then
                    FILE_KEY=$opt
                    break
                fi
            done
        else
            FILE_KEY=$(echo $matches | awk '{print $4}')
        fi

        echo "Recovering $FILE_KEY..."
    fi
}

# Function to check if file or directory exists locally
check_file_or_directory() {
    if [ ! -e "$LOCAL_PATH" ]; then
        echo "$TYPE not found! Recovering from S3..."
        recover_file_or_directory
    else
        echo "$TYPE exists at $LOCAL_PATH."
    fi
}

# Function to recover file or directory from S3
recover_file_or_directory() {
    if [ "$IS_DIRECTORY" = "yes" ]; then
        aws s3 cp s3://$S3_BUCKET/$FILE_KEY $LOCAL_PATH --recursive
    else
        aws s3 cp s3://$S3_BUCKET/$FILE_KEY $LOCAL_PATH
    fi

    if [ $? -eq 0 ]; then
        echo "$TYPE recovered successfully."
    else
        echo "$TYPE recovery failed."
    fi
}

# Load configuration file
CONFIG_FILE="config.cfg"

# Load variables from config
S3_BUCKET=$(read_config "S3" "bucket_name")

# Ask if recovering a file or a directory
read -p "Are you recovering a file or a directory (file/dir)? " TYPE

if [ "$TYPE" = "dir" ]; then
    IS_DIRECTORY="yes"
    read -p "Enter the local directory path where it should be saved: " LOCAL_DIR
    read -p "Enter the S3 directory path (leave blank to search recursively): " S3_DIR

    if [ -z "$S3_DIR" ]; then
        echo "Please specify the S3 directory path."
        exit 1
    fi

    FILE_KEY="$S3_DIR/"
    LOCAL_PATH="$LOCAL_DIR/$(basename $S3_DIR)"
else
    IS_DIRECTORY="no"
    read -p "Enter the filename you want to recover: " FILENAME
    read -p "Enter the local path where the file should be saved: " LOCAL_DIR

    LOCAL_PATH="$LOCAL_DIR/$FILENAME"

    # Perform recursive search in S3 if the path is not known
    search_s3_file
fi

# Validate that the local directory exists
if [ ! -d "$LOCAL_DIR" ]; then
    echo "Local directory does not exist. Creating directory..."
    mkdir -p "$LOCAL_DIR"
fi

# Main script
echo "Checking $TYPE status..."
check_file_or_directory

