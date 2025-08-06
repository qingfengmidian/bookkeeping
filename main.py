import tkinter as tk
from ui.main_window import RecordBook

def main():
    root = tk.Tk()
    RecordBook(root)
    root.mainloop()

if __name__ == '__main__':
    main()
