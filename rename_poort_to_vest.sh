#!/bin/zsh

# Directory containing the images (replace with your directory path)
image_directory="./shots/"

# Navigate to the directory
cd $image_directory

# Loop over files containing 'geldenaaksepoort' in their names
for file in *geldenaaksepoort*; do
    # Check if the file is a regular file
    if [[ -f $file ]]; then
        # Construct new filename by replacing 'geldenaaksepoort' with 'geldenaaksevest'
        new_name=${file//geldenaaksepoort/geldenaaksevest}

        # Rename the file
        mv "$file" "$new_name"
    fi
done

echo "Renaming completed."
