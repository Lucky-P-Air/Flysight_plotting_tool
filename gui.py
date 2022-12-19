import tkinter as tk
from  tkinter import filedialog
#import tkinter.ttk as ttk

MASTERWIDTH = 130  # of window
MASTERHEIGHT = 50  # of window
PAD_ALPHA = 10  # Padding of frames (large; between sections)
PAD_BETA = 2  # Padding of frames (small; within sections)
BWIDTH = 3  # Border width


def enable_usgs() -> None:
    # Need to connect to flysight_tool.get_elev & toggle boolean? Not sure
    #self.elev_bool = True
    pass

def entry_text_insert(text, ind=0) -> None:
    """Replaces text in Entry field with new text.
    Args: text: str
    Optional Args: ind: int (Non-zero index position to insert text)
    Returns: None"""
    ent_title.insert(ind, text)

def get_entry() -> str:
    """Reads text provided in Entry field.
    Args: None
    Returns: str"""
    return ent_title.get()

def get_filename() -> str:
    """Launches Open-File explorer window to locate Flysight CSV Track
    Args: None
    Returns: str(filepath/filename)"""
    filename = filedialog.askopenfilename(
        initialdir='C:/Users/mattc/Documents/Flysight', # TO-DO: replace with .env variable lookup
        title='Select a Flysight CSV file',
        filetypes=(('CSV Files', "*.csv*"), ("all files", "*.*"))
    )
    track_title = filename.split('/')[-1]  # Drop file path
    lbl_selection = tk.Label(text=f'Track: {filename}',
                             master=frm_openf,
                             width=MASTERWIDTH,
                             ).pack()
    entry_text_insert(track_title)
    return filename

def post_GUI_options() -> dict:  # Maybe a dictionary?
    """Returns all the meaningful data, names, options from GUI to primary app
    Args: None
    Returns: ??? Dictionary??

    Returned dictionary include the following keys:"""
    #gui_options = {"elev_bool": self.elev_bool.get(),
    #               "filename": self.filename,
    #               "track_title": self.track_title
    #               }
    pass

def update_title():
    new_title=get_entry()
    print(new_title)
    #self.track_title = new_title
    #return new_title

#class ControlGUI(tk.Tk):
#    self.filename = None
#    self.track_title = None
#    self.elev_bool = elev_bool.get()  # False
#    pass

#class BuilderGUI():
#    pass

# Initialize Window
window = tk.Tk()
window.title("Flysight Track Tool")
window.geometry("500x300")

# Loading Button Frame
frm_openf = tk.Frame(height=5, width=MASTERWIDTH//2, pady=PAD_ALPHA)
but_locate = tk.Button(text="Locate Flysight Track",
                       master=frm_openf,
                       borderwidth=BWIDTH,
                       command=get_filename,
                       anchor="center"
                       ).pack()  # fill=tk.X, side=tk.LEFT, expand=True)

frm_openf.pack()


# Text Input Frame
frm_text = tk.Frame(width=MASTERWIDTH, height=20, padx=PAD_ALPHA, pady=PAD_BETA)
lbl_name = tk.Label(text="Jump Title:",
                     master=frm_text,
                     borderwidth=BWIDTH,
                     anchor="w")
lbl_name.pack(side=tk.LEFT)

ent_title = tk.Entry(master=frm_text,
                     borderwidth=BWIDTH,
                     width=MASTERWIDTH//2,
                     )#.insert("Name?", 0)
ent_title.pack(side=tk.LEFT)
frm_text.pack()  #fill=tk.X, side=tk.BOTTOM, expand=True)

# Text Submit Button Frame
frm_submit_text = tk.Frame(width=MASTERWIDTH, height=10, pady=PAD_BETA)
but_submit = tk.Button(text="Update Title",
                       master=frm_submit_text,
                       borderwidth=BWIDTH,
                       #width=40,
                       command=update_title,
                       )
but_submit.pack(side=tk.BOTTOM)
frm_submit_text.pack()

# SpacerV frame
#tk.Frame(width=MASTERWIDTH, height=20).pack()

frm_checks = tk.Frame()
elev_bool = tk.BooleanVar()
chk_getelev = tk.Checkbutton(text="Include Ground Elevation from USGS",
                             master=frm_checks,
                             borderwidth=BWIDTH,
                             pady=PAD_ALPHA,
                             variable=elev_bool,
                             #onvalue=True,
                             #offvalue=False,
                             #command=enable_usgs,
                             )
chk_getelev.pack()
frm_checks.pack()

# SpacerV frame
#tk.Frame(width=MASTERWIDTH, height=20).pack()

# Plot-Button Frame
frm_plot = tk.Frame()
but_plot = tk.Button(text="Plot Track",
                     master=frm_plot,
                     borderwidth=BWIDTH,
                     width=MASTERWIDTH//3,
                     height=2,
                     command=post_GUI_options,
                     )
but_plot.pack()
frm_plot.pack()

# SpacerV frame
#tk.Frame(width=MASTERWIDTH, height=20).pack()

# Exit/Close Button
frm_exit = tk.Frame(height=20, pady=PAD_ALPHA)
but_exit = tk.Button(text="Close",
                     master=frm_exit,
                     borderwidth=BWIDTH,
                     command=window.quit,
                     ).pack()

frm_exit.pack()  #fill=tk.X, side=tk.BOTTOM, expand=True)

window.mainloop()
