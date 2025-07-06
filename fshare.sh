#!/bin/bash

# --- fshare: A robust wrapper for the fshare-cli Docker container ---
#
# This script simplifies sharing files by handling Docker commands,
# volume mounts, and path conversions automatically. It correctly
# handles multiple arguments, including those with spaces.

# --- Configuration ---
readonly IMAGE_NAME="sagnikbose/fshare:v1.0"

# --- Color Definitions (for pretty output) ---
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_NC='\033[0m' # No Color

# --- Helper Functions ---
show_help() {
    echo -e "${COLOR_BLUE}fshare - Dockerized File Sharing Utility${COLOR_NC}"
    echo "A simple wrapper to share files and directories from your current location using Docker."
    echo
    echo -e "${COLOR_YELLOW}USAGE:${COLOR_NC}"
    echo "  fshare [OPTIONS] <path1> <path2> ..."
    echo
    echo -e "${COLOR_YELLOW}IMPORTANT:${COLOR_NC}"
    echo "  - Run this command from the directory containing your files."
    echo "  - ${COLOR_RED}Enclose paths with spaces in quotes${COLOR_NC}: fshare \"My Document.docx\""
    echo
    echo -e "${COLOR_YELLOW}ARGUMENTS:${COLOR_NC}"
    echo "  <path>    One or more relative paths to files or directories to share."
    echo
    echo -e "${COLOR_YELLOW}OPTIONS:${COLOR_NC}"
    echo "  -h, --help    Show this help message and exit."
    echo
    echo -e "${COLOR_YELLOW}EXAMPLES:${COLOR_NC}"
    echo "  # Share a single file"
    echo "  fshare report.pdf"
    echo
    echo "  # Share a directory and a file with spaces in its name"
    echo "  fshare ./project_files/ \"My Final Report.docx\""
}

# --- Main Script Logic ---

# Handle --help flag or no arguments
if [[ "$1" == "-h" || "$1" == "--help" || "$#" -eq 0 ]]; then
    show_help
    exit 0
fi

# 1. Prerequisite Check: Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${COLOR_RED}Error: Docker does not seem to be running.${COLOR_NC}" >&2
    echo "Please start Docker and try again." >&2
    exit 1
fi

# 2. Prerequisite Check: Docker Image
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo -e "${COLOR_YELLOW}Docker image '${IMAGE_NAME}' not found.${COLOR_NC}"
    # Assuming Dockerfile is in the same directory as the script's location
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    if [ ! -f "${SCRIPT_DIR}/Dockerfile" ]; then
         echo -e "${COLOR_RED}Error: Cannot find Dockerfile to build the image.${NC}" >&2
         echo "Please ensure the Dockerfile is in the same directory as this script." >&2
         exit 1
    fi
    read -p "Do you want to build it now from '${SCRIPT_DIR}'? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${COLOR_GREEN}Building Docker image...${COLOR_NC}"
        docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${COLOR_RED}Error: Docker image build failed.${COLOR_NC}" >&2
            exit 1
        fi
        echo -e "${COLOR_GREEN}Image built successfully!${COLOR_NC}"
    else
        echo "Aborted. Please build the image manually." >&2
        exit 1
    fi
fi

# 3. Prepare arguments for the container
# This is the critical part for handling multiple arguments correctly.
container_paths=()
for path in "$@"; do
    # Crucial validation: check if the path exists on the host.
    # This catches errors where unquoted paths with spaces are split by the shell.
    if [ ! -e "$path" ]; then
        echo -e "${COLOR_RED}Error: Path not found: '${path}'${COLOR_NC}" >&2
        echo "Please ensure all paths are correct and relative to your current directory." >&2
        echo "Hint: If your filename contains spaces, you MUST enclose it in quotes." >&2
        exit 1
    fi
    # Prepend /data/ to each path for use inside the container
    container_paths+=("/data/$path")
done

# 4. Execute the Docker command
echo -e "${COLOR_BLUE}--- Starting fshare Session ---${COLOR_NC}"
echo -e "Host directory mounted: ${COLOR_YELLOW}$(pwd)${COLOR_NC}"
echo -e "Container mount point:  ${COLOR_YELLOW}/data${COLOR_NC}"
echo "Press CTRL+C to stop the session."
echo "---------------------------------"

# The key is "${container_paths[@]}". The quotes and the @ symbol ensure
# that each element of the array is passed as a separate, correctly-quoted
# argument to the docker run command. This preserves spaces in filenames.
docker run -it --rm \
    -v "$(pwd)":/data \
    "$IMAGE_NAME" \
    "${container_paths[@]}"

exit_code=$?

echo "---------------------------------"
if [ $exit_code -eq 0 ] || [ $exit_code -eq 130 ]; then # 130 is exit code for Ctrl+C
    echo -e "${COLOR_GREEN}fshare session ended.${COLOR_NC}"
else
    echo -e "${COLOR_RED}fshare exited with an error (code: $exit_code).${COLOR_NC}"
fi