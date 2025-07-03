import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
#from archeryconfig import config
import os
import json
import serial
# Global variable for the VideoCapture object
import serial.tools.list_ports

option_1_loop_id = None
option_2_loop_id = None
#-------------------------------------------
# Initialize frame counts
red_frame_count = 0
ser = None
# Setup the serial connection
#ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)  # Update as needed
#ser = serial.Serial('COM14', 57600, timeout=1)  # Replace 'COM3' with your actual COM port

# Function to send data over serial
ser = None

def serial_send(data):
    global ser
    lowbyte = data & 0xff
    highbyte = data >> 8

    try:
        # Ensure that the serial connection is open
        if ser and ser.is_open:
            print(f"Sending Data: {data} (Low: {lowbyte}, High: {highbyte})")
            ser.write(b'\xff')
            ser.write(b'\x55')
            ser.write(lowbyte.to_bytes(1, 'big'))
            ser.write((255 - lowbyte).to_bytes(1, 'big'))
            ser.write(highbyte.to_bytes(1, 'big'))
            ser.write((255 - highbyte).to_bytes(1, 'big'))
        else:
            print("Serial port not initialized or not open.")
    except Exception as e:
        print(f"Error sending data: {e}")

def send_cmd(cmd, dataH, dataL):
    # This function creates a command value from cmd, dataH, and dataL, and sends it via serial.
    serial_send(cmd * 16384 + dataH * 128 + dataL)
# Function to switch to the "Dribble & Attack" screen
def on_archery():
    menu_frame.pack_forget()  # Hide the menu frame
    create_archery_interface()  # Create the Dribble & Attack interface


def on_ball_color():
    menu_frame.pack_forget()  # Hide the menu frame
    create_ball_color_interface()  # Create the Ball Color interface

# Function to go back to the menu from any screen
def on_back_to_menu():
    # Hide any active frames
    if 'archery_frame' in globals() and archery_frame.winfo_ismapped():
        archery_frame.pack_forget()
    if 'ball_color_frame' in globals() and ball_color_frame.winfo_ismapped():
        ball_color_frame.pack_forget()

    release_webcam()  # Release the webcam when going back to the menu
    menu_frame.pack(fill=tk.BOTH, expand=True)  # Show menu frame again



# Function to release the webcam capture
def release_webcam():
    global cap
    if cap is not None:
        cap.release()
        cap = None

from PIL import Image, ImageTk  # Import Pillow for image handling

def create_interface():
    global menu_frame
    global root
    global ser
    global com_port_var

    root = tk.Tk()
    root.title("HUROCUP ARCHERY - PSIS ROBOTEAM")
    root.geometry("900x600")  # Set a size for the window

    # Common color
    default_bg = "lightgray"

    # Main Menu Frame
    menu_frame = tk.Frame(root, bg=default_bg, width=800, height=400)
    menu_frame.pack(fill=tk.BOTH, expand=True)

    # Left Side Menu
    left_frame = tk.Frame(menu_frame, width=200, bg=default_bg)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    tk.Button(left_frame, text="ARCHERY", height=2, width=20, font=("Anton", 12, "bold"), bg=default_bg, 
              command=on_archery).pack(pady=5)

    tk.Button(left_frame, text="COLOR CALIBRATION", height=2, width=20, font=("Anton", 12, "bold"), bg="lightgray",
              command=on_ball_color).pack(pady=5)

    # Line to separate Left and Middle
    tk.Frame(menu_frame, width=2, bg="black").pack(side=tk.LEFT, fill=tk.Y)

    # Middle Section for Bluetooth Pairing
    middle_frame = tk.Frame(menu_frame, bg=default_bg, width=400, height=400)
    middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Title Label
    title_label = tk.Label(middle_frame, text="HUROCUP ARCHERY - PSIS ROBOTEAM", font=("Anton", 24, "bold"), bg=default_bg, fg="black")
    title_label.pack(pady=10)

    # Add Resized Image
    try:
        # Load and resize the image
        image_path = r'D:\ARCHERY\logo.png'  # Replace 'logo.png' with the actual file name and extension
        original_img = Image.open(image_path)
        resized_img = original_img.resize((300, 300))  # Resize to 300x200 pixels (adjust as needed)

        # Convert to PhotoImage
        img = ImageTk.PhotoImage(resized_img)

        # Create a Label to display the image
        image_label = tk.Label(middle_frame, image=img, bg=default_bg)
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.pack(pady=5)  # Adjust padding as needed
    except Exception as e:
        print(f"Error loading image: {e}")

    # Box Frame
    box_frame = tk.Frame(middle_frame, bg="white", relief="solid", bd=2, padx=10, pady=10)
    box_frame.pack(pady=20, padx=20)

    # Fetch available COM ports
    com_ports = get_com_ports()

    # COM Port Dropdown
    com_port_var = tk.StringVar()
    if com_ports:  # If there are COM ports available, populate the dropdown
        com_port_var.set(com_ports[0])  # Default to the first available COM port
        com_port_combobox = tk.OptionMenu(box_frame, com_port_var, *com_ports)
        com_port_combobox.pack(pady=10)

    # Auto Search Button
    auto_search_button = tk.Button(
        box_frame,
        text="Auto Search COM Ports",
        command=lambda: auto_search_com_ports(com_port_var)
    )
    auto_search_button.pack(pady=10)

    # Send Command Button with simplified design
    send_button = tk.Button(
        box_frame,
        text="Send Command",
        command=lambda: send_cmd(1, 0x12, 0x34)
    )
    send_button.pack(pady=10)

    # Start the Tkinter main loop
    root.mainloop()



