
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# from raptor_functions.supervised.prediction import  make_prediction
# from raptor_functions.supervised.raptor_watchdog import upload_file
import requests
import webbrowser
from csv import DictWriter





URL = "http://127.0.0.1:5001/api"



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

    ## TO DO
    # extract filename, datetime

    with open(filename, 'a') as f_object:
        
        # Pass the file object and a list
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)

        #Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(pred_dict)

        #Close the file object
        f_object.close()


def event_handler(event, url=URL):

    filepath = event.src_path

    PARAMS = {'filepath': filepath}

    r = requests.post(url=url, params=PARAMS)
    # extracting data in json format
    data = r.json()
    # print(type(data))
    pred_dict = get_pred_dict(data)
    filename = 'predictions.csv'
    csv_writer(pred_dict, filename)
    bucket = 'raptor_bucket'
    print('done')    


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

            # event_handler(event, url=URL)
            
            filepath = event.src_path
            URL = "http://127.0.0.1:5001/api"
            PARAMS = {'filepath': filepath}
            r = requests.post(url=URL, params=PARAMS)
            # extracting data in json format
            data = r.json()
            # print(type(data))
            pred_dict = get_pred_dict(data)
            filename = 'predictions.csv'
            csv_writer(pred_dict, filename)
            bucket = 'raptor_bucket'
            print('done')
            # upload_file(filename, bucket)



        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    print('Starting watchdog................................')
    w = Watcher()
    w.run()


