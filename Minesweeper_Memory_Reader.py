import tkinter as tk
import psutil
import ctypes
import ctypes.wintypes
from enum import Enum
from tkinter import messagebox

SYMBOLS_MAP = {'@':' ', 'A':'1','B':'2','C':'3','D':'4','E':'5','F':'6','G':'7','H':'8',"x0f" : 'x', "x8f":'o', 'x0e':'f', 'x8e':'C','r':'?'}
FORMATTING_CHARS = set(['b',"'", '\\'])
COLOR_MAP = {'x':'gray', ' ':'dimgray', '1':'lightskyblue','2':'palegreen','3':'lightcoral','4':'dodgerblue','5':'firebrick','6':'mediumturquoise','7':'rosybrown','8':'chocolate','?':'khaki', 'C':'green', 'f':'red', 'o':'violet'}
difficulty = None
SIZE = []
#what to do with mixed 
class Difficulty(Enum):
    BEGINNER = 0
    INTERMEDIATE = 1
    EXPERT = 2
    CUSTOM = 3


def get_Size_by_difficulty():
    global difficulty
    if difficulty == Difficulty.BEGINNER:
        return [9,9]
    elif difficulty == Difficulty.INTERMEDIATE:
        return [16,16]
    elif difficulty == Difficulty.EXPERT:
        return [30,16]
    elif difficulty == Difficulty.CUSTOM:
        return SIZE
def get_proc_id():
    program_name = "winmine.exe"
    # Iterate over all running processes and check their names
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == program_name:
        # If the process name matches, return its PID
            print(f"The PID of {program_name} is {proc.info['pid']}")
            return proc.info['pid']
    print(f"No running process with the name '{program_name}' was found.")

def get_process_handle(pid):
    PROCESS_ALL_ACCESS = 0x1F0FFF
    return ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

def read_memory(process_handle, address, size):
    buffer = ctypes.create_string_buffer(size)
    bytesRead = ctypes.c_size_t(0)
    
    if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, size, ctypes.byref(bytesRead)):
        raise ctypes.WinError()
    
    return buffer.raw

procID = get_proc_id()
x = 5
y = 5
def get_table():
    global procID
    data = []
    address = 0x1005361
    size = get_Size_by_difficulty()  
  
    # Get a handle to the process
    process_handle = get_process_handle(procID)
    if not process_handle:
        messagebox.showerror("Failed to get process handle","Failed to get process handle")
        raise Exception("Failed to get process handle")
    try:
        for i in range(0,size[1]):
            
                # Read memory from the specified address
                
            data_at_adr = read_memory(process_handle, address+int(i*32), size[0])
            temp = [] 
            
            curStr = ""
            for val in str(data_at_adr):   
                #val = val.replace("'","") 
                
                if val in FORMATTING_CHARS:
                    pass      
                else :
                    curStr+= val
                    if curStr in SYMBOLS_MAP.keys():
                        temp.append(SYMBOLS_MAP[curStr])
                        curStr = ""
            data.append(temp)
    except Exception as e:
        print(e)
    finally:
        ctypes.windll.kernel32.CloseHandle(process_handle)
        #print(data)
        return data



def difficulty_selection():
    selection_root = tk.Tk()
    selection_root.geometry("300x150")
    selection_root.title("Select Difficulty")

    def confirm_selection():
        global difficulty
        selected = var.get()
        selection_root.destroy()
        if selected == "Custom":
            rows = tk.simpledialog.askinteger("Input", "Number of rows:", minvalue=1)
            cols = tk.simpledialog.askinteger("Input", "Number of columns:", minvalue=1)
            global SIZE
            SIZE = [cols,rows]
            difficulty = Difficulty.CUSTOM
        elif selected == "Beginner":
            difficulty = Difficulty.BEGINNER
        elif selected == "Intermediate":
            difficulty = Difficulty.INTERMEDIATE
        elif selected == "Expert":
            difficulty = Difficulty.EXPERT

    var = tk.StringVar(value="Beginner")

    beginner_rb = tk.Radiobutton(selection_root, text="Beginner", variable=var, value="Beginner")
    intermediate_rb = tk.Radiobutton(selection_root, text="Intermediate", variable=var, value="Intermediate")
    expert_rb = tk.Radiobutton(selection_root, text="Expert", variable=var, value="Expert")
    custom_rb = tk.Radiobutton(selection_root, text="Custom", variable=var, value="Custom")

    beginner_rb.pack(anchor='w')
    intermediate_rb.pack(anchor='w')
    expert_rb.pack(anchor='w')
    custom_rb.pack(anchor='w')

    confirm_button = tk.Button(selection_root, text="Confirm", command=confirm_selection)
    confirm_button.pack()

    selection_root.mainloop()

# Run the difficulty selection window
difficulty_selection()

if difficulty != None :
    root = tk.Tk()
    root.title("Minesweeper Memory Reader")
    grid_frame = tk.Frame(root)
    grid_frame.pack()

    def draw_grid():
        for widget in grid_frame.winfo_children():
            widget.destroy()
        for i,row in enumerate(board):
            for j,column in enumerate(row):
                color = COLOR_MAP[board[i][j]]
            
                L = tk.Label(grid_frame,text='  '+board[i][j]+'  ',bg=color)
                L.grid(row=i,column=j)
    def onclick():
        global board
        board = get_table()
        draw_grid()
    board = get_table()
    draw_grid()
    button_frame = tk.Frame(root)
    button_frame.pack()
    button = tk.Button(button_frame, text="Refresh", command=onclick)
    button.pack()
    root.mainloop()

