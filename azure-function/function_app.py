import logging
import os
import azure.functions as func

text = os.getenv('testpass')

app = func.FunctionApp()

@app.schedule(schedule="*/20 * * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False)
def monitoring_timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed. The test: ' + str(text))