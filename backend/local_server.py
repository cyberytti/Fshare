from flask import Flask, send_file, abort
import os
from typing import Optional

def start_local_file_server(
    file_path: str,
    port: int = 8000,
    download_name: Optional[str] = None,
    host: str = '0.0.0.0',
    debug: bool = False
) -> None:
    """
    Start a Flask server to serve a single file with forced download.
    
    Args:
        file_path: Path to the file to serve
        port: Port to run the server on (default: 8000)
        download_name: Custom filename for download (default: original filename)
        host: Host to bind to (default: '0.0.0.0')
        debug: Run in debug mode (default: False)
    """
    app = Flask(__name__)

    # Validate file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Use basename as download name if not specified
    if download_name is None:
        download_name = os.path.basename(file_path)

    @app.route('/')
    def serve_file():
        try:
            return send_file(
                file_path,
                as_attachment=True,
                download_name=download_name
            )
        except Exception as e:
            app.logger.error(f"Error serving file: {e}")
            abort(500, description="Failed to serve file")

    # Configuration for better production defaults
    app.config.update(
        SEND_FILE_MAX_AGE_DEFAULT=0,  # Disable caching
    )

    print(f"Serving '{download_name}' at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)