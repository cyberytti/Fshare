
<p align="center">
  <img src="logo/fshare_logo.png" alt="Fshare Logo" width="300" height="300"/>
</p>

<h1 align="center">Fshare: Instant File Sharing</h1>

<p align="center">
  <strong>Share files and directories directly from your terminal. Instantly. Securely. For free.</strong>
  <br />
  <br />
  <a href="https://github.com/cyberytti/Fshare/issues">Report Bug</a>
  ·
  <a href="https://github.com/cyberytti/Fshare/issues">Request Feature</a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
    <img src="https://img.shields.io/badge/version-v1.0-brightgreen" alt="Version">
    <img src="https://img.shields.io/docker/pulls/sagnikbose/fshare.svg" alt="Docker Pulls">
    <img src="https://img.shields.io/badge/built%20with-Python%20%26%20Flask-red" alt="Built with Python & Flask">
</p>

---

**Fshare** is a powerful, open-source CLI tool that lets you share files and directories from your terminal to anywhere in the world with a single command. Built with Python, Flask, and [Pinggy.io](https://pinggy.io), it eliminates the need for complex setups, cloud uploads, or sign-up forms.

## ✨ See It in Action

![Fshare Demo GIF](https://user-images.githubusercontent.com/.../fshare-demo.gif) 
*(Note: This is a placeholder for a demo GIF. Creating one would be a great addition!)*

---

## 🤔 Why Fshare? Tired of Slow Uploads and Sign-up Forms?

| Feature                | <img src="logo/fshare_logo.png" width="20"> Fshare | WeTransfer     | Google Drive   |
| ---------------------- | :-------------------------------------------------: | :------------: | :------------: |
| **No Sign-Up Required**|                        ✅ Yes                       |     ❌ No      |     ❌ No      |
| **No File Size Limits**|                        ✅ Yes                       |   ❌ 2GB Max   |  ❌ 15GB Max   |
| **Absolute Privacy**   |                  ✅ Stays on your PC                  | ❌ Uploads Files | ❌ Uploads Files |
| **Transfer Speed**     |                 ⚡ **Direct P2P**                  | 🐢 Upload First | 🐢 Upload First |
| **From Your Terminal** |                        ✅ Yes                       |     ❌ No      |     ❌ No      |

---

## 🚀 Key Features

| Feature                       | Description                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| ⚡ **Instant Sharing**         | Go from file to shareable link in seconds with one command.                                             |
| 📁 **Share Anything**         | Share a single file, multiple files, or entire directories effortlessly.                                |
| 🌐 **Global Reach**           | Powered by [Pinggy.io](https://pinggy.io) tunnels, your files are accessible from anywhere, not just your local network. |
| 🗜️ **Automatic Compression**  | Multiple files or directories? Fshare automatically zips them for a single, convenient download.        |
| 🧠 **Intuitive CLI**          | A beautiful and smart command-line interface built with `Typer` and `Rich`.                             |
| 🔒 **Preserves Quality**      | Your files are transferred bit-for-bit. No compression artifacts, no downscaling.                       |


---

# Installation

## Prerequisites

Before installing Fshare, ensure you have the following installed on your system:
- Python 3.x
- Git
- pip (Python package installer)

## Manual Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cyberytti/Fshare
```

### 2. Navigate to Project Directory

```bash
cd Fshare
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Tool

After successful installation, you can run the tool using:

```bash
python3 fshare.py --help
```

## Making Fshare Globally Accessible (Optional)

To use Fshare as a global command (like `apt` or `git`) from anywhere in your terminal, follow these steps:

### 1. Install Nuitka

```bash
pip install nuitka
```

### 2. Create Executable

```bash
python -m nuitka --onefile fshare.py
```

Upon successful compilation, you'll see the message:
```
Nuitka: Successfully created 'fshare.bin'.
```

### 3. Rename the Executable

```bash
cp fshare.bin fshare
```

### 4. Move to System Executables Directory

Move the executable to your system's executable directory:

**Linux/macOS:**
```bash
sudo mv fshare /usr/bin/
```

**Windows:**
Move the `fshare.exe` file to a directory in your system's PATH, such as:
- `C:\Windows\System32\`
- Or add the current directory to your PATH environment variable

### 5. Verify Global Installation

Test the global installation by running:

```bash
fshare --help
```

You should now be able to use Fshare from any directory in your terminal.
---

## ⚙️ How It Works

1.  **🖥️ Local Server:** Fshare spins up a lightweight Flask web server on your machine to serve the selected files.
2.  **tunneling:** It uses [Pinggy.io](https://pinggy.io) to create a secure SSH tunnel, exposing your local server to the internet with a public, random URL.
3.  **🗜️ Smart Archiving:** If you share multiple files or a directory, Fshare creates a temporary `.zip` archive on the fly. This archive is cleaned up automatically when you stop the server.
4.  **🛑 Temporary by Design:** The shareable link is active **only** as long as your Fshare process is running. As soon as you press `CTRL+C`, the server and the tunnel shut down, and the link becomes inactive.

---

## 🛡️ Your Files, Your Control: Security & Privacy

-   **✅ No Third-Party Uploads:** Your files are streamed directly from your computer to the recipient. They are never stored on any intermediate server.
-   **✅ Ephemeral Links:** Links expire the moment you terminate the session. No forgotten files lingering in the cloud.
-   **✅ You Are the Host:** You have full control and visibility over the sharing process.

---

## ❓ FAQ

> **Is Fshare free?**

Absolutely! Fshare is 100% free and open-source under the MIT License.

> **Can I share large files, like video exports or disk images?**

Yes! There are **no file size limits** imposed by Fshare. Your transfer speed is only limited by your own network bandwidth.

> **How long do the shared links last?**

The links are temporary and last only until you stop the server by pressing `CTRL+C` in your terminal.

> **Does it work on Windows?**

Yes, Fshare works perfectly on Windows via the **Windows Subsystem for Linux (WSL)**.

---

## 🤝 Contributing & License

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

-   ⭐ **Star the Repo** on [GitHub](https://github.com/cyberytti/Fshare)!
-   🐞 **Report a Bug** by opening an issue.
-   💡 **Suggest a Feature** or submit a Pull Request.

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

<p align="right">(<a href="#top">back to top</a>)</p>
