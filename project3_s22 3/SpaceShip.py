from tkinter import *

class SpaceShip:
    def __init__(self, canvas):
        self.canvas = canvas
        self.__active = False
        self.horizontal_shift = 15

    def activate(self):
        self.__active = True
        self.image = PhotoImage(file="ship.png")  # Ensure the ship.png is in the correct directory
        self.width = self.image.width()
        self.height = self.image.height()
        self.x = self.canvas.winfo_width() / 2
        self.y = self.canvas.winfo_height() - self.height / 2
        self.ship = self.canvas.create_image(self.x, self.y, anchor=CENTER, image=self.image)

    def deactivate(self):
        self.__active = False
        self.canvas.delete(self.ship)

    def is_active(self):
        return self.__active

    def shift_left(self):
        if self.x - self.width / 2 > self.horizontal_shift:  # Check if the ship can move left
            self.canvas.move(self.ship, -self.horizontal_shift, 0)
            self.x -= self.horizontal_shift

    def shift_right(self):
        if self.x + self.width / 2 < self.canvas.winfo_width() - self.horizontal_shift:  # Check if the ship can move right
            self.canvas.move(self.ship, self.horizontal_shift, 0)
            self.x += self.horizontal_shift

    
def main():
    root = Tk()  # Instantiate a tkinter window
    my_image = PhotoImage(file="space2.png")  # Ensure the space2.png is in the correct directory
    
    w = my_image.width()
    h = my_image.height()
    canvas = Canvas(root, width=w, height=h)  # Create a canvas width*height
    canvas.create_image(0, 0, anchor=NW, image=my_image)
   
    canvas.pack()
    root.update()  # Update the graphic (if not, cannot capture w and h for canvas)

    # Initialize the ship
    ship = SpaceShip(canvas)
    ship.activate()
    
    # Tkinter binding key actions
    root.bind("<Left>", lambda e: ship.shift_left())
    root.bind("<Right>", lambda e: ship.shift_right())

    root.mainloop()  # Wait until the window is closed
    

if __name__ == "__main__":
    main()
