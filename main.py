from random import randint
import tkinter as tk
from tkinter import messagebox

from functools import partial

class Minesweeper:

    def __init__(self, width: int, height: int, mines: int):
        self.width: int = width
        self.height: int = height
        self.mines: int = mines
        self.board: str = []            # game board with mines as "*" and numbers representing mines around fields
        self.visible: str = []          # game board visible for player with "?" on unknown fields
        self.prepared: bool = False     # boolean storing information if board is generated (required for always-safe first move)
        for _ in range(self.width * self.height):
            self.board.append(" ")
            self.visible.append("?")
        
    def print(self, hidden: bool = True):

        # function printing game board in console
        # hidden == True => displaying only board visible for players
        # hidden == False => displaying board with positions of all mines

        print(f"╔{'═══╦'*self.width}═══╗")
        print(f"║{'   ║'*(self.width+1)}", end="\n║   ║")

        for i in range(self.width):
            print(f"{self.len3_hex(i)}║", end="")

        print(f"\n║{'   ║'*(self.width+1)}")
        print(f"╠{'═══╬'*self.width}═══╣")

        for h in range(self.height):
            print(f"║{'   ║'*(self.width+1)}")
            print(f"║{self.len3_hex(h)}║", end="")
            for w in range(self.width):
                if hidden:
                    print(f" {self.visible[self.width*h + w]} ║", end="")
                else:
                    print(f" {self.board[self.width*h + w]} ║", end="")
            print(f"\n║{'   ║'*(self.width+1)}")
            if h < self.height-1:
                print(f"╠{'═══╬'*self.width}═══╣")
        print(f"╚{'═══╩'*(self.width)}═══╝")

    def restart(self):

        # restarting board by changing value of prepared to False, creating new empty board and hidding all fields

        self.board: str = []
        self.visible: str = []
        self.prepared: bool = False
        for _ in range(self.width * self.height):
            self.board.append(" ")
            self.visible.append("?")

    def prepare(self, x: int = -1, y: int = -1):

        # creating board
        # if values of x and y are provided, game will ensure that this field is safe

        selected = self.width * y + x
        mines_num = 0
        while mines_num != self.mines:
            coords = randint(0, self.width*self.height-1)
            if self.board[coords] == " " and coords != selected:
                self.board[coords] = "*"
                mines_num += 1
        self.prepared = True
        # creating numbers on fields around mines
        self.enumerate()

    def enumerate(self):

        # this functions goes through entire game board and counts mines around all fields

        cursor = 0
        cur_max = self.width*self.height
        while cursor < cur_max:
            if self.board[cursor] != "*":
                neighbours = 0
                for a in range(-1, 2):
                    for b in range(-1, 2):
                        temp_cursor = cursor + b + self.width * a
                        if temp_cursor < 0:
                            continue
                        if temp_cursor >= cur_max:
                            continue
                        if cursor % self.width == self.width-1 and b == 1:
                            continue
                        if cursor % self.width == 0 and b == -1:
                            continue
                        if self.board[temp_cursor] == "*":
                            neighbours += 1
                if neighbours:
                    self.board[cursor] = str(neighbours)
            cursor += 1

    def show(self, x: int, y: int) -> bool:

        # recursive function showing discovered fields

        if x >= self.width or x < 0:
            return False
        if y >= self.height or y < 0:
            return False

        pos = x + self.width * y
        if self.visible[pos] != "?":
            return False
        self.visible[pos] = self.board[pos]

        if self.visible[pos] == "*":
            return True
        
        if self.visible[pos] == " ":
            for a in range(-1, 2):
                for b in range(-1, 2):
                    self.show(x+a, y+b)
        return False

    def len3_hex(self, num: int) -> str:

        # function generating hex numbers with fixed length

        return ("00" + hex(num)[2:])[-3:]

    def result(self):

        # checking if game is finished

        empty = 0
        if "*" in self.visible:
            return -1
        for i in range(self.width*self.height):
            if self.visible[i] == "?":
                empty += 1
            if empty > self.mines:
                return 0
        return 1



