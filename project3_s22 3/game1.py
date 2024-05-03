from tkinter import *
import time
from Explosion import Explosion
from Counter import Counter
from Alien import *


########## global variable
game_over = False


######### Functions
def stop_game(canvas):
    global game_over    #game_over global variable 
    game_over = True       #game_over is set to True 
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2,
                       text="GAME OVER", font=('Courier', 40), fill="red")  # Display "GAME OVER" in red


def shoot(canvas, aliens, booms, ammunition, x, y):
    global game_over  # Reference the global variable to check if the game is over
    if not game_over:  # Process shooting only if the game is not over
        for alien in aliens[:]:  # Use a copy of the list to safely modify it during iteration
            if alien.is_active() and alien.is_shot(x, y):
                ammunition.increment(alien.intrinsic_point)
                alien.deactivate()
                if not alien.is_active():
                    aliens.remove(alien)
                new_explosion = Explosion(canvas, max_radius=30, color=alien.color)
                new_explosion.activate(x, y)
                booms.append(new_explosion)
            elif not alien.is_shot(x, y):
                ammunition.increment(-3)
                new_explosion = Explosion(canvas, max_radius=30, color="white")
                new_explosion.activate(x, y)
                booms.append(new_explosion)



def main():
    ##### create a window, canvas 
    root = Tk()
    my_image = PhotoImage(file="space1.png")
    w, h = my_image.width(), my_image.height()
    canvas = Canvas(root, width=w, height=h, bg="black")
    canvas.create_image(0, 0, anchor=NW, image=my_image)
    canvas.pack()
    root.update()   # update the graphic
    
    # Initialize list of Explosions, Aliens, and Counter
    booms = []
    aliens = []
    ammunition = Counter(canvas, 10)

    ####### Tkinter binding mouse actions
    root.bind("<Button-1>", lambda e: shoot(canvas, aliens, booms, ammunition, e.x, e.y))
    root.bind("<Escape>", lambda e: stop_game(canvas))


    ############################################
    ####### start simulation
    ############################################


    t = 0

    while True:
        if not game_over:  # Only continue game actions if the game is not over
            for alien in aliens:
                alien.next()

            for boom in booms[:]:
                boom.next()
                if not boom.is_active():
                    booms.remove(boom)

            if t % 50 == 0:
                Alien.add_alien(canvas, aliens)

        if ammunition.count <= 0:  # Check ammo and game over status
            stop_game(canvas)

        root.update()
        time.sleep(0.01)
        t += 1

    root.mainloop()

if __name__ == "__main__":
    main()
