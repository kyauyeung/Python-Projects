import tkinter as tk
import random
from math import cos, sin, pi
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for development and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FireworksApp:
    def __init__(self, canvas):
        self.canvas = canvas
        self.running = True
    
    def start_fireworks(self):
        if self.running:
            for _ in range(random.randint(1, 3)):  # Random number of fireworks at once
                x = random.randint(50, 750)
                y = random.randint(50, 650)
                self.firework_animation(x, y, num_particles=90)
            self.canvas.after(random.randint(400, 500), self.start_fireworks)
    
    def firework_animation(self, x, y, num_particles=50):
        standard_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'violet', 'white']
        all_colors = standard_colors + ['rainbow']  
        color_choice = random.choice(all_colors)
        particles = []

        if color_choice == 'rainbow':
            # If rainbow, assign each particle a different color from the standard list
            colors = [random.choice(standard_colors) for _ in range(num_particles)]
        else:
            # Otherwise, all particles have the selected color
            colors = [color_choice] * num_particles

        for i in range(num_particles):
            angle = random.uniform(0, 2 * pi)
            speed = random.uniform(3,7)
            vx = speed * cos(angle)
            vy = speed * sin(angle)
            life = random.randint(20, 40)
            particles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'color': colors[i], 'life': life})
        
        def update_particles():
            nonlocal particles
            self.canvas.delete("firework")
            alive_particles = []
            for particle in particles:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.15  # Gravity effect
                particle['life'] -= 1
                if particle['life'] > 0:
                    self.canvas.create_oval(
                        particle['x'] - 2, particle['y'] - 2,
                        particle['x'] + 2, particle['y'] + 2,
                        fill=particle['color'], outline=particle['color'], tags="firework")
                    alive_particles.append(particle)
            particles = alive_particles
            if particles:
                self.canvas.after(30, update_particles)

        update_particles()



def yes_action():
    print("Yes button clicked")
    canvas.delete("all")  # Clear the canvas
    gif_path = resource_path('Valentine.gif')
    gif_image = tk.PhotoImage(file=gif_path)
    canvas.create_image(400, 575, image=gif_image)  # Display the GIF at the center of the canvas
    canvas.image = gif_image  # Keep a reference to avoid garbage collection
    header_text = canvas.create_text(400, 50, text="I choose you too :)", font=('Helvetica', 16, 'bold'))
    fireworks.start_fireworks()


def no_action():
    print("No button clicked")
    update_button_text()
    # Move the "No" button to avoid overlap with the "Yes" button
    while True:
        new_x = random.randint(50, 750)
        new_y = random.randint(150, 650)
        if not overlap_with_yes_button(new_x, new_y):
            break
    canvas.coords(no_button_window, new_x, new_y)

def update_button_text():
    # List of phrases to cycle through
    phrases = ["No", "No again", "Wrong answer", "Try again", "Why not yes?", "Stawppp", "Last chance", "I lied :)", "Bro", "Click yes", "Hehe", "Haha", "Hurry up", "Ok fine", "No", "Gotcha :)"]
    current_phrase_index[0] = (current_phrase_index[0] + 1) % len(phrases)
    new_text = phrases[current_phrase_index[0]]
    no_button.config(text=new_text)

def overlap_with_yes_button(x, y):
    yes_x, yes_y = canvas.coords(yes_button_window)
    buffer = 100  # 100 pixels buffer in all directions
    return (yes_x - buffer < x < yes_x + buffer) and (yes_y - buffer < y < yes_y + buffer)


# Set up the main window and canvas
root = tk.Tk()
root.title("WILL YOU BE MINE? <3")
canvas = tk.Canvas(root, width=800, height=700, bg='black')
canvas.pack()

# Index to track current phrase
current_phrase_index = [0]  # Using a list to maintain a mutable reference

# Initialize the fireworks app with the canvas
fireworks = FireworksApp(canvas)

# Create and place buttons
yes_button = tk.Button(root, text="Yes", command=yes_action)
no_button = tk.Button(root, text="No", command=no_action)
yes_button_window = canvas.create_window(300, 350, window=yes_button)
no_button_window = canvas.create_window(500, 350, window=no_button)

root.mainloop()