class Game(tk.Tk):

    def __init__(self, x: int, y: int, mines: int):
        super().__init__()
        self.virtual_pixel = tk.PhotoImage(width=30, height=30)
        self.title = "Minesweeper"
        self.buttons: list[tk.Button] = []
        self.last_board = []
        self.game = Minesweeper(x, y, mines)
        self.btns = tk.Frame()
        self.init_buttons()
        self.label = tk.Label(text="Game state: Playing")
        self.top_panel = self.TopPanel()
        self.top_panel.pack()
        self.label.pack()
        self.btns.pack()

    def TopPanel(self):

        def validate(value):
            if not value:
                return True
            try:
                int(value)
                return True
            except:
                return False

        vcmd = (self.register(validate), "%P")

        frame = tk.Frame()
        width = tk.Frame(frame)
        tk.Label(width, text="Width").grid(column=0, row=0)
        height = tk.Frame(frame)
        tk.Label(height, text="Height").grid(column=0, row=0)
        mines = tk.Frame(frame)
        tk.Label(mines, text="Mines").grid(column=0, row=0)
        widthin = tk.Entry(width, vcmd=vcmd, validate="key")
        widthin.grid(column=1, row=0)
        heightin = tk.Entry(height, vcmd=vcmd, validate="key")
        heightin.grid(column=1, row=0)
        minesin = tk.Entry(mines, vcmd=vcmd, validate="key")
        minesin.grid(column=1, row=0)

        widthin.insert(tk.END, "9")
        heightin.insert(tk.END, "9")
        minesin.insert(tk.END, "10")
        width.grid(column=0, row=0)
        height.grid(column=0, row=1)
        mines.grid(column=0, row=2)

        def btn_click():
            try:
                w = int(widthin.get())
                h = int(heightin.get())
                m = int(minesin.get())
                if m > w * h - 1 or w < 5 or h < 5 or m < 5:
                    messagebox.showerror("Invalid parameters", "You can't create game with provided parameters")
                    return
            except:
                w, h, m = 9, 9, 10
            
            self.game = Minesweeper(w, h, m)
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.last_board = []
            self.init_buttons()

        tk.Button(frame, text="Apply", command=btn_click).grid(column=1, row=1)

        return frame

        
    def init_buttons(self):
        x: int = 0
        y: int = 0
        for field in self.game.visible:
            btn = tk.Button(self.btns, text=field,command=partial(self.move, x, y), 
                            bg="#bbbbbb", fg="#000000")
            btn.grid(column=x, row=y)
            x += 1
            if x == self.game.width:
                x = 0
                y += 1
            self.buttons.append(btn)
            self.last_board.append(field)

    def move(self, x, y):
        if not self.game.prepared:
            self.game.prepare(x, y)
        self.game.show(x, y)
        for i in range(len(self.game.visible)):
            if self.game.visible[i] != self.last_board[i]:
                self.buttons[i].configure(text=self.game.visible[i], command=lambda: None, bg="#eeeeee")
                if self.game.visible[i] == "*":
                    self.buttons[i].configure(bg="#ff0000")
        res = self.game.result()
        if res == 1:
            self.label["text"] = "Game state: Victory"
            answer = messagebox.askyesno("You won!", "Do you want to play again?")
        if res == -1:
            self.label["text"] = "Game state: Loss"
            answer = messagebox.askyesno("You lost!", "Do you want to play again?")

        if res:
            if answer:
                self.restart()
            else:
                exit()

    def restart(self):
        self.label["text"] = "Game state: Playing"
        self.game.restart()
        for i in range(len(self.game.visible)):
            self.buttons[i].configure(text=self.game.visible[i], command=partial(self.move, i%self.game.width, i//self.game.width), bg="#bbbbbb")
            
if __name__ == "__main__":
    a = Game(9, 9, 10)
    a.mainloop()