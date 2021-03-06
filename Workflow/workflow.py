import os
import sys
import logging
# Own imports
import settings
import pixel_counter
import recolorer
import logistic_regression
from threading import Thread, Event
from time import sleep

# create logger with 'workflow'
logger = logging.getLogger('workflow')

# threads and stop handlers
threads = []
stop_events = []

def prepare_threads():
  '''Prepares a thread for every step and insert them in threads, in order, also create a
  stop event for every thread and insert them in the same order in stop_events'''
  stop_events.append(Event())
  threads.append(Thread(target = pixel_counter.run,
    args = (settings.dpics, settings.dcsv, stop_events[-1])))

  stop_events.append(Event())
  threads.append(Thread(target = logistic_regression.run,
    args = (settings.dcsv, stop_events[-1])))

  stop_events.append(Event())
  threads.append(Thread(target = recolorer.run,\
    args = (settings.accepted, settings.dpics, settings.drecolor, settings.dprecolor, stop_events[-1])))

def steps():
  '''Executes every step in the workflow and manages the possible problems'''
  # prepare the thread for every step
  prepare_threads()
  # launch them
  for t in threads:
    t.start()

def main():
  try:
    settings.init()
    steps()

    while True:
      sleep(1)
  except KeyboardInterrupt: # preven Ctrl+C exceptions
    print('Interruption detected, stopping threads and closing...')
    # stop threads
    for e in stop_events:
      e.set()
    # wait for threads to stop
    for t in threads:
      t.join()
    # exit
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)

if __name__ == '__main__':
  main()