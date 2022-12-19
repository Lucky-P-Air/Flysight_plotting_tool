from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import filedialog
# import tkinter.ttk as ttk

MASTERWIDTH = 130  # of window
MASTERHEIGHT = 50  # of window
PAD_ALPHA = 10  # Padding of frames (large; between sections)
PAD_BETA = 2  # Padding of frames (small; within sections)
BWIDTH = 3  # Border width


def entry_text_clear() -> None:
    """Clears Entry Text Field"""
    ent_title.delete(0, tk.END)


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


def get_filename() -> None:
    """Launches Open-File explorer window to locate Flysight CSV Track
    Args: None
    Returns: str(filepath/filename)"""
    filename = filedialog.askopenfilename(
        initialdir='C:/Users/mattc/Documents/Flysight',  # TO-DO: replace with .env variable lookup
        title='Select a Flysight CSV file',
        filetypes=(('CSV Files', "*.csv*"), ("all files", "*.*"))
    )
    newtitle = filename.split('/')[-1]  # Drop file path
    tk.Label(text=f'Track (path/filename): {filename}',
             master=frm_openf,
             width=MASTERWIDTH,
             ).pack()
    entry_text_clear()
    entry_text_insert(newtitle)


def post_gui_options() -> dict:  # Maybe a dictionary?
    """Returns all the meaningful data, names, options from GUI to primary app
    Args: None
    Returns: ??? Dictionary??

    Returned dictionary include the following keys:"""
    gui_options = {"elev_bool": elev_bool.get(),
                   "filename": track_filename.get(),
                   "track_title": track_title.get(),
                   }
    for item, value in gui_options.keys():
        print(f'{item}: {value}')
    return gui_options


def update_title():
    new_title = get_entry()
    print(new_title)
    # self.track_title = new_title
    # return new_title


class ControlGUI(tk.Tk):
    def __init__(self, geometry=(500, 300), title="Flysight Track"):
        super().__init__()
        self.title(title)  # TO-DO: Replace This with a @setter
        self.geometry(f"{int(geometry[0])}x{int(geometry[1])}")  # TO-DO: Replace This with a @setter
#    self.filename = None
#    self.track_title = None
#    self.elev_bool = elev_bool.get()  # False
#    pass


class GUIBuilder(ABC):
    """GUI Builder Interface.
    May be unnecessary since only 1 Builder is planned (ControlGUIBuilder)"""
    @abstractmethod
    def pack_frm_input(self) -> None:
        pass

    @abstractmethod
    def pack_frm_chks(self) -> None:
        pass

    @abstractmethod
    def pack_frm_plot(self) -> None:
        pass

    @abstractmethod
    def pack_frm_exit(self) -> None:
        pass


class ControlGUIBuilder(GUIBuilder):
    """Concrete ControlGUI Builder class used to build up ControlGUI
    TO-DO: Pass in optional parameters for ControlGUI()"""
    def __init__(self) -> None:
        """Initialize blank slate object"""
        self.reset()

    def reset(self) -> None:
        self._gui = ControlGUI()

    @property
    def gui(self) -> ControlGUI:
        """Retrieve the built ControlGUI() object"""
        gui = self._gui
        self.reset()
        return gui

    def pack_frm_input(self) -> None:
        pass

    def pack_frm_chks(self) -> None:
        pass

    def pack_frm_plot(self) -> None:
        pass

    def pack_frm_exit(self) -> None:
        pass


if __name__ == "__main__":
    # Initialize Window
    window = tk.Tk()
    window.title("Flysight Track Tool")
    window.geometry("500x300")

    # Initialize Frame for file input widgets
    frm_input_file = tk.LabelFrame(width=MASTERWIDTH)

    # Loading Button Frame
    frm_openf = tk.LabelFrame(master=frm_input_file,
                              height=5,
                              width=MASTERWIDTH//2,
                              pady=PAD_ALPHA,
                              )
    track_filename = tk.StringVar()
    but_locate = tk.Button(text="Locate Flysight Track",
                           master=frm_openf,
                           width=25,
                           borderwidth=BWIDTH,
                           command=get_filename,
                           textvariable=track_filename,
                           anchor="center",
                           )
    but_locate.pack()  # fill=tk.X, side=tk.LEFT, expand=True)
    frm_openf.pack()

    # Text Input Frame
    frm_text = tk.LabelFrame(master=frm_input_file,
                             width=MASTERWIDTH,
                             height=20,
                             padx=PAD_ALPHA,
                             pady=PAD_BETA,
                             )
    lbl_name = tk.Label(text="Jump Title:",
                        master=frm_text,
                        borderwidth=BWIDTH,
                        anchor="w",
                        )
    lbl_name.pack(side=tk.LEFT)

    track_title = tk.StringVar()
    ent_title = tk.Entry(master=frm_text,
                         borderwidth=BWIDTH,
                         width=MASTERWIDTH//2,
                         textvariable=track_title
                         )  # .insert("Name?", 0)
    ent_title.pack(side=tk.LEFT)
    frm_text.pack()  # fill=tk.X, side=tk.BOTTOM, expand=True)

    # Text Submit Button Frame
    frm_submit_text = tk.LabelFrame(master=frm_input_file,
                                    width=MASTERWIDTH,
                                    height=10,
                                    pady=PAD_BETA,
                                    )
    but_submit = tk.Button(text="Update Title",
                           master=frm_submit_text,
                           borderwidth=BWIDTH,
                           # width=40,
                           command=update_title,
                           )
    but_submit.pack()
    frm_submit_text.pack()

    frm_input_file.pack()

    # SpacerV frame
    # tk.Frame(width=MASTERWIDTH, height=20).pack()

    frm_checks = tk.LabelFrame()
    elev_bool = tk.BooleanVar()
    chk_getelev = tk.Checkbutton(text="Include Ground Elevation from USGS",
                                 master=frm_checks,
                                 borderwidth=BWIDTH,
                                 pady=PAD_ALPHA,
                                 variable=elev_bool,
                                 # onvalue=True,
                                 # offvalue=False,
                                 # command=enable_usgs,
                                 )
    chk_getelev.pack()
    frm_checks.pack()

    # SpacerV frame
    # tk.Frame(width=MASTERWIDTH, height=20).pack()

    # Plot-Button Frame
    frm_plot = tk.LabelFrame()
    but_plot = tk.Button(text="Plot Track",
                         master=frm_plot,
                         borderwidth=BWIDTH,
                         width=MASTERWIDTH//3,
                         height=2,
                         command=post_gui_options,
                         )
    but_plot.pack()
    frm_plot.pack()

    # SpacerV frame
    # tk.Frame(width=MASTERWIDTH, height=20).pack()

    # Exit/Close Button
    frm_exit = tk.LabelFrame(height=20, pady=PAD_ALPHA)
    but_exit = tk.Button(text="Close",
                         master=frm_exit,
                         borderwidth=BWIDTH,
                         command=window.quit,
                         )
    but_exit.pack()

    frm_exit.pack()  # fill=tk.X, side=tk.BOTTOM, expand=True)

    window.mainloop()
