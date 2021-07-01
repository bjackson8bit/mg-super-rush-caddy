#!/usr/bin/env python
from functools import partial
from tkinter.constants import BOTTOM, LEFT, RIGHT, TOP
try:
    from PIL import Image
except ImportError:
    import Image
import time
from cv2 import cv2
import sys
from datetime import datetime
from scripts.utils.video_stream_helper import VideoStreamWidget
from scripts.utils.event_logging import log_event, save_image
from parse_scores import get_results_data, is_results_screen, is_hole_screen, get_hole_data
from skimage import io
import queue
from tkinter import Button, Frame, Radiobutton, Label, StringVar, IntVar, Tk
import tkinter
import threading
import sys


class GuiPart:
    def __init__(self, master, queue, end_command, start_parsing_command, set_vcam_command, preview_vcam_command):
        self.queue = queue
        header = Label(master, text="Mario Golf Super Rush Parser", font=("Arial", 15))
        bot_frame = Frame(master, pady=20)

        left_frame = Frame(bot_frame, padx=10)

        # idk
        vcam_label = Label(left_frame, text="Select Virtual Cam", font=("Arial", 10))
        vcam_label.pack(side=TOP)
        vcam_subtitle = Label(left_frame, text="(Default = 1)", font=("Arial", 10))
        vcam_subtitle.pack(side=TOP)
        vcam_var = IntVar()
        vcam_var.set(1)

        for i in range(5):
            r1 = Radiobutton(left_frame, text=str(i+1), indicatoron=0, width=10, padx=10, variable=vcam_var, value=i+1, command=lambda: set_vcam_command(vcam_var.get()), anchor=tkinter.W)
            r1.pack(side=TOP)
        preview_button = Button(left_frame, text='Preview VCam', command=preview_vcam_command)
        preview_button.pack(side=TOP)

        # Set up the GUI
        right_frame = Frame(bot_frame, padx=10)
        resolution_var = StringVar()
        res_label = Label(right_frame, text="OBS Output Resolution", font=("Arial", 10))
        
        res_label.pack(side=TOP)
        r1 = Radiobutton(right_frame, text="720p", indicatoron=0, width=10, padx=10, variable=resolution_var, value='720p', anchor=tkinter.W)
        r1.pack(side=TOP)
        r2 = Radiobutton(right_frame, text="1080p", indicatoron=0, width=10, padx=10, variable=resolution_var, value='1080p', anchor=tkinter.W)
        r2.pack(side=TOP)
        start_button = Button(right_frame, text='Start Parsing', command=lambda: start_parsing_command(resolution_var.get()))
        start_button.pack(side=TOP)
        done_button = Button(right_frame, text='Done Parsing', command=end_command)
        done_button.pack(side=TOP)

        left_frame.pack(side=LEFT)
        right_frame.pack(side=LEFT)

        header.pack(side=TOP)
        bot_frame.pack(side=TOP)


        
        # console.pack()
        # Add more GUI stuff here depending on your specific needs

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

class SuperRushScoreParser():
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master, virtual_cam=1):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master
        self.virtual_cam = virtual_cam
        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.end_application, self.start_parsing, self.set_virtual_cam, self.preview_virtual_cam)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = True
        self.stream = None
        self.thread1 = None
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodic_call()


    def parse_superrush_multplayer(self):
        time.sleep(1)
        old_ts = self.stream.now
        last_result_parse_ts = 0
        last_hole_parse_ts = 0
        downtime_end_ts = 0
        tick_count = 0
        while self.stream.status and self.running:
            img = self.stream.frame
            now_ts = self.stream.now
            tick_count += 1
            if now_ts >= downtime_end_ts:
                if now_ts - last_result_parse_ts > 0.2:
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    last_result_parse_ts = now_ts
                    if is_results_screen(rgb_img):
                        res = None
                        for _ in range(5):
                            time.sleep(0.1)
                            if res:
                                self.queue.put(res)
                                downtime_end_ts = now_ts + 20
                                break
                            res = get_results_data(rgb_img)
                if now_ts - last_hole_parse_ts > 5:
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    last_hole_parse_ts = now_ts
                    if is_hole_screen(rgb_img):
                        res = get_hole_data(rgb_img)
                        if res:
                            self.queue.put(f"Hole {res}")
                    # else:
                    #     self.queue.put(f"Not Hole")          
            old_ts = now_ts
            self.stream.update()

        self.stream.finish()


    def periodic_call(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming( )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            if self.stream is not None:
                self.stream.finish()
            print("Closing Parser")
            sys.exit(1)
        self.master.after(200, self.periodic_call)


    def end_application(self):
        self.running = False
    

    def start_parsing(self, resolution):
        if resolution is None or resolution == "":
            print("Resolution is not selected")
            return

        if self.stream is not None or self.thread1 is not None:
            print("Parsing is already running")
        else: 
            print(f"Starting Golf Parsing in {resolution}")
            self.stream = VideoStreamWidget(self.virtual_cam, resolution)
            self.thread1 = threading.Thread(target=self.parse_superrush_multplayer)
            self.thread1.start()
    
    def set_virtual_cam(self, idx):
        self.virtual_cam = idx

    def preview_virtual_cam(self):
        cam = cv2.VideoCapture(self.virtual_cam)
        if not cam:
            print(f"Virtual Camera {self.virtual_cam} not found")
            return
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        while True:
            _, img = cam.read()
            if img is None or (img.shape[0] == 0 or img.shape[1] == 0):
                print(f"No input detected for Virtual Camera {self.virtual_cam}")
                break 
            cv2.imshow('Virtual Camera - Downscaled to 720p [PRESS ESC TO EXIT]', img)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit
        cv2.destroyAllWindows()


root = Tk()
root.title('MGSR Score Parser')

client = SuperRushScoreParser(root, virtual_cam=1)
root.mainloop()