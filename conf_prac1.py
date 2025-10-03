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
                    elif command == "tree":
                        result = self.tree(args)
                        self.print_output(result)
                        self.log_event(command, args, "tree")
                    elif command == "echo":
                        result = self.echo(args)
                        if result:
                            self.print_output(result)
                        self.log_event(command, args, "echo")
                    elif command == "wc":
                        result = self.wc(args)
                        self.print_output(result)
                        self.log_event(command, args, "wc")
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
        self.print_output("Доступные команды: ls, cd, tree, echo, wc, exit")
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
        elif command == "tree":
            result = self.tree(args)
            self.print_output(result)
            self.log_event(command, args, "tree")
        elif command == "echo":
            result = self.echo(args)
            if result:
                self.print_output(result)
            self.log_event(command, args, "echo")
        elif command == "wc":
            result = self.wc(args)
            self.print_output(result)
            self.log_event(command, args, "wc")
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
                    raw_path = (row.get('path') or '').strip()
                    if raw_path == '':
                        continue
                    path = raw_path.strip('/')
                    type_ = (row.get('type') or '').strip().lower()
                    data = row.get('data') or ''
                    if path == '':
                        if type_ != 'dir':
                            continue
                        continue
                    parts = path.split('/')
                    current_level = self.vfs['/']
                    for part in parts[:-1]:
                        if part not in current_level or not isinstance(current_level[part], dict):
                            current_level[part] = {}
                        current_level = current_level[part]
                    last = parts[-1]
                    if type_ == 'dir':
                        current_level.setdefault(last, {})
                    else:
                        current_level[last] = data
            self.print_output(f"VFS загружена из {vfs_path}")
        except Exception as e:
            self.print_output(f"[ОШИБКА] Не удалось загрузить VFS: {e}")
            self.vfs = None

    def get_vfs_node(self, path_list):
        node = self.vfs['/']
        if not path_list:
            return node
        for part in path_list:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return None
        return node
    
    def resolve_node_from_path(self, path):
        if not path or path == "":
            return self.cwd
        if path.startswith('/'):
            parts = [p for p in path.strip('/').split('/') if p]
            if not parts:
                return self.vfs['/']
            return self.get_vfs_node(parts)
        parts = [p for p in self.current_path_str.strip('/').split('/') if p] if self.current_path_str != "/" else []
        node = self.get_vfs_node(parts) if parts else self.vfs['/']
        for comp in [p for p in path.split('/') if p]:
            if comp == ".":
                continue
            if comp == "..":
                if parts:
                    parts.pop()
                    node = self.get_vfs_node(parts) if parts else self.vfs['/']
                else:
                    node = self.vfs['/']
                continue
            if not isinstance(node, dict) or comp not in node:
                return None
            node = node[comp]
            parts.append(comp)
        return node
    
    def tree(self, args):
        path = args[0] if args else ""
        node = self.resolve_node_from_path(path)
        if node is None:
            return f"Ошибка: путь '{path}' не найден."
        lines = []
        def walk(n, prefix=""):
            if not isinstance(n, dict):
                lines.append(prefix + "- " + str(n))
                return
            items = sorted(n.items())
            for i, (k, v) in enumerate(items):
                connector = "└── " if i == len(items)-1 else "├── "
                if isinstance(v, dict):
                    lines.append(prefix + connector + k + "/")
                    ext = "    " if i == len(items)-1 else "│   "
                    walk(v, prefix + ext)
                else:
                    lines.append(prefix + connector + k)
        base = path.rstrip('/') if path and path != "/" else "/"
        lines.append(base)
        walk(node)
        return "\n".join(lines)

    def echo(self, args):
        if not args:
            return ""
        if len(args) >= 3 and args[-2] == '>':
            text = " ".join(args[:-2])
            dest = args[-1]
            if not dest.startswith('/'):
                parts = [p for p in self.current_path_str.strip('/').split('/') if p] if self.current_path_str != "/" else []
                node = self.get_vfs_node(parts)
                if node is None:
                    return f"Ошибка: текущая директория недоступна."
                node[dest] = text
                return ""
            parts = [p for p in dest.strip('/').split('/') if p]
            cur = self.vfs['/']
            for part in parts[:-1]:
                cur = cur.setdefault(part, {})
            cur[parts[-1]] = text
            return ""
        return " ".join(args)

    def wc(self, args):
        if not args:
            return "0 0 0"
        target = args[0]
        data = None
        node = self.resolve_node_from_path(target)
        if node is None:
            data = " ".join(args)
        else:
            if isinstance(node, dict):
                return f"wc: {target}: это директория"
            data = node
        lines = data.count('\n') + (1 if data and not data.endswith('\n') else 0)
        words = len(data.split())
        bytes_len = len(data.encode('utf-8'))
        return f"{lines} {words} {bytes_len}"


    def ls_vfs(self):
        if not self.vfs:
            return "[ОШИБКА] VFS не загружена."
        if self.cwd is None:
            return "[ОШИБКА] Текущая директория не установлена."
        items = []
        for name, content in self.cwd.items():
            if isinstance(content, dict):
                items.append(f"{name}/")
            else:
                items.append(name)
        return "\n".join(items) if items else "(пусто)"

    def cd_vfs(self, folder):
        if not self.vfs:
            return "[ОШИБКА] VFS не загружена."
        if folder is None or folder == "" or folder == "/":
            self.current_path_str = "/"
            self.cwd = self.vfs['/']
            return f"Текущая директория: {self.current_path_str}"
        if folder == "..":
            if self.current_path_str == "/" or self.current_path_str == "":
                self.current_path_str = "/"
                self.cwd = self.vfs['/']
                return f"Текущая директория: {self.current_path_str}"
            parts = [p for p in self.current_path_str.strip('/').split('/') if p]
            parts.pop()
            if parts:
                self.current_path_str = "/" + "/".join(parts)
                self.cwd = self.get_vfs_node(parts)
            else:
                self.current_path_str = "/"
                self.cwd = self.vfs['/']
            return f"Текущая директория: {self.current_path_str}"
        if folder.startswith('/'):
            parts = [p for p in folder.strip('/').split('/') if p]
            node = self.get_vfs_node(parts) if parts else self.vfs['/']
            if node is None:
                return f"Ошибка: директория '{folder}' не найдена."
            if not isinstance(node, dict):
                return f"Ошибка: '{folder}' не является директорией."
            self.current_path_str = "/" + "/".join(parts) if parts else "/"
            self.cwd = node
            return f"Текущая директория: {self.current_path_str}"
        parts = [p for p in self.current_path_str.strip('/').split('/') if p] if self.current_path_str != "/" else []
        node = self.get_vfs_node(parts)
        for comp in [p for p in folder.split('/') if p]:
            if comp == ".":
                continue
            if comp == "..":
                if parts:
                    parts.pop()
                    node = self.get_vfs_node(parts) if parts else self.vfs['/']
                else:
                    node = self.vfs['/']
                continue
            if not isinstance(node, dict) or comp not in node:
                return f"Ошибка: директория '{folder}' не найдена."
            node = node[comp]
            parts.append(comp)
        if not isinstance(node, dict):
            return f"Ошибка: '{folder}' не является директорией."
        self.current_path_str = "/" + "/".join(parts) if parts else "/"
        self.cwd = node
        return f"Текущая директория: {self.current_path_str}"

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