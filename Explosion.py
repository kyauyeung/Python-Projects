
from tkinter import *
import math, time, random
from Dot import Dot

class Explosion:
    def __init__(self, canvas, max_radius=80, color="rainbow", active=False, dot_number=100):  # Increased default dot_number
        self.canvas = canvas
        self.color = color
        self.__active = active
        self.dot_number = dot_number
        self.dot_list = []
        self.max_radius = max_radius
        self.gravity = 0.2  # Gravity effect to make dots fall

    def is_active(self):
        return self.__active

    def activate(self, x, y):
        self.x = x
        self.y = y
        self.__active = True
        self.r = 0  # Initial radius
        # Create initial dots to simulate the burst of a firework
        for i in range(self.dot_number):
            angle = 2 * math.pi * i / self.dot_number
            speed = random.uniform(2, 5)  # Random speed for each dot
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            dot = Dot(self.canvas, self.x, self.y, self.color)
            dot.vx = vx
            dot.vy = vy
            self.dot_list.append(dot)

    def deactivate(self):
        self.__active = False
        for dot in self.dot_list:
            self.canvas.delete(dot.myoval)

    def next(self):
        if self.__active:
            for dot in self.dot_list:
                # Apply gravity
                dot.vy += self.gravity
                # Move dot based on velocity
                self.canvas.move(dot.myoval, dot.vx, dot.vy)
                dot.x += dot.vx
                dot.y += dot.vy

                # Fade effect by reducing the size of dots
                current_coords = self.canvas.coords(dot.myoval)
                if current_coords[2] - current_coords[0] > 0.5:  # Ensure the dot size does not go to zero immediately
                    new_size = (current_coords[2] - current_coords[0]) * 0.95  # Reduce size by 5%
                    new_coords = (current_coords[0], current_coords[1], current_coords[0] + new_size, current_coords[1] + new_size)
                    self.canvas.coords(dot.myoval, new_coords)

            if len(self.dot_list) == 0 or all(current_coords[2] - current_coords[0] <= 0.5 for dot in self.dot_list):
                self.deactivate()

    @staticmethod
    def add_explosion(canvas, booms, x, y, max_radius=80, color="rainbow"):
        new_explosion = Explosion(canvas, max_radius=max_radius, color=color, dot_number=200)  # Increase dot number here
        booms.append(new_explosion)
        new_explosion.activate(x, y)

def main():
    root = Tk()
    w, h = 800, 1000
    canvas = Canvas(root, width=w, height=h, bg="black")
    canvas.pack()
    root.update()

    booms = []
    root.bind("<Button-1>", lambda e: Explosion.add_explosion(canvas, booms, e.x, e.y))

    while True:
        for boom in booms[:]:  # Iterate over a copy of the list
            boom.next()
            if not boom.is_active():
                booms.remove(boom)
        root.update()
        time.sleep(0.03)

    root.mainloop()

if __name__ == "__main__":
    main()
