
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# from raptor_functions.supervised.prediction import  make_prediction
from raptor_functions.supervised.raptor_watchdog import upload_file
import requests
import webbrowser
from csv import DictWriter







def get_pred_dict(data):
    pred_dict = {}

    pred_dict['final_pred'] = data['final prediction']
    for idx, i in enumerate(data['model predictions'][1:-1].split(',')):

        name = i.split(':')[0].strip()[1:-1]
        pred = i.split(':')[1].strip()
        pred_dict[name] = pred

        # print('name: ', name)
        # print('prediction: ', pred)
    
    return pred_dict


def csv_writer(pred_dict, filename='predictions.csv'):
        # Import DictWriter class from CSV module

    field_names = list(pred_dict.keys())

    # Open your CSV file in append mode
    # Create a file object for this file

    with open(filename, 'a') as f_object:
        
        # Pass the file object and a list
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)

        #Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(pred_dict)

        #Close the file object
        f_object.close()


class Watcher:
    DIRECTORY_TO_WATCH = "/Users/amash/Insync/GDrive/Projects/Raptor/others"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print( "Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print ("Received created event - %s." % event.src_path)
            filepath = event.src_path
            URL = "http://127.0.0.1:5001/api"
            PARAMS = {'filepath': filepath}
            r = requests.post(url=URL, params=PARAMS)
            # extracting data in json format
            data = r.json()
            # print(type(data))
            pred_dict = get_pred_dict(data)
            filename = 'prediction.csv'
            csv_writer(pred_dict, filename)
            bucket = 'raptor_bucket'
            upload_file(filename, bucket)






        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()









# import watchdog.events
# import watchdog.observers
# import time


# class Handler(watchdog.events.PatternMatchingEventHandler):
# 	def __init__(self):
# 		# Set the patterns for PatternMatchingEventHandler
# 		watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.csv'],
# 															ignore_directories=True, case_sensitive=False)

# 	def on_created(self, event):
# 		print("Watchdog received created event - % s." % event.src_path)
# 		# Event is created, you can process it now

# 	def on_modified(self, event):
# 		print("Watchdog received modified event - % s." % event.src_path)
# 		# Event is modified, you can process it now


# if __name__ == "__main__":
# 	src_path = r"C:\Users\GeeksforGeeks\PycharmProjects\requests hotel"
# 	event_handler = Handler()
# 	observer = watchdog.observers.Observer()
# 	observer.schedule(event_handler, path=src_path, recursive=True)
# 	observer.start()
# 	try:
# 		while True:
# 			time.sleep(1)
# 	except KeyboardInterrupt:
# 		observer.stop()
# 	observer.join()
