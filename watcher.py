#source: https://stackoverflow.com/a/39373932
import logging
import sys
import time
import os
import subprocess
import PIL
import imghdr
#my function, writeHealthDataServer
from datetime import date, datetime, timedelta
from writeHealthDataServer import writeHealthDataServer
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from subprocess import call
from google.cloud import storage
from PIL import Image

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        # Take any action here when a file is first created.
        elif (event.event_type == 'created'):
          print("file created")
          # Determine when file was created
          timestamp = datetime.now().strftime("%Y-%m-%d")
          # Determine where  file was created    
          dir_split = event.src_path.split('/')
          dir = dir_split[0] + "/" + dir_split[1] + "/" #e.g. /color/input/
          print "Received created event - %s." % event.src_path
          # Run thermal image processing
          if dir == "thermal/input/":
            print "Thermal"
            # Make sure file is uploaded by polling the size
            size = os.path.getsize(event.src_path)
            uploading = True
            while uploading == True:
              time.sleep(1)
              new_size = os.path.getsize(event.src_path)
              print(new_size)
              if (size != 0.0) & (new_size != 0.0):
                if (abs(size-new_size) == 0.0):
                  if (new_size > 10000):
                    #print("size is greater than 0.5 Mb")
                    print("done uploading...")
                    uploading = False
                  else:
                    size = new_size
                else:
                    size = new_size
              else:
                  size = new_size
            time.sleep(3)
            #rename file to timestamp
            command = "./thermal/main " + dir_split[2]
            print("command: ", command)
            call(["./thermal/main", dir_split[2]])
            os.remove(event.src_path)
            writeHealthDataServer(os.path.splitext(dir_split[2])[0], "thermal")
          # Run color image processing
          elif dir == "color/input/":
            print "Color"
          # Make sure file is uploaded by polling the size
            size = os.path.getsize(event.src_path)
            uploading = True
            while uploading == True:
              time.sleep(1)
              new_size = os.path.getsize(event.src_path)
              print(new_size)
              if (size != 0.0) & (new_size != 0.0):
                if (abs(size-new_size) == 0.0):
                  if (new_size > 950000):
                    #print("size is greater than 0.5 Mb")
                    print("done uploading...")
                    uploading = False
                  else:
                    size = new_size
                else:
                    size = new_size
              else:
                  size = new_size
            time.sleep(3)

            command = "./color/main " + dir_split[2]
            print(command)
            call(["./color/main", dir_split[2]])
            os.remove(event.src_path)
            writeHealthDataServer(os.path.splitext(dir_split[2])[0], "color")
            ########James Code ###########
            #Upload validation txt file to GC Bucket
            bucket_name = 'facevalidation'
            source_file_name = "color/output/face.txt"
            destination_blob_name = "face.txt"
            """Uploads a file to the bucket."""
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
      
            blob.upload_from_filename(source_file_name)
      
            print('File {} uploaded to {}.'.format(
              source_file_name,
              destination_blob_name))
            
            
# function that handles event
event_handler = Handler()
# Create Observer to watch directories
observer = Observer()
# take in list of paths.  If none given, watch CWD
paths = open(sys.argv[1], 'r') if len(sys.argv) > 1 else '.'
# Empty list of observers .
observers = []
# Base logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# iterate through paths and attach observers
for line in paths:
    # convert line into string and strip newline character
    targetPath = str(line).rstrip()
    # Schedules watching of a given path
    observer.schedule(event_handler, targetPath)
    # Add observable to list of observers
    observers .append(observer)

# start observer
observer.start()

try:
    while True:
        # poll every second
        time.sleep(1)
except KeyboardInterrupt:
    for o in observers:
        o.unschedule_all()
        # stop observer if interrupted
        o.stop()
for o in observers:
    # Wait until the thread terminates before exit
    o.join()