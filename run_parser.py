from parsers.gas_parser import run as gas_run
from parsers.water_parser import run as water_run
from parsers.elect_parser import run as elect_run
from datetime import datetime


def start():
    gas_run()
    #elect_run()
    #water_run()
    print("---------------------------------------")

print("---------------------------------------")
print(f"Starting cron job at: {datetime.now()}")
#start()
print("---------------------------------------")
