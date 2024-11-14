figlet -f block Fshare | lolcat ; echo -e "\t\t\t\t\tversion: 1.0" | lolcat
echo -e "\033[33;1muploading files..\033[0m"
sleep 2

# Define a cleanup function to stop both commands and print "Process completed"
cleanup() {
    echo -e "\033[33;1mStopping background and foreground processes...\033[0m"
    kill $bg_pid 2>/dev/null  # Stop the background process
    echo -e "\033[33;1mRemoving the cached directory...\033[0m"
    cd /etc
    sudo rm -r fshare_dir 2>/dev/null
    if [ $? == 0 ];then
        echo -e "\033[32;1mSuccesfully removed cached directory!\033[0m"
    else
        echo -e "Can't remove cached directory!"
    fi
    echo -e "\033[32;1mThanks to use fshare..\033[0m"
    exit 0
}

# Function to extract filename without extension
get_filename_without_extension() {
    # Check if the user provided a filename as an argument
    if [ -z "$1" ]; then
        echo "Usage: get_filename_without_extension filename"
        return 1
    fi

    # Get the filename without extension using parameter expansion
    local filename="${1%.*}"

    # Output the result
    echo "$filename"
}

if [ -d "/etc/fshare_dir" ]; then
	echo -e "Chached directory(/etc/fshare_dir) already exists.It should be removed after file transfering! \n" | lolcat
	sudo rm -r /etc/fshare_dir
	sudo mkdir /etc/fshare_dir
	for input in "$@"; do
		echo "File name: $input" | lolcat
		filename_without_extension=$(get_filename_without_extension $input)
		sudo cp $input /etc/fshare_dir
		if [ $? == 0 ];then
			echo -e "\033[33;1mStatus:\033[33;0m \033[32;1muploaded\033[0m"
		else
			echo -e "\033[33;1mStatus:\033[33;0m \033[31;1merror oucars\033[0m"
		fi
	done

else
	echo -e "Chached directory(/etc/fshare_dir) created.It should be removed after file transfering! \n" | lolcat
	sudo mkdir /etc/fshare_dir
	for input in "$@"; do
		echo "File name: $input" | lolcat
		filename_without_extension=$(get_filename_without_extension $input)
		sudo cp $input /etc/fshare_dir
		if [ $? == 0 ];then
			echo -e "\033[33;1mStatus:\033[33;0m \033[32;1muploaded\033[0m"
		else
			echo -e "\033[33;1mStatus:\033[33;0m \033[31;1merror oucars\033[0m"
		fi
	done
fi

echo -e "\n"
cd /etc/fshare_dir

# Trap Ctrl+C (SIGINT) to execute the cleanup function
trap cleanup SIGINT

# Start the background process
python3 -m http.server 8000 &  # Replace with your background command
bg_pid=$!

# Run the foreground process
cd /etc
./cloudflared-linux-amd64 --url localhost:8000 # Replace with your foreground command

# Wait here indefinitely, so Ctrl+C can trigger the cleanup
wait

