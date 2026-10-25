import wx

from main_frame import MainFrame


class MyWindow(wx.Frame):
    def __init__(self):
        # Создаем главное окно (заголовок и начальный размер)
        super().__init__(parent=None, title="Привет, wxPython!", size=(350, 200))

        # Панель нужна для корректного отображения элементов и фонового цвета
        panel = wx.Panel(self)

        # Вертикальный сайзер для автоматического выравнивания элементов
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Добавляем текстовую надпись (StaticText)
        self.label = wx.StaticText(panel, label="Нажмите кнопку ниже", style=wx.ALIGN_CENTER)
        sizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 15)

        # Добавляем кнопку (Button)
        self.btn = wx.Button(panel, label="Нажми меня")
        sizer.Add(self.btn, 0, wx.ALL | wx.CENTER, 10)

        # Связываем событие клика по кнопке с методом-обработчиком
        self.btn.Bind(wx.EVT_BUTTON, self.on_button_click)

        # Устанавливаем сайзер для панели
        panel.SetSizer(sizer)

        self.Center()

    def on_button_click(self, event):
        # Изменяем текст надписи при клике
        self.label.SetLabel("Кнопка успешно нажата!")


if __name__ == "__main__":
    app = wx.App(False)

    # window = MyWindow()
    # window.Show()

    frame = MainFrame()
    frame.Show()

    app.MainLoop()
