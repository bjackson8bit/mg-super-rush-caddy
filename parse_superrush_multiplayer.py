#!/usr/bin/env python
from scripts.utils.event_logging import OutputConn
from google_sheets import SheetsOutputConn, check_creds, create_sheet, get_sheet_from_id
from tkinter.constants import LEFT, RIGHT, TOP, BOTTOM
import time
from cv2 import cv2
from scripts.utils.video_stream_helper import VideoStreamWidget
from scripts.parsing.parse_score import get_results_data, is_results_screen, result_to_string
from scripts.parsing.parse_hole import is_hole_screen, get_hole_data
from tkinter import Text, Button, Frame, Radiobutton, Label, StringVar, IntVar, Tk, filedialog
import tkinter
import threading
import sys

# if anyone is looking for evidence that I am not a frontend developer here it is
class GuiPart:
    def __init__(self, master,
    end_command, start_parsing_command, 
    set_vcam_command, preview_vcam_command, 
    set_text_output_command, set_sheets_output_command):
        header = Label(master, text="Mario Golf Super Rush Parser", font=("Arial", 15))
        bot_frame = Frame(master, pady=20)

        # Set up the GUI
        left_frame = self.get_output_frame(bot_frame, set_text_output_command, set_sheets_output_command)
        mid_frame = self.get_vcam_preview_frame(bot_frame, set_vcam_command, preview_vcam_command)
        right_frame = self.get_parsing_frame(bot_frame, end_command, start_parsing_command)
        left_frame.pack(fill=tkinter.Y, side=LEFT)
        mid_frame.pack(fill=tkinter.Y, side=LEFT)
        right_frame.pack(fill=tkinter.Y, side=LEFT)
    
        header.pack(side=TOP)
        bot_frame.pack(side=TOP)

    def file_explorer(self, label, var, valid_label):
        filename = filedialog.askopenfilename(initialdir = ".",
                                    title = "Select Credentials File",
                                    filetypes = (("JSON",
                                                "*.json*"),
                                                ("all files",
                                                "*.*")))
        if not filename:
            return
        label.configure(text="File Opened: ..." + filename[-20:])
        var.set(filename)
        creds = check_creds(filename)
        ret_label = "Failed to Authenticate" if not creds or not creds.valid else "Authorization Success"
        valid_label.configure(text=ret_label)


    def check_sheet_conn(self, sheet_id, cred_file, valid_label, init_col, init_row, set_sheets_output_conn):
        sheet_data = get_sheet_from_id(sheet_id, cred_file)
        ret_label = "Failed to Connect to Sheet" if sheet_data is None else "Successfully Connected to Sheet"
        valid_label.configure(text=ret_label)
        if sheet_data is not None:
            set_sheets_output_conn(cred_file, sheet_id, init_col, init_row)
    


    def get_output_frame(self, master, set_text_output_command, set_sheets_output_command):
        frame = Frame(master, padx=10)
        sheets_frame = Frame(frame)
        output_type_var = StringVar()
        def update_output(output_type):
            if output_type == "googlesheets":
                sheets_frame.pack(side=TOP)
            else:
                sheets_frame.pack_forget()
                set_text_output_command()

        res_label = Label(frame, text="Output", font=("Arial", 10))
        
        res_label.pack(side=TOP)
        r1 = Radiobutton(frame, text="Text File", command=lambda: update_output(output_type_var.get()), indicatoron=0, width=10, padx=10, 
            variable=output_type_var, value='text', anchor=tkinter.W)
        r1.pack(side=TOP)
        r2 = Radiobutton(frame, text="Google Sheets", command=lambda: update_output(output_type_var.get()) ,indicatoron=0, width=10, padx=10, 
            variable=output_type_var, value='googlesheets', anchor=tkinter.W)
        r2.pack(side=TOP)

        sheet_cfg_label = Label(sheets_frame, text="Google Sheets Configuration", font=("Arial", 10))
        sheet_cfg_label.pack(side=TOP)
        cred_file = StringVar()
        creds_valid_label= Label(sheets_frame, text="", font=("Arial", 8))

        load_button = Button(sheets_frame, text='Load Creds', command=lambda: self.file_explorer(cred_file_label, cred_file, creds_valid_label))
        load_button.pack(side=TOP)
        cred_file_label = Label(sheets_frame, text="")
        cred_file_label.pack(side=TOP)
        creds_valid_label.pack(side=TOP)
        
        def create_sheet_update_id(sheet_name, creds_filename, tgt_text):
            if creds_filename:
                if sheet_name:
                    new_sheet_id = create_sheet(sheet_name, creds_filename)
                    if new_sheet_id:
                        tgt_text.delete(1.0, "end")
                        tgt_text.insert(1.0, new_sheet_id)
                    else:
                        print("Failed to create new sheet")
                else:
                    print('Please enter sheet name')
            else:
                print("Unable to validate credentials")

        create_sheet_frame = Frame(sheets_frame)
        sheet_id_frame = Frame(sheets_frame)

        sheet_id_text = Text(sheet_id_frame, height=1, width=15)
        sheet_name = Text(create_sheet_frame, height=1, width=15)
        new_sheet_label = Button(create_sheet_frame, command=lambda: create_sheet_update_id(sheet_name.get("1.0", "end-1c"), cred_file.get(), sheet_id_text),text="Create Sheet w/ Name:")
        new_sheet_label.pack(side=LEFT)
        sheet_name.pack(side=LEFT)
        create_sheet_frame.pack(side=TOP, fill=tkinter.X)
        
        sheet_id_label = Label(sheet_id_frame, text="Sheet ID:")
        sheet_id_label.pack(side=LEFT)

        sheet_id_text.pack(side=LEFT)
        sheet_id_frame.pack(side=TOP, fill=tkinter.X)
        
        idx_frame = Frame(sheets_frame)

        init_col = Label(idx_frame, text="Column:")
        init_col.pack(side=LEFT)
        init_col_text = Text(idx_frame,  height=1, width=5) 
        init_col_text.pack(side=LEFT)
        init_col_text.insert(1.0, "B")
        init_row = Label(idx_frame, text="Row:")
        init_row.pack(side=LEFT)
        init_row_text = Text(idx_frame, height=1, width=5)
        init_row_text.pack(side=LEFT)  
        init_row_text.insert(1.0, "2")
        idx_frame.pack(side=TOP)
        sheet_name.pack(side=LEFT)

        sheet_conn_valid_label = Label(sheets_frame, text="", font=("Arial", 8))
        check_sheets_conn_button = Button(sheets_frame, text='Check Sheets Connection', 
            command=lambda:self.check_sheet_conn(
                sheet_id_text.get("1.0", "end-1c"), 
                cred_file.get(), 
                sheet_conn_valid_label, 
                init_col_text.get("1.0", "end-1c"), 
                init_row_text.get("1.0", "end-1c"), 
                set_sheets_output_command))
        check_sheets_conn_button.pack(side=TOP)
        sheet_conn_valid_label.pack(side=TOP)

        
        return frame


    def get_vcam_preview_frame(self, master, set_vcam_command, preview_vcam_command):
        frame = Frame(master, padx=10)

        # idk
        vcam_label = Label(frame, text="Select Virtual Cam", font=("Arial", 10))
        vcam_label.pack(side=TOP)
        vcam_subtitle = Label(frame, text="(Default = 1)", font=("Arial", 10))
        vcam_subtitle.pack(side=TOP)
        vcam_var = IntVar()
        vcam_var.set(1)

        for i in range(5):
            r1 = Radiobutton(frame, text=str(i+1), indicatoron=0, width=10, padx=10, variable=vcam_var, value=i+1, command=lambda: set_vcam_command(vcam_var.get()), anchor=tkinter.W)
            r1.pack(side=TOP)
        preview_button = Button(frame, text='Preview VCam', command=preview_vcam_command)
        preview_button.pack(side=TOP)
        return frame

    def get_parsing_frame(self, master, end_command, start_parsing_command):
        frame = Frame(master, padx=10)
        resolution_var = StringVar()
        res_label = Label(frame, text="OBS Output Resolution", font=("Arial", 10))
        
        res_label.pack(side=TOP)
        r1 = Radiobutton(frame, text="720p", indicatoron=0, width=10, padx=10, variable=resolution_var, value='720p', anchor=tkinter.W)
        r1.pack(side=TOP)
        r2 = Radiobutton(frame, text="1080p", indicatoron=0, width=10, padx=10, variable=resolution_var, value='1080p', anchor=tkinter.W)
        r2.pack(side=TOP)
        start_button = Button(frame, text='Start Parsing', command=lambda: start_parsing_command(resolution_var.get()))
        start_button.pack(side=TOP)
        done_button = Button(frame, text='Done Parsing', command=end_command)
        done_button.pack(side=TOP)
        return frame

