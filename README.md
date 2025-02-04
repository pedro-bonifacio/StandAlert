# StandAlert 🚗

StandAlert is a Python-based web scraper that automatically monitors the StandVirtual used car marketplace. It checks for new listings that match user-defined criteria and sends email notifications when new matching cars appear.

## Features
- Scrapes StandVirtual for cars matching user criteria every 30 minutes (configurable)
- Sends email notifications when new listings are found
- Runs in headless mode on Raspberry Pi for efficient background execution
- Can be set up as a systemd service for automation

## Installation (Raspberry Pi - Headless RPi OS)

### Prerequisites
Ensure your Raspberry Pi has the following installed:
- `git`
- `chromium-chromedriver`
- `xvfb` (for headless browsing with `pyvirtualdisplay`)
- `UV` (Python package and project manager - recommended)

### Installation Steps
1. **Clone the repository**
   ```sh
   git clone https://github.com/pedro-bonifacio/StandAlert.git
   cd StandAlert
   ```
2. **Install Chromium WebDriver**
   ```sh
   sudo apt-get install chromium-chromedriver
   ```
   - Ensure that `chromedriver` is located at `/usr/bin/chromedriver`. If not, update the `executable_path` in `scrape_urls` function inside `webscraper.py`.
3. **Install Xvfb for headless operation**
   ```sh
   sudo apt install xvfb
   ```
4. **Set up virtual environment using UV**
   ```sh
   uv venv
   source .venv/bin/activate
   uv pip sync
   ```

## Running as a Systemd Service (Automated Execution)

To run StandAlert as a background service:

1. Create a systemd service file:
   ```sh
   sudo nano /etc/systemd/system/StandAlert.service
   ```
2. Add the following content:
   ```ini
   [Unit]
   Description=StandAlert
   After=network.target

   [Service]
   Type=simple
   Restart=always
   RestartSec=5
   User=yourusername
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/your/project/.venv/bin/python /path/to/your/project/main.py
   Environment="PYTHONUNBUFFERED=1"

   [Install]
   WantedBy=multi-user.target
   ```
   - Replace `/path/to/your/project` with the actual project path.
   - Replace `yourusername` with your Raspberry Pi username.
   - Ensure `ExecStart` points to the Python binary inside the virtual environment.

3. Reload systemd daemon and enable the service:
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable StandAlert.service
   sudo systemctl start StandAlert.service
   ```
4. Check logs for errors:
   ```sh
   journalctl -u StandAlert.service -f
   ```

## Setting Up Email Notifications
To receive email notifications:
1. Obtain a **GMail App Password** (if using Gmail SMTP).
2. Edit the `.env` file in the project directory with:
   ```sh
    SENDER_EMAIL=youremail@gmail.com
    RECEIVER_EMAIL=youremail@gmail.com
    SENDER_PASSWORD=gmail_app_password
   ```

## Usage
- By default, `CHECK_INTERVAL` is set to **30 minutes**, meaning StandAlert will check for new listings every 30 minutes.
- You can change this interval in `main.py`.
- Customize your filters in `cars.csv`. Ensure that **brand/model names match StandVirtual query format**:
  - Example URL: `https://www.standvirtual.com/carros/tesla/model-3`
  - **BRAND** should be `tesla`, and **MODEL** should be `model-3`.

## Contributions
Feel free to submit pull requests or open issues if you find bugs or have suggestions for improvements!

## Feedback
If you buy a car using StandAlert, send me a message! 🚗

---

Happy car hunting! 🚀

