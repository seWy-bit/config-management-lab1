import tkinter as tk
from tkinter import scrolledtext

class ShellEmulator:
    def __init__(self):
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
        
        self.commands = []
        
        self.print_welcome()
        
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
        
    def process_command(self, event):
        input_text = self.input_entry.get()
        self.input_entry.delete(0, 'end')
        
        self.print_output(f"> {input_text}")
        
        command, args = self.parse_command(input_text)
        self.commands.append((command, args))
        
        if command == "exit":
            self.root.quit()
        elif command == "ls":
            self.print_output(f"Команда 'ls' с аргументами: {args}")
        elif command == "cd":
            self.print_output(f"Команда 'cd' с аргументами: {args}")
        elif command == "":
            pass
        else:
            self.print_output(f"Ошибка: неизвестная команда '{command}'")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    emulator = ShellEmulator()
    emulator.run()