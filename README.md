# Python Monitoring

## Description

This Python service monitors the health a single endpoint that is specified in the script by performing a GET request and analyzing the response as per HTTP status codes (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

The service will log each request in a log file named `python-monitor.log`. 

If the request returns an HTTP 200 code for a successful request it will increment the checks (total & total successful), log the success (as an info item) and report the uptime percentage (%) and total downtime recorded in HH:MM:SS format and then waits 5 seconds and perform another request. This successful request path will also be used for HTTP 308 and any code received between HTTP 100 and HTTP 299.

If the request returned is an HTTP 500 or between HTTP 300 and HTTP 599 (excluding 308) the health check will begin the downtime reporting sequence. This sequence begins recording the downtime, incremements ONLY the total checks, logs the error code received, and attempts to send a notification email to the email specified. The script will then retry a GET request to see if the endpoint is now back up or still down.

If the endpoint is still down, it will incremment the total checks again, log the error code received, but will NOT attempt to send another notification email to avoid spamming the email account.

If the endpoint is now back up, it will incremement the checks (total & total successful), log the successful request, calculate the uptime percentage (%) and total downtime. It will also send another email notification to report the site is now back up.

## Prerequisites

In order to run this Python Monitoring Health Checker the below packages must be installed.

- Python3
- Python Requests module

To install Python3:

```bash
sudo apt-get install python3-pip
```

To install the Requests module of Python3 after Python has been installed:

```bash
pip install requests
```

## Usage

```python
# Config Variables
## site and email to send notification to
site = "https://example.com" ### set the URL for the endpoint being monitored
email = "example@example.com" ### set the email to receive a notification for when there is a problem reaching the endpoint
```

After these variables are set, `cd` into the direcotry with the Python script file and run:

```bash
python3 python-monitoring.py
```

Or, on Windows, run:

```bash
python python-monitoring.py
```

This service may also be ran as a systemd service. Please visit the Systemd Service for more information.

## Systemd Service Setup
To set up a systemd service, use the following configuration:

```bash
[Unit]
Description=Python Health Monitoring

[Service]
User=<user>
WorkingDirectory=/ # this is where the log file will be stored - replace with whatever you'd like
ExecStart=/usr/bin/python3 /home/<user>/<dir>/python-monitoring.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace the variables wrapped in `<>` with whatever you'd like and place the systemd service file in `/etc/systemd/service/python-monitoring.service`.

You can then enable and start your service.

```bash
sudo systemctl enable python-monitoring.service
sudo systemctl start python-monitoring.service
```

To restart the service:

```bash
sudo systemctl restart python-monitoring.service
```

To stop the service:

```bash
sudo systemctl stop python-monitoring.service
```

## Roadmap

- Proper storage of total checks and total successful checks in a database to preserve history
- Store check records in a database to preserve history