def get_com_ports():
    """Function to fetch and return a list of available USB COM ports (Linux version)."""
    com_ports = []
    # Check for both ttyUSB* and ttyACM* devices which are common for USB serial devices
    for port in serial.tools.list_ports.comports():
        if 'USB' in port.description or 'ACM' in port.device:
            com_ports.append(port.device)
    return com_ports

def auto_search_com_ports(com_port_var):
    """Function to automatically search for USB COM ports and update the dropdown."""
    com_ports = get_com_ports()  # Get the latest list of available USB COM ports
    if com_ports:
        com_port_var.set(com_ports[0])  # Set the dropdown to the first available COM port
        # Show a success message box
        messagebox.showinfo("COM Port Found", f"COM port {com_ports[0]} found and selected.")
        # Try to connect to the selected COM port
        connect_serial(com_ports[0])
    else:
        # Show an error message box if no COM ports are found
        messagebox.showerror("No COM Port Found", "No USB COM ports were found. Please check your connections.")

def connect_serial(com_port):
    """Function to initialize the serial connection based on the selected COM port."""
    global ser
    if com_port:
        try:
            # Establish a serial connection
            ser = serial.Serial(com_port, 57600, timeout=1)
            print(f"Connected to {com_port}")
        except serial.SerialException as e:
            print(f"Error: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to {com_port}. {e}")


def update_frame(cap, label):
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        # If frame capture fails, just skip updating the frame (no error message)
        return
    
    # Convert the frame from BGR to RGB (Tkinter uses RGB, not BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the frame to an Image object
    img = Image.fromarray(frame)

    # Convert the Image object to a Tkinter PhotoImage object
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the label to display the new frame
    label.imgtk = imgtk
    label.configure(image=imgtk)

    # Call the function again after 10 ms to keep updating the frame
    label.after(10, update_frame, cap, label)

def update_frame(cap, label):
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        # If frame capture fails, just skip updating the frame (no error message)
        return
    
    # Resize the frame to 340x240
    frame = cv2.resize(frame, (640, 480))
    
    # Convert the frame from BGR to RGB (Tkinter uses RGB, not BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the frame to an Image object
    img = Image.fromarray(frame)

    # Convert the Image object to a Tkinter PhotoImage object
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the label to display the new frame
    label.imgtk = imgtk
    label.configure(image=imgtk)

    # Call the function again after 10 ms to keep updating the frame
    label.after(10, update_frame, cap, label)



config_path = r'D:\ARCHERY\archeryconfig.ini'
os.makedirs(os.path.dirname(config_path), exist_ok=True)

# Initialize global variables for the lower and upper red ranges
global_lower_range_red = np.array([0, 0, 0])
global_upper_range_red = np.array([179, 255, 255])

# Global slider variables (initialize these outside functions)
red_l_h = None
red_l_s = None
red_l_v = None
red_u_h = None
red_u_s = None
red_u_v = None



