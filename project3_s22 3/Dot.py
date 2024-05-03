########################


from tkinter import *
import random


class Dot:
    ##### TO COMPLETE
    def __init__(self,canvas,x,y,color, display=False):   #Constructor for all attributes in class Dot
        self.canvas = canvas    
        self.x = x        
        self.y = y
        self.color = color
        self.display = display

        if self.color == "rainbow":  #If attribute self.color is set to "rainbow in program then..."
                colors = ["red", "green", "blue", "yellow", "white", "orange", "purple"] #Create list of colors
                color = random.choice(colors) #And redefine color attribute as a random color from list colors

        if display == True:  #If display attribute is True in main program:
            print(self.x ,self.y, color)  #Prints display of x coordinate, y coordinate, and random color generated

        self.myoval = canvas.create_oval(self.x-1,self.y-1,self.x+1,self.y+1,outline=color)  #Creates oval as "dot" in main program with the outlined color set to randomly generated color





        
#################################################################
#################################################################
    
def main(): 

        ##### create a window, canvas
        root = Tk() # instantiate a tkinter window
        canvas = Canvas(root,width=800,height=1000,bg="black") # create a canvas width*height
        canvas.pack()
        root.update()   # update the graphic
        
        
        # Tkinter binding action (mouse click)
        root.bind("<Button-1>",lambda e:Dot(canvas,e.x,e.y,"rainbow",True))
        
        root.mainloop() # wait until the window is closed
        

if __name__=="__main__":
    main()

