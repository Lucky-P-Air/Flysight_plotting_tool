from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import filedialog
# import tkinter.ttk as ttk

MASTERWIDTH = 130  # of window
MASTERHEIGHT = 50  # of window
PAD_ALPHA = 10  # Padding of frames (large; between sections)
PAD_BETA = 2  # Padding of frames (small; within sections)
BWIDTH = 3  # Border width


class ControlGUI(tk.Tk):
    def __init__(self, geometry=(500, 300), title="Flysight Track"):
        super().__init__()
        self.title(title)  # TO-DO: Replace This with a @setter
        self.geometry(f"{int(geometry[0])}x{int(geometry[1])}")  # TO-DO: Replace This with a @setter
        self.MASTERWIDTH = 130  # of window
        self.MASTERHEIGHT = 50  # of window
        self.PAD_ALPHA = 10  # Padding of frames (large; between sections)
        self.PAD_BETA = 2  # Padding of frames (small; within sections)
        self.BWIDTH = 3  # Border width
        self.track_filename = None
        self.track_title = None
        self.gui_options = {}
#    self.filename = None
#    self.track_title = None
#    self.elev_bool = elev_bool.get()  # False

# Some of these methods could be abstracted into lower-level classes of GUI-subcomponents
    def entry_text_clear(self) -> None:
        """Clears Entry Text Field"""
        self.ent_title.delete(0, tk.END)

    def entry_text_insert(self, text, ind: int = 0) -> None:
        """Replaces text in Entry field with new text.
        Args: text: str
        Optional Args: ind: int (Non-zero index position to insert text)
        Returns: None"""
        self.ent_title.insert(ind, text)

    def get_entry(self) -> str:
        """Reads text provided in Entry field.
        Args: None
        Returns: str"""
        return self.ent_title.get()

    def get_filename(self) -> None:
        """Launches Open-File explorer window to locate Flysight CSV Track
        Args: None
        Returns: str(filepath/filename)"""
        self.track_filename = filedialog.askopenfilename(
            initialdir='C:/Users/mattc/Documents/Flysight',  # TO-DO: replace with .env variable lookup
            title='Select a Flysight CSV file',
            filetypes=(('CSV Files', "*.csv*"), ("all files", "*.*"))
        )
        self.track_title = self.track_filename.split('/')[-1]  # Drop file path
        # tk.Label(text=f'Track (path/filename): {self.track_filename}',
        #          master=self.frm_openf,
        #          width=self.MASTERWIDTH,
        #          ).pack()
        self.lbl_filename['text'] = self.track_filename
        self.entry_text_clear()
        self.entry_text_insert(self.track_title)

    @property
    def post_gui_options(self) -> dict:  # Maybe a dictionary?
        """Returns all the meaningful data, names, options from GUI to primary app
        Args: None
        Returns: ??? Dictionary??

        Returned dictionary include the following keys:"""
        self.gui_options = {"track_filename": self.track_filename.get(),
                            "track_title": self.track_title.get(),
                            # "elev_bool": self.elev_bool.get(),
                            }
        for item, value in self.gui_options.keys():
            print(f'{item}: {value}')
        return self.gui_options

    def update_title(self):
        self.track_title = self.get_entry()
        print(self.track_title)  # DELETE


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
        self._gui = ControlGUI()
        # self.reset()

    def reset(self) -> None:
        self._gui = None
        # self._gui = ControlGUI()

    @property
    def gui(self) -> ControlGUI:
        """Retrieve the built ControlGUI() object"""
        gui = self._gui
        self.reset()
        return gui

    def pack_frm_input(self) -> None:
        # Initialize Frame for file input widgets
        self._gui.frm_input_file = tk.LabelFrame(width=self._gui.MASTERWIDTH)
        # Loading Button Frame
        # self._gui.frm_openf = tk.LabelFrame(master=self._gui.frm_input_file,
        #                                     height=5,
        #                                     width=self._gui.MASTERWIDTH // 2,
        #                                     pady=self._gui.PAD_ALPHA,
        #                                     )
        tk.Button(text="Locate Flysight Track",
                  master=self._gui.frm_input_file,
                  width=25,
                  borderwidth=self._gui.BWIDTH,
                  pady=self._gui.PAD_ALPHA,
                  command=self._gui.get_filename,
                  anchor="center",
                  ).pack()
        # Label the chosen filename, with full path
        filename = self._gui.track_filename or ""
        self._gui.lbl_filename = tk.Label(textvariable=filename,
                                          master=self._gui.frm_input_file,
                                          pady=self._gui.PAD_BETA,
                                          )
        self._gui.lbl_filename.pack()
        # self._gui.frm_openf.pack()
        # EntryText for Track Title Updating
        self._gui.frm_text = tk.Frame(master=self._gui.frm_input_file,
                                      width=self._gui.MASTERWIDTH,
                                      height=20,
                                      padx=self._gui.PAD_ALPHA,
                                      pady=self._gui.PAD_BETA,
                                      )
        self._gui.lbl_name = tk.Label(text="Jump Title:",
                                      master=self._gui.frm_text,
                                      borderwidth=self._gui.BWIDTH,
                                      anchor="w",
                                      )
        self._gui.lbl_name.pack(side=tk.LEFT)  # Move up & DELETE?

        self._gui.ent_title = tk.Entry(master=self._gui.frm_text,
                                       borderwidth=self._gui.BWIDTH,
                                       width=self._gui.MASTERWIDTH // 2,
                                       )  # .insert("Name?", 0)
        self._gui.ent_title.pack(side=tk.LEFT)
        self._gui.frm_text.pack()  # fill=tk.X, side=tk.BOTTOM, expand=True)

        # Text Submit Button Frame
        self._gui.frm_submit_text = tk.Frame(master=self._gui.frm_input_file,
                                             width=self._gui.MASTERWIDTH,
                                             height=10,
                                             pady=self._gui.PAD_BETA,
                                             )
        # self._gui.but_submit = tk.Button(text="Update Title",
        tk.Button(text="Update Title",
                  master=self._gui.frm_submit_text,
                  borderwidth=self._gui.BWIDTH,
                  # width=40,
                  command=self._gui.update_title,
                  ).pack()
        self._gui.frm_submit_text.pack()
        self._gui.frm_input_file.pack()

    def pack_frm_chks(self) -> None:
        pass

    def pack_frm_plot(self) -> None:
        pass

    def pack_frm_exit(self) -> None:
        pass