import configparser
import os

# Paths for separate configuration files
interception_config_path = r'D:\ARCHERY\interception_config.ini'
slider_config_path = r'D:\ARCHERY\slider_config.ini'
delay_config_path = r'D:\ARCHERY\delay_config.ini'
offset_config_path = r'D:\ARCHERY\offset_config.ini'

adjustable_delay = 5  # Default value


# Default adjustable offset value
adjustable_offset = 20  # Default value

def save_offset_config():
    """Saves the adjustable offset to a configuration file."""
    config = configparser.ConfigParser()

    # Offset Section
    config["Offset"] = {
        "offset_value": adjustable_offset
    }

    with open(offset_config_path, 'w') as configfile:
        config.write(configfile)
    print(f"Offset configuration saved: {adjustable_offset} pixels")


def load_offset_config():
    """Loads the adjustable offset from a configuration file or creates the file with default value."""
    global adjustable_offset

    if os.path.exists(offset_config_path):
        try:
            config = configparser.ConfigParser()
            config.read(offset_config_path)

            # Load Offset Value
            adjustable_offset = int(config["Offset"].get("offset_value", adjustable_offset))

            print(f"Offset configuration loaded: {adjustable_offset} pixels")
        except Exception as e:
            print(f"Error loading offset configuration: {e}. Using default value ({adjustable_offset} pixels).")
    else:
        # File doesn't exist, create it with default value
        print(f"Offset configuration file not found at {offset_config_path}. Creating one with default value ({adjustable_offset} pixels).")
        save_offset_config()



# File paths


def save_delay_config():
    """Saves the adjustable delay to a configuration file."""
    config = configparser.ConfigParser()

    # Delay Section
    config["Delay"] = {
        "delay_time": adjustable_delay
    }

    with open(delay_config_path, 'w') as configfile:
        config.write(configfile)
    print(f"Delay configuration saved: {adjustable_delay} seconds")


def load_delay_config():
    """Loads the adjustable delay from a configuration file or creates the file with default value."""
    global adjustable_delay

    if os.path.exists(delay_config_path):
        try:
            config = configparser.ConfigParser()
            config.read(delay_config_path)

            # Load Delay Time
            adjustable_delay = int(config["Delay"].get("delay_time", adjustable_delay))

            print(f"Delay configuration loaded: {adjustable_delay} seconds")
        except Exception as e:
            print(f"Error loading delay configuration: {e}. Using default value ({adjustable_delay} seconds).")
    else:
        # File doesn't exist, create it with default value
        print(f"Delay configuration file not found at {delay_config_path}. Creating one with default value ({adjustable_delay} seconds).")
        save_delay_config()


def save_interception_config():
    global interception_point_x, interception_point_y
    config = configparser.ConfigParser()

    # Interception Point
    config["InterceptionPoint"] = {
        "x": interception_point_x,
        "y": interception_point_y,
    }

    with open(interception_config_path, 'w') as configfile:
        config.write(configfile)
    print("Interception configuration saved.")

def load_interception_config():
    global interception_point_x, interception_point_y

    if os.path.exists(interception_config_path):
        try:
            config = configparser.ConfigParser()
            config.read(interception_config_path)

            # Load Interception Point
            interception_point_x = int(config["InterceptionPoint"].get("x", interception_point_x))
            interception_point_y = int(config["InterceptionPoint"].get("y", interception_point_y))

            print("Interception configuration loaded.")
        except Exception as e:
            print(f"Error loading interception configuration: {e}")
    else:
        print("Interception configuration file not found. Using default values.")

#--------------------------------------------------------------------------------------------------------------------------------#  


 
#--------------------------------------------------------------------------------------------------------------------------------# 
def save_slider_config():
    config = configparser.ConfigParser()

    # Color Ranges
    config["ColorRanges"] = {
        "red_l_h": red_l_h.get(),
        "red_l_s": red_l_s.get(),
        "red_l_v": red_l_v.get(),
        "red_u_h": red_u_h.get(),
        "red_u_s": red_u_s.get(),
        "red_u_v": red_u_v.get(),
    }

    with open(slider_config_path, 'w') as configfile:
        config.write(configfile)
    print("Slider configuration saved.")

