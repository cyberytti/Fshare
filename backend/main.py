import multiprocessing
import time
import sys
from backend.local_server import start_local_file_server
from backend.local_to_wan_server import run_wan_server

def run_server(file_name):
    """
    Sets up and runs the local file server in the background and the
    WAN tunnel in the foreground. Both are terminated automatically
    when the user presses CTRL+C.
    """
    # --- Configuration for the local file server ---
    # For more flexibility, you could parse this from command-line arguments.
    server_kwargs = {
        'file_path': file_name,
        'port': 8000,
        'host': 'localhost'
    }

    # Create a Process to run the local file server in the background.
    local_server_process = multiprocessing.Process(
        target=start_local_file_server,
        kwargs=server_kwargs
    )

    try:
        # 1. Start the local file server in the background.
        local_server_process.start()
        print(f"Started local file server in the background (PID: {local_server_process.pid}).")
        
        # Give the server a moment to initialize before starting the tunnel.
        time.sleep(2)

        # 2. Run the WAN tunnel server in the foreground.
        # This function is blocking and will run until interrupted.
        print("\nStarting WAN tunnel in the foreground to expose the local server.")
        print("Press CTRL+C to shut down both servers.")
        run_wan_server()

    except KeyboardInterrupt:
        # This block is executed when the user presses CTRL+C.
        # The 'finally' block will handle the actual cleanup.
        print("\nKeyboardInterrupt received. Shutting down...")
        
    finally:
        # This block will always run on exit, ensuring a clean shutdown.
        if local_server_process.is_alive():
            print("Terminating background server process...")
            local_server_process.terminate()  # Sends SIGTERM to the process
            local_server_process.join()       # Waits for the process to finish
            print("Background server stopped.")
        
        print("Shutdown complete.")
        sys.exit(0)
