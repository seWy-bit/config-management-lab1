import tkinter as tk
from tkinter import scrolledtext
import argparse
import sys
from datetime import datetime
import csv

class ShellEmulator:
    def __init__(self, log_path=None, script_path=None, vfs_path=None):
        self.log_path = log_path
        self.script_path = script_path
        self.vfs_path = vfs_path
        self.commands = []

        self.root = tk.Tk()
        self.root.title("Эмулятор - MyVFS")
        self.root.configure(bg='black')
        
        self.font = ("DejaVu Sans Mono", 10)
        
        # Область вывода
        self.output_area = scrolledtext.ScrolledText(
            self.root, 
            width=80, 
            height=25, 
            state='disabled',
            bg='black',
            fg='white',
            font=self.font,
            insertbackground='white'
        )
        self.output_area.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Фрейм для ввода команды
        input_frame = tk.Frame(self.root, bg='black')
        input_frame.pack(padx=10, pady=5, fill='x')
        
        tk.Label(input_frame, text=">", bg='black', fg='white', font=self.font).pack(side='left')
        
        self.input_entry = tk.Entry(
            input_frame, 
            width=70,
            bg='black',
            fg='white',
            font=self.font,
            insertbackground='white'
        )
        self.input_entry.pack(side='left', fill='x', expand=True)
        self.input_entry.bind('<Return>', self.process_command)
        
        self.vfs = None
        self.cwd = None
        self.current_path_str = ""

        if self.vfs_path:
            self.load_vfs(self.vfs_path)

        self.print_welcome()
        if self.script_path:
            self.run_script(self.script_path)
    def run_script(self, script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    cmd = line.strip()
                    if not cmd or cmd.startswith('#'):
                        continue
                    self.print_output(f"> {cmd}")
                    command, args = self.parse_command(cmd)
                    result = ""
                    error = False
                    if command == "exit":
                        result = "Выход из эмулятора"
                        self.print_output(result)
                        self.log_event(command, args, result)
                        break
                    elif command == "ls":
                        result = self.ls_vfs()
                        self.print_output(result)
                        self.log_event(command, args, " ".join(result.split()))
                    elif command == "cd":
                        if args:
                            result = self.cd_vfs(args[0])
                        else:
                            result = "Ошибка: не указана директория."
                        self.print_output(result)
                        self.log_event(command, args, result)
                    elif command == "":
                        continue
                    else:
                        result = f"Ошибка: неизвестная команда '{command}'"
                        self.print_output(result)
                        self.log_event(command, args, result)
                        error = True
                    if error:
                        self.print_output("[ОШИБКА] Скрипт остановлен из-за ошибки.")
                        break
        except Exception as e:
            self.print_output(f"[ОШИБКА] Не удалось выполнить скрипт: {e}")
        
    def print_welcome(self):
        self.print_output("Добро пожаловать в эмулятор командной оболочки")
        self.print_output("Доступные команды: ls, cd, exit")
        self.print_output("Введите команду:")
        
    def print_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert('end', text + '\n')
        self.output_area.config(state='disabled')
        self.output_area.see('end')
        
    def parse_command(self, input_text):
        parts = input_text.strip().split()
        if not parts:
            return "", []
        command = parts[0]
        args = parts[1:]
        return command, args
        
    def log_event(self, command, args, result):
        if not self.log_path:
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([now, command, ' '.join(args), result])

    def process_command(self, event):
        input_text = self.input_entry.get()
        self.input_entry.delete(0, 'end')

        self.print_output(f"> {input_text}")

        command, args = self.parse_command(input_text)
        self.commands.append((command, args))

        result = ""
        if command == "exit":
            result = "Выход из эмулятора"
            self.log_event(command, args, result)
            self.root.quit()
        elif command == "ls":
            result = self.ls_vfs()
            self.print_output(result)
            self.log_event(command, args, " ".join(result.split()))
        elif command == "cd":
            if args:
                result = self.cd_vfs(args[0])
            else:
                result = "Ошибка: не указана директория."
            self.print_output(result)
            self.log_event(command, args, result)
        elif command == "":
            pass
        else:
            result = f"Ошибка: неизвестная команда '{command}'"
            self.print_output(result)
            self.log_event(command, args, result)
            
    def run(self):
        self.root.mainloop()

    def load_vfs(self, vfs_path):
        self.vfs = {'/': {}}
        self.cwd = self.vfs['/']
        self.current_path_str = "/"
        try:
            with open(vfs_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    path = row['path']
                    type = row['type']
                    data = row['data']
                    
                    parts = path.split('/')
                    current_level = self.vfs['/']
                    
                    for part in parts[:-1]:
                        if part not in current_level:
                            current_level[part] = {}
                        current_level = current_level[part]
                    
                    if type == 'dir':
                        if parts[-1] not in current_level:
                            current_level[parts[-1]] = {}
                    else:
                        current_level[parts[-1]] = data
            self.print_output(f"VFS загружена из {vfs_path}")
        except Exception as e:
            self.print_output(f"[ОШИБКА] Не удалось загрузить VFS: {e}")
            self.vfs = None

    def get_vfs_node(self, path_list):
        node = self.vfs['/']
        for part in path_list:
            if part in node:
                node = node[part]
            else:
                return None
        return node

    def ls_vfs(self):
        if not self.vfs:
            return "[ОШИБКА] VFS не загружена."
        
        items = []
        for name, content in self.cwd.items():
            if isinstance(content, dict):
                items.append(f"{name}/")
            else:
                items.append(name)
        return "\n".join(items) if items else ""

    def cd_vfs(self, folder):
        if not self.vfs:
            return "[ОШИБКА] VFS не загружена."

        if folder == "..":
            if self.current_path_str != "/":
                path_list = self.current_path_str.strip('/').split('/')
                path_list.pop()
                self.current_path_str = "/" + "/".join(path_list)
                self.cwd = self.get_vfs_node(path_list)
            return f"Текущая директория: {self.current_path_str}"

        
        path_list = self.current_path_str.strip('/').split('/') if self.current_path_str != "/" else []
        
        temp_node = self.get_vfs_node(path_list)

        if folder in temp_node and isinstance(temp_node[folder], dict):
            path_list.append(folder)
            self.current_path_str = "/" + "/".join(path_list)
            self.cwd = self.get_vfs_node(path_list)
            return f"Текущая директория: {self.current_path_str}"
        else:
            return f"Ошибка: директория '{folder}' не найдена."

def main():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки MyVFS")
    parser.add_argument('--vfs', required=True, help='Путь к физическому расположению VFS')
    parser.add_argument('--log', required=True, help='Путь к лог-файлу')
    parser.add_argument('--script', required=True, help='Путь к стартовому скрипту')
    args = parser.parse_args()

    print("[ОТЛАДКА] Параметры запуска эмулятора:")
    print(f"VFS: {args.vfs}")
    print(f"Log: {args.log}")
    print(f"Script: {args.script}")

    emulator = ShellEmulator(vfs_path=args.vfs, log_path=args.log, script_path=args.script)
    emulator.run()

if __name__ == "__main__":
    main()