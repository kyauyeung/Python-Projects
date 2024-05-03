from tkinter import *
import time,random
from Explosion import Explosion
from Missile import Missile

def main(): 
       
        ##### create a window, canvas 
        root = Tk() # instantiate a tkinter window
        
        my_image=PhotoImage(file="umass_campus.png")
        w=my_image.width()
        h=my_image.height()
        canvas = Canvas(root, width=w,height=h) # create a canvas width*height

        canvas.create_image(10,10,anchor=NW,image=my_image)
        
        canvas.pack()
        root.update()   # update the graphic (if not cannot capture w and h for canvas if needed)

        #Initialize list of Explosions
        booms=[]
        #Initialize list of Missiles
        missiles=[]
        
        ############################################
        ####### start simulation
        ############################################

        t=0                # initialize time clock    

        while True:
            
            if t%50 == 0: #Every .5 seconds 
            
                x = random.randint(10,w)      #x is set to a random number from 10 (starting x coordinate for picture) to the width of the canvas
                y = h           #y is set to the height but in tkinter format that is the bottom
                colors = ["blue", "yellow", "green", "purple", "red", "orange"]   #Colors is instantiated as a list of random colors
                p_increment = random.randint(4,9)    #The increment is set as a random vaalue from 2 to 7
                color = random.choice(colors)   #Color variable is set to a random value from the list of colors
                c_height = random.randint(h//4,3*h//4)  #The new max height for each missile is set to a random number from h//4 to 3*h//4
                Missile.add_missile(canvas, missiles, x,y,p_increment, c_height, color)  #Adds missile from Missile class using all variables from above 
                
            for boom in booms: #For boom in list of booms
                boom.next()    #Call next method for each boom in list

            for M in missiles:  #For missile in list of missiles 
                was_active = M.is_active()  #New variable was_active is set to current active status of each missile in list of missiles
                M.next()  #Call next method for each missile in list of missiles
                if M.is_active() != was_active:           #If the active status of each missile is not equal to was_active (its active_status prior to calling next method) then...
                    explosion_colors = ["rainbow", "blue", "red", "green", "yellow", "rainbow", "orange", "purple", ]   #Explosion colors is set to list of colors
                    explosion_color = random.choice(explosion_colors)   #Explosion color is instantiated as a random choice from list of explosion_colors
                    new_radius = random.randint(100,300)  #new_radius is instantiated as a random integer from 100 to 300
                    Explosion.add_explosion(canvas,booms,M.x,M.c_height, max_radius = new_radius, color = explosion_color)   #Add explosion from class Explosion is called using all variables instantiated above



            root.update()   # update the graphic (redraw)
            time.sleep(0.01)  # wait 0.01 second  
            t=t+1      # increment time
       
        root.mainloop() # wait until the window is closed

        ### To complete
        
if __name__=="__main__":
    main()

