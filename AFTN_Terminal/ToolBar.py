from tkinter import Frame, N, W, S, E, Label


class ToolBar(Frame):

    def __init__(self, parent):
        super().__init__(parent, borderwidth=2, relief="groove")
        self.grid(column=0, row=0, sticky=N + E + W + S)

        # For testing / early development, NOTE: this sets the height of the toolbar
        lbl = Label(self, text="Tool Bar - Will be implemented soon", fg='purple', font=("Arial", 16))
        lbl.pack()
