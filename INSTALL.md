# SIGNAL TERMINAL — Installation Guide

This guide explains how to install and run **SIGNAL TERMINAL** on Windows.

---

## 1. Extract the Project

Unzip the downloaded archive.

After extracting, locate the folder that contains:

```text
requirements.txt
run.py
app/
```

If you see a nested `signal_terminal` folder first, open that folder.

### Example

**Wrong location:**

```text
C:\Users\you\Downloads>
```

**Correct location:**

```text
C:\Users\you\Downloads\SIGNAL_TERMINAL>
```

You must run the installation commands from the project folder containing `requirements.txt`, `run.py`, and the `app/` directory.

---

## 2. Easiest Installation — Windows

For the simplest setup:

1. Open the project folder.
2. Double-click:

```text
install.bat
```

3. Wait for the installation to finish.
4. Then double-click:

```text
run.bat
```

The application should start automatically.

---

## 3. Manual Installation

If you prefer using Command Prompt, open **Command Prompt** and navigate to the project directory first.

For example:

```cmd
cd C:\Users\you\Downloads\SIGNAL_TERMINAL
```

Then create a Python virtual environment:

```cmd
python -m venv .venv
```

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Install the required dependencies:

```cmd
pip install -r requirements.txt
```

Finally, start SIGNAL TERMINAL:

```cmd
python run.py
```

---

## 4. Complete Command Sequence

If you are already inside the correct project directory:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

## 5. Project Directory Check

Before running the commands, make sure your folder looks approximately like this:

```text
SIGNAL_TERMINAL/
│
├── app/
├── requirements.txt
├── run.py
├── install.bat
└── run.bat
```

If `requirements.txt` cannot be found, you are most likely in the wrong directory.

---

## Troubleshooting

### `requirements.txt` not found

Make sure Command Prompt is inside the **SIGNAL_TERMINAL** directory.

Run:

```cmd
dir
```

You should see:

```text
requirements.txt
run.py
app
```

### `python` is not recognized

Python may not be installed or may not be available in your system PATH.

Install Python and make sure the **Add Python to PATH** option is enabled during installation.

### Installation fails

Make sure you are using a supported Python version and that your internet connection is available while dependencies are being installed.

---

## Quick Start

For most Windows users:

```text
1. Extract SIGNAL_TERMINAL
2. Open the SIGNAL_TERMINAL folder
3. Double-click install.bat
4. Wait for installation
5. Double-click run.bat
```

That's it.
