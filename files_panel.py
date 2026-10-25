import os
import shutil
import platform
import wx


class FilePanel(wx.Panel):
    """Класс для одной панели файлового менеджера."""

    def __init__(self, parent, initial_dir):
        super().__init__(parent)
        self.current_dir = os.path.abspath(initial_dir)

        # Главный вертикальный лейаут для панели
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Верхняя строка: Выбор диска (для Windows) и строка пути
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if platform.system() == "Windows":
            self.drive_choice = wx.Choice(self, choices=self.get_windows_drives())
            self.drive_choice.SetStringSelection(self.current_dir[:3])
            self.drive_choice.Bind(wx.EVT_CHOICE, self.on_drive_change)
            top_sizer.Add(self.drive_choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.path_text = wx.TextCtrl(self, style=wx.TE_READONLY)
        top_sizer.Add(self.path_text, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(top_sizer, 0, wx.EXPAND)

        # Список файлов (Аналог таблицы в Total Commander)
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Имя", width=180)
        self.list_ctrl.InsertColumn(1, "Размер", width=80, format=wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(2, "Дата изменения", width=130)

        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        # Привязка событий
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)

        # Обновляем содержимое
        self.refresh_list()

    def get_windows_drives(self):
        """Получает список доступных дисков в системе Windows."""
        drives = []
        for r in range(65, 91):
            drive = f"{chr(r)}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives

    def on_drive_change(self, event):
        """Переключение диска."""
        drive = self.drive_choice.GetStringSelection()
        if os.path.exists(drive):
            self.current_dir = drive
            self.refresh_list()

    def refresh_list(self):
        """Обновляет список файлов и папок в текущей директории."""
        self.list_ctrl.DeleteAllItems()
        self.path_text.SetValue(self.current_dir)

        if platform.system() == "Windows" and hasattr(self, "drive_choice"):
            self.drive_choice.SetStringSelection(self.current_dir[:3])

        try:
            items = os.listdir(self.current_dir)
        except PermissionError:
            wx.MessageBox(
                "Нет доступа к этой папке", "Ошибка", wx.OK | wx.ICON_ERROR
            )
            # Возвращаемся на шаг назад, если это возможно
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir != self.current_dir:
                self.current_dir = parent_dir
                self.refresh_list()
            return

        # Добавляем строку перехода на уровень вверх [..]
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:
            index = self.list_ctrl.InsertItem(0, "..")
            self.list_ctrl.SetItem(index, 1, "<ВВЕРХ>")

        # Разделяем на папки и файлы для удобной сортировки (сначала папки)
        dirs_list = []
        files_list = []

        for item in items:
            full_path = os.path.join(self.current_dir, item)
            try:
                stat = os.stat(full_path)
                mtime = wx.DateTime()
                mtime.SetTimeT(int(stat.st_mtime))
                date_str = mtime.Format("%d.%m.%Y %H:%M")

                if os.path.isdir(full_path):
                    dirs_list.append((item, "<ПАПКА>", date_str))
                else:
                    size_kb = f"{max(1, stat.st_size // 1024)} KB"
                    files_list.append((item, size_kb, date_str))
            except Exception:
                continue

        # Сортируем по имени
        dirs_list.sort(key=lambda x: x[0].lower())
        files_list.sort(key=lambda x: x[0].lower())

        # Выводим в ListCtrl
        for name, size, date in dirs_list + files_list:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), name)
            self.list_ctrl.SetItem(index, 1, size)
            self.list_ctrl.SetItem(index, 2, date)

    def on_item_activated(self, event):
        """Обработка двойного клика или Enter на элементе."""
        selected_item = event.GetText()

        if selected_item == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            target_path = os.path.join(self.current_dir, selected_item)
            if os.path.isdir(target_path):
                self.current_dir = target_path
            else:
                # Если это файл — пытаемся открыть его системным приложением
                try:
                    os.startfile(target_path)  # Windows
                except AttributeError:
                    import subprocess

                    opener = (
                        "open" if platform.system() == "Darwin" else "xdg-open"
                    )
                    subprocess.call([opener, target_path])

        self.refresh_list()

    def get_selected_file(self):
        """Возвращает имя выделенного файла/папки и полный путь."""
        selected_index = self.list_ctrl.GetNextItem(
            -1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED
        )
        if selected_index == -1:
            return None, None
        name = self.list_ctrl.GetItemText(selected_index)
        if name == "..":
            return None, None
        return name, os.path.join(self.current_dir, name)