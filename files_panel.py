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

        # # Верхняя строка: Выбор диска (для Windows) и строка пути
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if platform.system() == "Windows":
            self.drive_choice = wx.Choice(self, choices=self.get_windows_drives())
            self.drive_choice.SetStringSelection(self.current_dir[:3])
            self.drive_choice.Bind(wx.EVT_CHOICE, self.on_drive_change)
            top_sizer.Add(self.drive_choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.path_text = wx.TextCtrl(self, style=wx.TE_READONLY)
        top_sizer.Add(self.path_text, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(top_sizer, 0, wx.EXPAND)

        # Список файлов
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        # Настраиваем шрифты
        sys_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        nerd_font_name = "CaskaydiaCove NF"  # Укажите установленный у вас Nerd Font

        self.nerd_font = wx.Font(
            sys_font.GetPointSize() + 1,  # Сделаем иконку чуть крупнее для наглядности
            wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
            faceName=nerd_font_name
        )

        # Создаем колонки
        scale = self.GetDPIScaleFactor()
        self.list_ctrl.InsertColumn(0, "", width=int(35 * scale))  # Узкая колонка для иконок Nerd Font
        self.list_ctrl.InsertColumn(1, "Имя", width=int(220 * scale))  # Обычный пропорциональный шрифт
        self.list_ctrl.InsertColumn(2, "Размер", width=int(80 * scale), format=wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(3, "Дата изменения", width=int(140 * scale))

        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)

        # Символы Nerd Fonts
        self.icon_dir_parent = "\uf0aa"
        self.icon_dir = "\uf115"
        self.ext_icons = {
            '.zip': "\uf410", '.rar': "\uf410", '.tar': "\uf410", '.gz': "\uf410", '.7z': "\uf410",
            '.exe': "\uf17a", '.bat': "\uf17a", '.sh': "\uf489", '.py': "\uf31f", '.cmd': "\uf489",
            '.txt': "\uf15c", '.md': "\uf48a", '.pdf': "\uf1c1", '.docx': "\uf1c2", '.xlsx': "\uf1c3",
            '.jpg': "\uf1c5", '.jpeg': "\uf1c5", '.png': "\uf1c5", '.gif': "\uf1c5", '.bmp': "\uf1c5",
            '.json': "\ue60b", '.xml': "\ue796", '.html': "\uf13b", '.css': "\uf13c", '.js': "\uf81d"
        }
        self.icon_default_file = "\uf15b"


        # self.list_ctrl.InsertColumn(0, "Имя", width=180)
        # self.list_ctrl.InsertColumn(1, "Размер", width=80, format=wx.LIST_FORMAT_RIGHT)
        # self.list_ctrl.InsertColumn(2, "Дата изменения", width=130)
        #
        # sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # self.SetSizer(sizer)
        #
        # # Привязка событий
        # self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)

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

    def get_file_icon(self, full_path, is_dir, is_parent=False):
        if is_parent: return self.icon_dir_parent
        if is_dir: return self.icon_dir
        _, ext = os.path.splitext(full_path.lower())
        return self.ext_icons.get(ext, self.icon_default_file)

    def refresh_list(self):
        self.list_ctrl.DeleteAllItems()
        self.path_text.SetValue(self.current_dir)

        if platform.system() == "Windows" and hasattr(self, "drive_choice"):
            self.drive_choice.SetStringSelection(self.current_dir[:3])

        try:
            items = os.listdir(self.current_dir)
        except PermissionError:
            wx.MessageBox("Нет доступа к этой папке", "Ошибка", wx.OK | wx.ICON_ERROR)
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir != self.current_dir:
                self.current_dir = parent_dir
                self.refresh_list()
            return

        # Строка перехода Вверх [..]
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:
            icon = self.get_file_icon("", is_dir=True, is_parent=True)
            index = self.list_ctrl.InsertItem(0, icon)
            self.list_ctrl.SetItemFont(index, self.nerd_font)  # Применяем Nerd Font ТОЛЬКО к колонке 0

            self.list_ctrl.SetItem(index, 1, "..")
            self.list_ctrl.SetItem(index, 2, "<ВВЕРХ>")

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
                    dirs_list.append((item, "", True, date_str, full_path))
                else:
                    size_kb = f"{max(1, stat.st_size // 1024)} KB"
                    files_list.append((item, size_kb, False, date_str, full_path))
            except Exception:
                continue

        dirs_list.sort(key=lambda x: x[0].lower())
        files_list.sort(key=lambda x: x[0].lower())

        for name, size, is_dir, date, full_path in dirs_list + files_list:
            row_idx = self.list_ctrl.GetItemCount()
            icon = self.get_file_icon(full_path, is_dir)

            # 1. Вставляем иконку в первую (нулевую) колонку
            index = self.list_ctrl.InsertItem(row_idx, icon)

            # 2. Меняем шрифт конкретно этой ячейки на Nerd Font
            item_obj = self.list_ctrl.GetItem(index, 0)
            item_obj.SetFont(self.nerd_font)
            self.list_ctrl.SetItem(item_obj)

            # 3. Заполняем остальные колонки (они автоматически используют стандартный шрифт)
            self.list_ctrl.SetItem(index, 1, name)
            self.list_ctrl.SetItem(index, 2, size)
            self.list_ctrl.SetItem(index, 3, date)

    def on_item_activated(self, event):
        # Поскольку имя теперь в чистом виде лежит в колонке 1 (индекс 1)
        selected_index = event.GetIndex()
        name = self.list_ctrl.GetItemText(selected_index, 1)

        if name == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            target_path = os.path.join(self.current_dir, name)
            if os.path.isdir(target_path):
                self.current_dir = target_path
            else:
                try:
                    os.startfile(target_path)
                except AttributeError:
                    import subprocess
                    opener = "open" if platform.system() == "Darwin" else "xdg-open"
                    subprocess.call([opener, target_path])
        self.refresh_list()

    def get_selected_file(self):
        selected_index = self.list_ctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if selected_index == -1: return None, None

        # Получаем имя из первой текстовой колонки (индекс 1)
        name = self.list_ctrl.GetItemText(selected_index, 1)
        if name == "..": return None, None
        return name, os.path.join(self.current_dir, name)
