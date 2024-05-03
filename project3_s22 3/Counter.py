from tkinter import *

class Counter:    
    def __init__(self, canvas, initial_value=0):    #Constructor method with arguments including the canvas and initial_value of counter (set to 0 by default)
        self.canvas = canvas 
        self.initial_value = initial_value             #Here variables or arguments are instantiated 
        self.count = canvas.create_text(canvas.winfo_width() - 70, 20, text = initial_value, font = ('Courier 25'), fill = "orange") #New variable self.count is instantiated as a create_text method of the canvas using the following arguments
        
    def increment(self,value):    #Increment method is created using only value as an argument 
        self.value = value       #Here value is instantiated
        self.initial_value = self.initial_value + value        #In this method the initial value from the constructor is set to the initial value + the value in the increment method as an input 
        self.canvas.itemconfig(self.count, text = self.initial_value)   #After initial_value is altered method itemconfig of the canvas from the constuctor is called changing the self.count variable from constructor by changing the text to the new initial_value from the line above 
        return self.count      #Here self.count is reset to a new value of the self.count value from the line above 


        

    # to complete

#########################


def main(): 
    root = Tk() # instantiate a tkinter window
    my_image=PhotoImage(file="space2.png")

    w=my_image.width()
    h=my_image.height()
    canvas = Canvas(root, width=w,height=h,bg="black") # create a canvas width*height

    canvas.create_image(0,0,anchor=NW,image=my_image)
    canvas.pack()
    root.update()   # update the graphic (neede to capture w and h for canvas)
    # to complete

    a = Counter(canvas, 10)    #Instantiate object of class Counter with initial value set to 10 

    root.bind("<Left>", lambda e: a.increment(-1))           #Binds left arrow key to the method increment with an increment of -1 changing the current text by -1 

    root.bind("<Right>", lambda e: a.increment(+1))          #Binds right arrow key to the method increment with an increment of 1 changing the current text by 1 


    while True:
        
        root.update()   # update the graphic (redraw)


if __name__=="__main__":
    main()



        