def load_slider_config():
    global global_lower_range_red, global_upper_range_red

    if os.path.exists(slider_config_path):
        try:
            config = configparser.ConfigParser()
            config.read(slider_config_path)

            # Load Color Ranges
            red_l_h_value = int(config["ColorRanges"].get("red_l_h", 0))
            red_l_s_value = int(config["ColorRanges"].get("red_l_s", 0))
            red_l_v_value = int(config["ColorRanges"].get("red_l_v", 0))
            red_u_h_value = int(config["ColorRanges"].get("red_u_h", 255))
            red_u_s_value = int(config["ColorRanges"].get("red_u_s", 255))
            red_u_v_value = int(config["ColorRanges"].get("red_u_v", 255))

            # Update global variables
            global_lower_range_red = (red_l_h_value, red_l_s_value, red_l_v_value)
            global_upper_range_red = (red_u_h_value, red_u_s_value, red_u_v_value)

            print("Slider configuration loaded.")
        except Exception as e:
            print(f"Error loading slider configuration: {e}")
    else:
        print("Slider configuration file not found. Using default values.")




# Call load_slider_values at the start of your progra


def create_ball_color_interface():
    global ball_color_frame, cap, red_l_h, red_l_s, red_l_v, red_u_h, red_u_s, red_u_v

    load_slider_config()

    # Create the ball color frame
    ball_color_frame = tk.Frame(root, bg="lightgray")
    ball_color_frame.pack(fill=tk.BOTH, expand=True)

    # Back Button at the top-left corner using place()
    back_button = tk.Button(ball_color_frame, text="Back", command=on_back_to_menu, bg="lightgray", font=("Anton", 10, "bold"))
    back_button.place(x=10, y=10)  # Positioning the button at the top-left corner

    # Setup Webcam feed
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access webcam")
        return
    
    mask_display_frame = tk.LabelFrame(ball_color_frame, text="Mask Display", bg="lightgray", width=340, height=240)
    mask_display_frame.place(x=10, y=50)  # Positioned below the back button

    result_display_frame = tk.LabelFrame(ball_color_frame, text="Result Display", bg="lightgray", width=340, height=240)
    result_display_frame.place(x=360, y=50)  # Positioned beside the mask display frame

    # Inside each LabelFrame, create a label for displaying the webcam frames
    mask_label = tk.Label(mask_display_frame, bg="black", width=340, height=240)
    mask_label.pack(padx=5, pady=5)

    result_label = tk.Label(result_display_frame, bg="black", width=340, height=240)
    result_label.pack(padx=5, pady=5)

    # Slider frame below the webcam frames
    slider_frame = tk.LabelFrame(ball_color_frame, text="Adjust Red Color Range", bg="lightgray")
    slider_frame.place(x=230, y=325)  # Positioned below the webcam frames

    # Slider for Lower Red Hue
    red_l_h = tk.Scale(slider_frame, from_=0, to=179, label="Lower Hue", orient=tk.HORIZONTAL)
    red_l_h.set(global_lower_range_red[0])  # Default value if config file not loaded
    red_l_h.grid(row=0, column=0, padx=10, pady=5)

    # Slider for Lower Red Saturation
    red_l_s = tk.Scale(slider_frame, from_=0, to=255, label="Lower Saturation", orient=tk.HORIZONTAL)
    red_l_s.set(global_lower_range_red[1])  # Default value if config file not loaded
    red_l_s.grid(row=1, column=0, padx=10, pady=5)

    # Slider for Lower Red Value
    red_l_v = tk.Scale(slider_frame, from_=0, to=255, label="Lower Value", orient=tk.HORIZONTAL)
    red_l_v.set(global_lower_range_red[2])  # Default value if config file not loaded
    red_l_v.grid(row=2, column=0, padx=10, pady=5)

    # Slider for Upper Red Hue
    red_u_h = tk.Scale(slider_frame, from_=0, to=179, label="Upper Hue", orient=tk.HORIZONTAL)
    red_u_h.set(global_upper_range_red[0])  # Default value if config file not loaded
    red_u_h.grid(row=0, column=1, padx=10, pady=5)

    # Slider for Upper Red Saturation
    red_u_s = tk.Scale(slider_frame, from_=0, to=255, label="Upper Saturation", orient=tk.HORIZONTAL)
    red_u_s.set(global_upper_range_red[1])  # Default value if config file not loaded
    red_u_s.grid(row=1, column=1, padx=10, pady=5)

    # Slider for Upper Red Value
    red_u_v = tk.Scale(slider_frame, from_=0, to=255, label="Upper Value", orient=tk.HORIZONTAL)
    red_u_v.set(global_upper_range_red[2])  # Default value if config file not loaded
    red_u_v.grid(row=2, column=1, padx=10, pady=5)

    # Save Button below sliders
    save_button = tk.Button(ball_color_frame, text="Save", command=save_slider_config)
    save_button.place(x=345, y=560)  # Positioned below the sliders

    # Load the saved slider values

    # Start updating frames
    update_ball_color_frame(cap, mask_label, result_label)

