from tkinter import *
import time,random

class Missile:

       #### to complete
    
    def __init__(self, canvas, c_height=0, p_increment = 5, color = "orange", m_width = 4, m_height = 18, active = False):

        self.canvas = canvas 
        self.c_height = c_height
        self.p_increment = p_increment
        self.color = color              #Defines all attributes in the constructor 
        self.m_width = m_width 
        self.m_height = m_height 
        self.__active = active

    def activate(self, x,y):   #Creates new attributes x and y
        self.__active = True  #Private variable is set to true 
        self.x = x 
        self.y = y
        self.missile = self.canvas.create_rectangle(x,y,x+self.m_width,y-self.m_height,fill=self.color)  #Uses the x and y arguments to create a new rectangle that serves as a  missile 
        
    def deactivate(self): #Deactivate method 
        self.__active = False      #Here private variable is set to False
        self.canvas.delete(self.missile)    #In this case, when private variable is set to false, then method delete is used to delete a rectangle(missile) in the canvas 

    def is_active(self): #Supposed to return boolean value of private variable
        return self.__active   #Make active a new private variable

    def next(self): 
        self.__active = True   #This returns the active status of the new missile at the time it is active

        if self.__active:           #If the active status of private variable is set to True 
                self.canvas.move(self.missile,0,-self.p_increment)  #Then the rectangle(missile) is moved up by increment of value of p_increment defined in constructor 
                self.y = self.y - self.p_increment  #Here the y value is reset to a new y value after each increment

        if self.y - self.m_height < self.c_height:    #If the new y value is less than the max height (Less than because it is in tkinter format and 0 is the highest point on the canvas, therefore y value decreases as missile moves up canvas) 
                self.deactivate()                #then deactivate is called

    @staticmethod
    def add_missile(canvas, missiles, x, y, p_increment=5, c_height=0, color= "orange" ): #Defines method add_missile using static method

        for missile in missiles:
            if missile.is_active() == False:
                missiles.pop(missiles.index(missile))
        new_missile = Missile(canvas,p_increment = p_increment, c_height = c_height, color = color ) #New missile is instantiated as an instance of class Missile 
        new_missile.activate(x,y)   #New missile is now activated using the activate method
        missiles = missiles.append(new_missile) #List of missiles in main method is redefined as the list appending values of new_missile
    


###################################################
###################################################

        
def main(): 
       
        ##### create a window, canvas and ball object
        root = Tk() # instantiate a tkinter window
        w,h=800,1000
        canvas = Canvas(root, width=w,height=h,bg="black") # create a canvas width*height
        
        canvas.pack()
        root.update()   # update the graphic (if not cannot capture w and h for canvas if needed)

        #Initialize list of Missiles
        missiles=[]
        
        
        
        ############################################
        ####### start simulation
        ############################################
        t=0                # initialize time clock       
        while True:

            for M in missiles:  #For objects M in list of missiles 
                    M.next()   #M.next which calls next method for each object in list

            if t%50 == 0:      #If t is divisble by 50 (because t increments by 1 and missile must be launched every .5 seconds) then...
                x = random.randint(0,w)    #x is defined as a random value from 0 to width and this sets a random x position for each missile (rectangle)
                y = h                       #y value is set to bottom of canvas as every missile starts at bottom of canvas 
                colors = ["blue", "yellow", "green", "purple", "red", "orange"]    #colors is instantiated as a list of these colors
                p_increment = random.randint(2,7)       #increment speed is set to a random value between 2 and 7 which determines the speed of each missile
                color = random.choice(colors)        #color is set as a random choice of the list of colors 
                c_height = random.randint(0,h)            #The height that each missile can reach is a randomly generated value from 0 to the max height of the campus 
                Missile.add_missile(canvas, missiles, x,y,p_increment, c_height, color)    #Call nmethod add_missile of the class MIssile using all these values


           ##### To complete

            # check active status of list of booms (for debugging)
            for m in missiles:
                print(m.is_active(),end=" ")
            print()
            
            # update the graphic and wait time        
            root.update()   # update the graphic (redraw)
            time.sleep(0.01)  # wait 0.01 second  
            t=t+1      # increment time
       
        root.mainloop() # wait until the window is closed
        
if __name__=="__main__":
    main()

