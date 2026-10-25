import os
import shutil
import platform
import wx
from files_panel import FilePanel

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="wxCommander", size=(1000, 600))

        # Главный контейнер
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Горизонтальный сплиттер для двух панелей
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        # Стартовые директории
        start_dir = os.path.expanduser("~")

        self.left_panel = FilePanel(splitter, start_dir)
        self.right_panel = FilePanel(splitter, start_dir)

        # Разделяем окно пополам (500 пикселей)
        splitter.SplitVertically(self.left_panel, self.right_panel, 500)
        splitter.SetMinimumPaneSize(200)

        main_sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        # Настройка горячих клавиш (F-кнопки)
        # self.setup_shortcuts()

        # Отслеживаем, какая панель была активна последней
        self.active_panel = self.left_panel
        self.left_panel.list_ctrl.Bind(wx.EVT_SET_FOCUS, self.set_left_active)
        self.right_panel.list_ctrl.Bind(wx.EVT_SET_FOCUS, self.set_right_active)

        self.Center()

    def set_left_active(self, event):
        self.active_panel = self.left_panel
        event.Skip()

    def set_right_active(self, event):
        self.active_panel = self.right_panel
        event.Skip()

    def get_source_and_target(self):
        """Определяет активную панель (источник) и пассивную (приемник)."""
        if self.active_panel == self.left_panel:
            return self.left_panel, self.right_panel
        else:
            return self.right_panel, self.left_panel

    # def setup_shortcuts(self):
    #     """Привязывает клавиши F5-F8 к операциям."""
    #     accel_entries = [
    #         wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F5, 5001),
    #         wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F6, 5002),
    #         wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F7, 5003),
    #         wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F8, 5004),
    #     ]
    #     table = wx.AcceleratorTable(accel_entries)
    #     self.SetAcceleratorTable(table)
    #
    #     self.Bind(wx.EVT_MENU, self.on_copy, id=5001)
    #     self.Bind(wx.EVT_MENU, self.on_move, id=5002)
    #     self.Bind(wx.EVT_MENU, self.on_make_dir, id=5003)
    #     self.Bind(wx.EVT_MENU, self.on_delete, id=5004)
    #
    # # --- Операции с файлами ---
    #
    # def on_copy(self, event):
    #     src_panel, tgt_panel = self.get_source_and_target()
    #     name, src_path = src_panel.get_selected_file()
    #
    #     if not src_path:
    #         return
    #
    #     tgt_path = os.path.join(tgt_panel.current_dir, name)
    #
    #     if os.path.exists(tgt_path):
    #         dial = wx.MessageDialog(
    #             self,
    #             f"Файл {name} уже существует. Заменить?",
    #             "Внимание",
    #             wx.YES_NO | wx.ICON_QUESTION,
    #         )
    #         if dial.ShowModal() != wx.ID_YES:
    #             return
    #
    #     try:
    #         if os.path.isdir(src_path):
    #             shutil.copytree(src_path, tgt_path)
    #         else:
    #             shutil.copy2(src_path, tgt_path)
    #         tgt_panel.refresh_list()
    #     except Exception as e:
    #         wx.MessageBox(
    #             f"Ошибка копирования: {e}", "Ошибка", wx.OK | wx.ICON_ERROR
    #         )
    #
    # def on_move(self, event):
    #     src_panel, tgt_panel = self.get_source_and_target()
    #     name, src_path = src_panel.get_selected_file()
    #
    #     if not src_path:
    #         return
    #
    #     tgt_path = os.path.join(tgt_panel.current_dir, name)
    #
    #     try:
    #         shutil.move(src_path, tgt_path)
    #         src_panel.refresh_list()
    #         tgt_panel.refresh_list()
    #     except Exception as e:
    #         wx.MessageBox(
    #             f"Ошибка перемещения: {e}", "Ошибка", wx.OK | wx.ICON_ERROR
    #         )
    #
    # def on_make_dir(self, event):
    #     panel, _ = self.get_source_and_target()
    #
    #     dialog = wx.TextEntryDialog(self, "Введите имя новой папки:", "Новая папка")
    #     if dialog.ShowModal() == wx.ID_OK:
    #         new_dir_name = dialog.GetValue()
    #         if new_dir_name:
    #             new_dir_path = os.path.join(panel.current_dir, new_dir_name)
    #             try:
    #                 os.makedirs(new_dir_path, exist_ok=True)
    #                 panel.refresh_list()
    #             except Exception as e:
    #                 wx.MessageBox(
    #                 f"Не удалось создать папку: {e}",
    #                 "Ошибка",
    #                 wx.OK | wx.ICON_ERROR,
    #                 )
    #     dialog.Destroy()
    #
    # def on_delete(self, event):
    #     panel, _ = self.get_source_and_target()
    #
    #     name, path = panel.get_selected_file()
    #     if not path:
    #         return
    #     dial = wx.MessageDialog(
    #         self,
    #         f"Вы уверены, что хотите удалить '{name}'?",
    #         "Подтверждение удаления",
    #         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
    #     )
    #     if dial.ShowModal() == wx.ID_YES:
    #         try:
    #             if os.path.isdir(path):
    #                 shutil.rmtree(path)
    #             else:
    #                 os.remove(path)
    #             panel.refresh_list()
    #         except Exception as e:
    #             wx.MessageBox(f"Ошибка удаления: {e}", "Ошибка", wx.OK | wx.ICON_ERROR)