if __name__ == "__main__":
    builder = ControlGUIBuilder()
    builder.pack_frm_input()
    app = builder.gui
    app.mainloop()

    # Junk ###################################################
    # frm_checks = tk.LabelFrame()
    # elev_bool = tk.BooleanVar()
    # chk_getelev = tk.Checkbutton(text="Include Ground Elevation from USGS",
    #                              master=frm_checks,
    #                              borderwidth=BWIDTH,
    #                              pady=PAD_ALPHA,
    #                              variable=elev_bool,
    #                              # onvalue=True,
    #                              # offvalue=False,
    #                              # command=enable_usgs,
    #                              )
    # chk_getelev.pack()
    # frm_checks.pack()
    #
    # # SpacerV frame
    # # tk.Frame(width=MASTERWIDTH, height=20).pack()
    #
    # # Plot-Button Frame
    # frm_plot = tk.LabelFrame()
    # but_plot = tk.Button(text="Plot Track",
    #                      master=frm_plot,
    #                      borderwidth=BWIDTH,
    #                      width=MASTERWIDTH//3,
    #                      height=2,
    #                      command=post_gui_options,
    #                      )
    # but_plot.pack()
    # frm_plot.pack()
    #
    # # SpacerV frame
    # # tk.Frame(width=MASTERWIDTH, height=20).pack()
    #
    # # Exit/Close Button
    # frm_exit = tk.LabelFrame(height=20, pady=PAD_ALPHA)
    # but_exit = tk.Button(text="Close",
    #                      master=frm_exit,
    #                      borderwidth=BWIDTH,
    #                      command=window.quit,
    #                      )
    # but_exit.pack()
    #
    # frm_exit.pack()  # fill=tk.X, side=tk.BOTTOM, expand=True)
    #
    # window.mainloop()
