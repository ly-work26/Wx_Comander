import ctypes
import wx
from main_frame import MainFrame

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    app = wx.App(False)

    frame = MainFrame()
    frame.Show()

    app.MainLoop()
