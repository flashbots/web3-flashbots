#!/bin/bash

# make sure this is running in a poetry shell
if [ -z "$VIRTUAL_ENV" ]; then
    echo "This script should be run from a poetry shell. Run 'poetry shell' and try again."
    echo "
Alternatively, if you don't want to use poetry and know that you have python and dependencies configured correctly,
set VIRTUAL_ENV in your shell to override this check."
    exit 1
fi

# ensure twine and wheel are installed
echo "Checking build requirements..."
pip install twine wheel 1>/dev/null

# build the package
python setup.py sdist bdist_wheel
if [ $? -ne 0 ]; then
    echo "Failed to build package"
    exit 1
fi
echo "*********************************************************************"
echo "Build successful."

# pick last two files in dist/ in case there are previous builds present
files=(dist/*)
files=("${files[@]: -2}")
echo "Prepared files for upload:"
for file in "${files[@]}"; do
    echo -e "  - $file"
done

# parse the version number from the first element of files
libname="flashbots"
version=$(echo "$files" | grep -oP "$libname-\d+\.\d+\.\d+")
version=${version#"$libname-"}

# draw some lines to alert the user to their one last chance to exit
for i in $(seq 1 69); do
    printf '*'
    sleep 0.013
done; echo

echo "This is the point of no return."
echo -e "  package:\t$libname"
echo -e "  version:\t$version"
echo "Press Enter to upload the package to PyPI."
read -rs dummy

# upload the package
twine upload "${files[@]}"
