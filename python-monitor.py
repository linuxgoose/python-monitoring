#!/usr/bin/env python

## Python Web Monitoring Application

import requests ## pip install requests
import time
import logging
from smtplib import SMTP, SMTPException

# Config Variables
## endpoint to monitor and the email address that will receive notifications
site = "https://example.com"
email = "example@example.com"

# email alert function
def email_alert(message, status):
    errSent = 1

    fromaddr = 'example@example.com'
    toaddrs = email
    
    SMTPMessage = "From: " + fromaddr + "\n Python Web Monitor \n" + "Subject: " + str(status) + "\n" + "After performing a GET request to " + site + "an error code '" + str(status) + "' was received with a reason of: " + message
    
    statusType = isinstance(status, str)

    # set the logMessage to indicate which type of email was sent
    if statusType == False:
        if status == 200 or status == 308 or status >= 100 and status <= 299:
            subject = str(status) + " - " + site + " is UP"
            logMessage = "Successfully sent UP notification (to: " + email + ")"
        else:
            subject = "Error " + str(status) + " - " + site + " is DOWN"
            logMessage = "Successfully sent error (DOWN) notification (to: " + email + ")"
    else:
        subject = "Error " + str(status) + " - " + site + " is DOWN"
        logMessage = "Successfully sent error (DOWN) notification (to: " + email + ")"
    
    # specify SMTP server details to connect to
    try:
        server = SMTP('<mail_server>:<port>')
        server.starttls()
        server.login('example@example.com', '<password>')
    except OSError as error:
        logging.error("Error sending mail")
        return

    # send email notification
    try:
        server.sendmail(fromaddr, toaddrs, 'Subject: %s\r\n%s' % ("[Python Web Monitor]: " + subject, SMTPMessage))
        print(logMessage)
        logging.info(logMessage)
    except SMTPException:
        print("Unable to send error notification (to: " + email + ")")
        logging.error("Unable to send error notification (to: " + email + ")")

    server.quit()

# function to convert seconds to readable time
def convertSeconds(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

# main function
def main():
    # error email tracker to  (i.e. 0 = Email Not Sent, 1 = Email Has Already Been Sent)
    errSent = 0

    # all-time checks counters for uptime %
    checks = 0 ## total checks, starts at 0
    sChecks = 0 ## successful checks, starts at 0

    # downtime counters
    isDown = False
    totalDown = 0 ## in seconds
    firstDown = 0

    # intro
    print('Starting Python Web Monitor')

    # setup logging to file & record anything from info or higher (warnings and errors)
    logging.basicConfig(level=logging.INFO, filename='python-monitor.log', 
            ## set format of log records
            format='%(asctime)s %(levelname)s: %(message)s', 
            ## set format of the date in the log records
            datefmt='%Y-%m-%d %H:%M:%S')
    
    # infinite loop to execute monitoring checks
    while True:
        try:       
            # perform GET request to check status of site (will return GET response)
            r = requests.get(site)

            # check to see if response code is a SUCCESSFUL code
            if r.status_code == 200 or r.status_code == 308 or r.status_code >= 100 and r.status_code <= 299:
                # set uptime variables
                checks += 1
                sChecks += 1
                errSent = 0 ## reset notification flag as there has now been a successful check

                # print & log downtime information after site is back up
                if isDown == True:
                    timeDown = time.perf_counter() - firstDown
                    totalDown += timeDown
                    isDown = False
                    print(site + " : Site is back up. It was down for " + convertSeconds(timeDown))
                    logging.info(site + " : Site is back up. It was down for " + convertSeconds(timeDown)) # log site is back up after downtime and print downtime info
                    email_alert(site + " is back online!", r.status_code)

                # print & log request information
                print("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " (Uptime: " + str(round((sChecks/checks)*100, 2)) + "%)" + " (Total downtime: " + convertSeconds(totalDown) + ")")
                logging.info("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " (Uptime: " + str(round((sChecks/checks)*100, 2)) + "%)" + " (Total downtime: " + convertSeconds(totalDown) + ")") ## log success
                
                time.sleep(5)

            # check to see if response code is an HTTP ERROR code
            elif r.status_code == 500 or r.status_code >= 300 and r.status_code <= 599:
                # set downtime variables
                checks += 1
                isDown = True
                firstDown = time.perf_counter()

                # print & log request information
                print("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " - " + site + " is down.")
                logging.error("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " - " + site + " is down.")

                # check to see if error email notification has already been sent for this down occurrence, if not, send
                if errSent != 1:
                    email_alert(r.reason, r.status_code) ## call notification function

                time.sleep(5)

            else: # else, error out catch-all
                # set downtime variables
                checks += 1
                isDown = True
                firstDown = time.perf_counter()

                # print & log request information
                print("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " - " + site + " is DOWN.")
                logging.error("GET " + site + " - " + str(r.status_code) + ": " + r.reason + " - " + site + " is DOWN.")
                if errSent != 1:
                    email_alert(r.reason, r.status_code)
                
                time.sleep(5)

        except requests.exceptions.InvalidURL: # if the URL is invalid format
            # print & log request information
            print("GET " + site + " : HTTP Error - Check your URL.")
            logging.error("GET " + site + " : HTTP Error - Check your URL.") ## log error

            # check to see if error email notification has already been sent for this down occurrence, if not, send
            if errSent != 1:
                email_alert('HTTP Error - Check your URL.', 'Invalid URL')

            time.sleep(5)

        except requests.ConnectionError: # if unable to connect
            # set downtime variables
            checks += 1
            isDown = True
            firstDown = time.perf_counter()

            # print & log request information
            ## first verify that there is an internet connection and the apocolapyse hasn't started
            if requests.get("https://google.ca/").status_code == 200 or requests.get("https://duckduckgo.com/").status_code == 200:
                print("GET " + site + " : Connection Error - Unable to reach " + site + ". Check that your URL is correct or your DNS settings.")
                logging.error("GET " + site + " : Connection Error - Unable to reach " + site + ". Check that your URL is correct or your DNS settings.")
            else: # internet is likely down
                print("GET " + site + " : Connection Error - Unable to reach " + site + ". Check internet connection as either the apocalypse or the internet is sleeping (or not connected).")
                logging.error("GET " + site + " : Connection Error - Unable to reach " + site + ". Check internet connection as either the apocalypse or the internet is sleeping (or not connected).")

            # check to see if error email notification has already been sent for this down occurrence, if not, send
            if errSent != 1:
                email_alert("Connection Error - Unable to reach " + site + ". Please check the log files.", 'ConnErr')

            time.sleep(5)

# execute main
if __name__ == '__main__':
    main()