def update_ball_color_frame(cap, mask_display, result_display):
    ret, frame = cap.read()
    if not ret:
        return

    # Resize the frame for better visualization
    frame = cv2.resize(frame, (340, 240))

    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get slider values for Red detection
    l_h_r, l_s_r, l_v_r = red_l_h.get(), red_l_s.get(), red_l_v.get()
    u_h_r, u_s_r, u_v_r = red_u_h.get(), red_u_s.get(), red_u_v.get()

    # Red mask across one hue range
    lower_red = np.array([l_h_r, l_s_r, l_v_r])
    upper_red = np.array([u_h_r, u_s_r, u_v_r])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)

    # Apply mask to the frame
    result = cv2.bitwise_and(frame, frame, mask=mask_red)

    # Convert images to RGB for Tkinter compatibility
    mask_rgb = cv2.cvtColor(cv2.cvtColor(mask_red, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2RGB)
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Convert to Tkinter-compatible PhotoImage
    mask_tk = ImageTk.PhotoImage(image=Image.fromarray(mask_rgb))
    result_tk = ImageTk.PhotoImage(image=Image.fromarray(result_rgb))

    # Update the images in Tkinter
    mask_display.config(image=mask_tk)
    result_display.config(image=result_tk)

    # Keep a reference to the images
    mask_display.image = mask_tk
    result_display.image = result_tk

    # Repeat this function after a short delay
    mask_display.after(10, update_ball_color_frame, cap, mask_display, result_display)


cap = None  # Define cap as a global variable

def initialize_webcam():
    global cap
    # Initialize webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access webcam")
        return False
    return True



# Global variables
interception_point_x = 365  # Default X coordinate
interception_point_y = 203  # Default Y coordinate

# Define global entry variables to access the input fields across functions
entry_x = None
entry_y = None



# File to store the interception point data



 # Set the global red HSV range
# Function to create the archery interface with adjustable interception point
 # Initialize to False

# Global variable to control START ARCHERY mode
start_archery_active = False

def reset_all():
    global interception_point_x, interception_point_y, command_sent, centered
    global red_frame_count, start_archery_active, cap

    # Reset flags
    command_sent = False
    centered = False
    red_frame_count = 0
    start_archery_active = False

    # Reset webcam capture
    if cap is not None:
        cap.release()
        cap = None

    # Re-initialize the webcam
    if not initialize_webcam():
        messagebox.showerror("Error", "Cannot access webcam")

    # Show a success message after reset
    messagebox.showinfo("Reset", "System has been successfully reset.")

    print("System reset to initial state.")

    # Optionally, update the display or UI elements
    # For example, you can reset the entry fields for interception points
 
# Define adjustable_delay as a global variable
adjustable_delay = 5  # Default delay in seconds
adjustable_offset = 20  # Default offset value

def create_archery_interface():
    global archery_frame, cap, red_frame_count, start_archery_active, adjustable_delay
    global global_lower_range_red, global_upper_range_red
    global interception_point_x, interception_point_y  # Access global interception coordinates

    red_frame_count = 0
    load_interception_config()
    load_slider_config()
    load_delay_config()
    load_offset_config()

    # Dribble & Attack Frame
    archery_frame = tk.Frame(root, bg="lightgray", width=900, height=600)
    archery_frame.pack(fill=tk.BOTH, expand=True)

    # Back Button
    back_button = tk.Button(archery_frame, text="Back", command=on_back_to_menu, bg="lightgray", font=("Anton", 10, "bold"))
    back_button.place(x=10, y=10)

    # START ARCHERY Button
    def start_archery():
        global start_archery_active
        start_archery_active = True
        print("START ARCHERY mode activated.")

    option1_button = tk.Button(archery_frame, text="START ARCHERY", command=start_archery, bg="lightgray", font=("Anton", 10, "bold"))
    option1_button.place(x=80, y=10)

    # Save Button
    save_button = tk.Button(
        archery_frame, 
        text="Save", 
        command=lambda: (save_interception_config(), save_delay_config(), save_offset_config()),  # Save both configurations
        bg="lightgray", 
        font=("Anton", 10, "bold")
    )
    save_button.place(x=250, y=10)

    # Add the Delay Adjustment Section
    delay_title = tk.Label(archery_frame, text="TIME DELAY", font=("Anton", 12, "bold"), bg="lightgray")
    delay_title.place(x=700, y=290)

    # Create a frame to act as a box for the delay controls
    box_frame_delay = tk.Frame(archery_frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
    box_frame_delay.place(x=700, y=320)  # Adjust position as needed

    # Delay Controls
    delay = tk.Label(box_frame_delay, text="Seconds:", bg="white", font=("Anton", 10))
    delay.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    delay_input = tk.Entry(box_frame_delay, font=("Anton", 10), highlightbackground="black", highlightthickness=1, width=7)
    delay_input.grid(row=0, column=1, padx=5, pady=5)
    delay_input.insert(0, str(adjustable_delay))  # Pre-fill with default delay value

    def set_delay():
        global adjustable_delay
        try:
            delay_value = int(delay_input.get())
            if delay_value < 0:
                raise ValueError("Delay must be non-negative")
            adjustable_delay = delay_value
            print(f"Delay adjusted to: {adjustable_delay} seconds")
        except ValueError:
            messagebox.showerror("Error", "Invalid delay value. Please enter a positive integer.")

    set_delay_button = tk.Button(archery_frame, text="Set Delay", command=set_delay, bg="lightgray", font=("Anton", 10, "bold"))
    set_delay_button.place(x=745, y=390)

    # Video Display (Label to show the webcam feed)
    video_display = tk.Label(archery_frame, bg="black", width=640, height=480)
    video_display.place(x=20, y=50)

    # Offset Adjustment Section
    offset_title = tk.Label(archery_frame, text="OFFSET", font=("Anton", 12, "bold"), bg="lightgray")
    offset_title.place(x=700, y=450)

    # Create a frame to act as a box for the offset controls
    box_frame_offset = tk.Frame(archery_frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
    box_frame_offset.place(x=700, y=480)

    # Offset Controls
    offset_label = tk.Label(box_frame_offset, text="Threshold:", bg="white", font=("Anton", 10))
    offset_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    offset_input = tk.Entry(box_frame_offset, font=("Anton", 10), highlightbackground="black", highlightthickness=1, width=7)
    offset_input.grid(row=0, column=1, padx=5, pady=5)
    offset_input.insert(0, "20")
        # Update the offset input entry box to reflect the loaded value
    offset_input.delete(0, tk.END)  # Clear the current text
    offset_input.insert(0, str(adjustable_offset))  # Insert the loaded value



    def set_offset():
        global adjustable_offset
        try:
            offset_value = int(offset_input.get())
            if offset_value <= 0:
                raise ValueError("Offset must be a positive integer")
            adjustable_offset = offset_value
            
            print(f"Offset threshold adjusted to: {adjustable_offset}")
        except ValueError:
            messagebox.showerror("Error", "Invalid offset value. Please enter a positive integer.")
          

    set_offset_button = tk.Button(archery_frame, text="Set Offset", command=set_offset, bg="lightgray", font=("Anton", 10, "bold"))
    set_offset_button.place(x=745, y=550)


    box_frame = tk.Frame(archery_frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
    box_frame.place(x=700, y=120)  # Adjust position as needed
    # Title: Distance from Ball
    distance_title = tk.Label(archery_frame, text="INTERCEPTION POINT", font=("Anton", 12, "bold"), bg="lightgray")
    distance_title.place(x=700, y=90)

    # Interception Point Controls
    label_x = tk.Label(box_frame, text="Interception X:", bg="white", font=("Anton", 10))
    label_x.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_x = tk.Entry(box_frame, font=("Anton", 10), highlightbackground="black", highlightthickness=1, width=7)
    entry_x.grid(row=1, column=1, padx=5, pady=5)
    entry_x.insert(0, str(interception_point_x))

    label_y = tk.Label(box_frame, text="Interception Y:", bg="white", font=("Anton", 10))
    label_y.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_y = tk.Entry(box_frame, font=("Anton", 10), highlightbackground="black", highlightthickness=1, width=7)
    entry_y.grid(row=2, column=1, padx=5, pady=5)
    entry_y.insert(0, str(interception_point_y))

    def set_interception_point():
        global interception_point_x, interception_point_y
        try:
            interception_point_x = int(entry_x.get())
            interception_point_y = int(entry_y.get())
            print(f"Interception point updated to: ({interception_point_x}, {interception_point_y})")
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates. Please enter valid integers.")

    # Set Interception Point Button
    set_button = tk.Button(archery_frame, text="Set Interception Point", command=set_interception_point, bg="lightgray", font=("Anton", 10, "bold"))
    set_button.place(x=720, y=220)

    # Reset Button
    reset_button = tk.Button(archery_frame, text="Reset", command=reset_all, bg="lightgray", font=("Anton", 10, "bold"))
    reset_button.place(x=350, y=10)

    # Function to handle right-click and update interception point coordinates
    def on_right_click(event):
        # Get the coordinates of the mouse click relative to the video display
        mouse_x = event.x
        mouse_y = event.y
        
        # Update the entry fields with the coordinates
        entry_x.delete(0, tk.END)
        entry_y.delete(0, tk.END)
        entry_x.insert(0, str(mouse_x))
        entry_y.insert(0, str(mouse_y))
        
        # Update global interception coordinates
        global interception_point_x, interception_point_y
        interception_point_x = mouse_x
        interception_point_y = mouse_y
        
        print(f"Interception point set to ({interception_point_x}, {interception_point_y}) by mouse click.")

    # Bind the right-click event to the video display
    video_display.bind("<Button-3>", on_right_click)

    # Ensure webcam is initialized before proceeding
    if not initialize_webcam():
        return

    # Start the frame update loop
    update_frame(video_display)




delay_active = False  # Tracks if a delay is currently active


# Update frame function with dynamic interception point
def update_frame(video_display):
    global cap, red_frame_count, global_lower_range_red, global_upper_range_red
    global command_sent, start_archery_active, interception_point_x, interception_point_y, delay_active

    if cap is None:
        return

    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Failed to capture frame")
        return

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, global_lower_range_red, global_upper_range_red)
    cnts_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    red_detected_this_frame = False
    red_bbox = None

    frame_height, frame_width = frame.shape[:2]
    center_x = frame_width // 2
    center_y = frame_height // 2

    # Draw crosshairs
    cv2.line(frame, (0, center_y), (frame_width, center_y), (0, 255, 0), 1)
    cv2.line(frame, (center_x, 0), (center_x, frame_height), (0, 255, 0), 1)

    # Draw offset lines
    left_offset_x = center_x - adjustable_offset
    right_offset_x = center_x + adjustable_offset
    cv2.line(frame, (left_offset_x, 0), (left_offset_x, frame_height), (255, 255, 0), 1)  # Left offset line (cyan)
    cv2.line(frame, (right_offset_x, 0), (right_offset_x, frame_height), (255, 255, 0), 1)  # Right offset line (cyan)

    # Display offset indicator on the video feed
    offset_text = f"Offset: {adjustable_offset}"
    cv2.putText(frame, offset_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Draw interception line (only to the right)
    if interception_point_x > 0 and interception_point_y > 0:
        cv2.line(frame, (interception_point_x, interception_point_y), (frame_width, interception_point_y), (255, 0, 0), 2)
        cv2.putText(frame, "Interception Line", (interception_point_x + 10, interception_point_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    for c in cnts_red:
        if cv2.contourArea(c) > 500:
            red_detected_this_frame = True
            red_bbox = cv2.boundingRect(c)
            break

    if red_detected_this_frame and not getattr(update_frame, 'last_red_detected', False):
        red_frame_count += 1
    update_frame.last_red_detected = red_detected_this_frame

    if red_bbox is not None:
        x, y, w, h = red_bbox
        obj_center_x = int(x + w // 2)
        obj_center_y = int(y + h // 2)

        radius = int((w + h) / 4)
        cv2.circle(frame, (obj_center_x, obj_center_y), radius, (0, 255, 0), 2)
        cv2.putText(frame, "RED DETECTED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Only center the red object if START ARCHERY mode is active
        if start_archery_active and not delay_active:
            center_red_object(obj_center_x, center_x, 20)

        # Draw the interception point
        cv2.circle(frame, (interception_point_x, interception_point_y), 5, (0, 255, 0), -1)

        # Check if the red object's circle frame touches the interception point
        distance_to_interception = ((obj_center_x - interception_point_x) ** 2 + 
                                    (obj_center_y - interception_point_y) ** 2) ** 0.5
        point_touched = distance_to_interception <= radius

        # Check if the red object's circle frame touches or crosses the line
        right_edge_x = obj_center_x + radius
        line_touched = interception_point_x <= right_edge_x and abs(obj_center_y - interception_point_y) <= radius

        # Send command if conditions are met
        if start_archery_active and not command_sent and not delay_active:
            if point_touched or line_touched:
                print(f"Red object's circle triggered command at ({obj_center_x}, {obj_center_y}). Sending command (3, 0, 2)...")
                send_cmd(3, 0, 2)
                command_sent = False

    # Display red frame count
    cv2.putText(frame, f"Red Frame Count: {red_frame_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

    video_display.config(image=photo)
    video_display.image = photo

    video_display.after(10, update_frame, video_display)













# Initialize global variables at the start
centered = False       # Indicates if the red object is centered
command_sent = True   # Indicates if the command has already been sent
#------------------------------------------------------------------------

def center_red_object(obj_center_x, frame_center_x, threshold):
    """Adjust motor ID 19 to center the red object if it's outside the threshold."""
    global centered

    offset = obj_center_x - frame_center_x

    if abs(offset) > threshold and not centered:
        # Move the motor to center the object
        if offset > 0:
            send_cmd(3, 0, 6)  # Move motor right
            print("Moving motor right to center red object")
        else:
            send_cmd(3, 0, 5)  # Move motor left
            print("Moving motor left to center red object")
    elif abs(offset) <= threshold and not centered:
        # Stop the motor when centered
        send_cmd(3, 0, 7)  # Stop motor
        print("Red object is centered, stopping motor")

                # After stopping the motor, send the additional command
        send_cmd(3, 0, 3)  # New command after centering the object
        print("Sending command to perform the next action (3, 0, 3).")
        centered = True

        # Start the delay with countdown
        delay_before_interception(adjustable_delay)  # Pass the delay time in seconds
    else:
        print("Red object is already centered, no further movement needed.")







def delay_before_interception(delay_time):
    """Delay before proceeding to interception point with adjustable countdown display."""
    global archery_frame, delay_active, adjustable_delay

    delay_active = True

    countdown_label = tk.Label(archery_frame, text="", font=("Anton", 12, "bold"), bg="lightgray", fg="red")
    countdown_label.place(x=700, y=450)

    def update_countdown(seconds_left):
        if seconds_left > 0:
            countdown_label.config(text=f"Waiting: {seconds_left} seconds")
            root.after(1000, update_countdown, seconds_left - 1)  # Decrease by 1 second
        else:
            countdown_label.config(text="")  # Clear countdown after delay
            proceed_after_delay()

    def proceed_after_delay():
        global command_sent, delay_active
        print("Delay completed. Proceeding with interception logic...")
        delay_active = False  # Allow interception logic to resume
        command_sent = False  # Reset command flag to allow new commands
        countdown_label.destroy()  # Remove the countdown label

    # Use the provided delay_time argument for countdown (in seconds)
    update_countdown(delay_time)






    # Additional code for going back to the menu...

# Additional helper functions (like load_slider_values, on_save_archery, etc.)


    # Start updating the frame
   # update_frame()
    # Run the Tkinter main loop
if ser is not None and ser.is_open:
    ser.close()
# Initialize the interface
create_interface()
root.mainloop()