class SuperRushScoreParser():
    """
    """
    def __init__(self, master, virtual_cam=1):
        """
        """
        self.master = master
        self.virtual_cam = virtual_cam
        # Create the queue
        self.output_conn = OutputConn()

        # Set up the GUI part
        self.gui = GuiPart(master,
            self.end_application, self.start_parsing, 
            self.set_virtual_cam, self.preview_virtual_cam, 
            self.set_text_output_conn, self.set_sheets_output_conn)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = True
        self.stream = None
        self.thread1 = None
        self.last_known_score = None


    def parse_superrush_multplayer(self):
        current_hole_str = '-'
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
                                downtime_end_ts = now_ts + 20
                                break
                            res = get_results_data(rgb_img)
                        if res:
                            self.last_known_score = res
                            data = [[result_to_string(val), current_hole_str] for val in res]
                            self.output_conn.write_rows(data)
                if now_ts - last_hole_parse_ts > 20:
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    last_hole_parse_ts = now_ts
                    if is_hole_screen(rgb_img):
                        res = get_hole_data(rgb_img)
                        if res:
                            if current_hole_str == '-' \
                                or current_hole_str == 'F' \
                                    or res == "F" \
                                        or res == int(current_hole_str) + 1:
                                current_hole_str = str(res)
            self.stream.update()
        self.stream.finish()


    def end_application(self):
        if self.last_known_score:
            data = [[result_to_string(val), 'F'] for val in self.last_known_score]
            self.output_conn.write_rows(data)
        self.running = False
        self.stream.finish()
        sys.exit(0)

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
            time.sleep(1)
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

    def set_sheets_output_conn(self, creds_filename, sheet_id, init_col, init_row):
        self.output_conn = SheetsOutputConn(creds_filename, sheet_id, init_col, init_row)

    def set_text_output_conn(self):
        self.output_conn = OutputConn()


root = Tk()
root.title('MGSR Caddy')

client = SuperRushScoreParser(root)
root.mainloop()