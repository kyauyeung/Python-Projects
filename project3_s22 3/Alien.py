from tkinter import *
import math
import time, random

class Alien:

    def __init__(self, canvas, p_increment = 4, color = "yellow", a_width = 50, a_height = 50, intrinsic_point = 1, active = False):

        self.canvas = canvas
        self.p_increment = p_increment
        self.color = color        #All attributes are defined here in the constructor for Class Alien 
        self.a_width = a_width
        self.a_height = a_height 
        self.intrinsic_point = intrinsic_point
        self._active = active

    def activate(self,x = None,y = None):   #Define activate method with x and y variables being instantiated and set to none by default  
        self._active = True       #Here self._active (protected variable) is set to true 
        self.x = x       #Arguments are instantiated
        self.y = y
        x = random.randint(0,self.canvas.winfo_width()-self.a_width) #x is set to a random value along x axis starting at 0 and ending at the end of the width of the canvas - the width of the alien, this is so that the alien does not go out of the canvas
        y = 0                                                         #y is set to 0 (tkinter format) so top of the canvas
        self.alien = self.canvas.create_rectangle(x,y,x+self.a_width, y+self.a_height, fill = self.color)  #self.alien is instantiated as a rectangle created in the canvas with dimenisons x,y and then x and y + their width and height 
        self.y = y   #self.y is then currently set to its value in this instant
        self.x = x   #self.x is currently set to its value in this instant

    def is_active(self):   #method is_active is created using self argument
        return self._active   #returns value of protected variable self._active

    def deactivate(self):      #deactivate method using argument self
        self._active = False        #Here private variable is set to False
        self.canvas.delete(self.alien)     #Here in the method the private variable is false and each instance of self.alien when this method is called is deleted

    def next(self):     #next method is created using argument self
        self._active = True       #Here protected variable is set to true 
        if self._active:      #If the protected variable is true then...
            self.canvas.move(self.alien, 0, self.p_increment)   #Move the alien down the canvas by value of p_increment
            self.y = self.y + self.p_increment   #Here self.y has its value reset to sel.y + p_increment, esentially reseting the y value to its current y value while moving for every increment

        if self.y + self.a_height > self.canvas.winfo_height():  #if the bottom of the square (self.y + a_height) ever goes above the canvas height (since in tkinter format y position increases as square moves down)...
            self.deactivate()                                   #then the method deactivate is called and the alien is deleted
        

    def is_shot(self,x0,y0):    #is_shot method is created instantiating new variables x0 and y0
        self.x0 = x0     #Variables are instantiated here
        self.y0 = y0

        self._active = True #Protected variable is set to true here

        if self.x <= x0 <= self.x+self.a_width and self.y <= y0 <= self.y + self.a_height:  #if x0 falls within x parameters of square and y0 falls within y parameters of square then...
            return True  #return value of true
        else: 
            return False #Else return False

    @staticmethod
    def add_alien(canvas, aliens):

        for a in aliens:     #For item in list of aliens
            if a._active == False:              #If protected variable of item in list is false
                aliens.pop(aliens.index(a))     #Delete the index of the list of aliens of that item 
        list_aliens = [Alien_red(canvas), Alien_green(canvas), Alien_blue(canvas)]    #List of aliens is instantiated as list of different types of aliens
        random_alien = random.choice(list_aliens)    #Random alien is instantiated as a random choice from the list of aliens
        aliens = aliens.append(random_alien) #Unbound variable aliens is instantiated as aliens.append(value of random_alien), (aliens will no longer be unbound when called in game1.py file)
        random_alien.activate()   #Call activate method using random_alien variable

        
    
        
    ### to complete
        
################################################################
################################################################

class Alien_red(Alien):
    def __init__(self,canvas):
        self.image=PhotoImage(file="alien_red.png")  # keep a reference (avoid garbage collector)
        width=self.image.width()              #Width is set to the width of the self.image
        height=self.image.height()            #Height is set to the height of the self.image
        super().__init__(canvas, 4, "red", width, height, 2)   #Resets all values inherited from original constructor to new values fit for class Alien_red

    def activate(self):
        self.angle = (random.randint(-120,-20) * math.pi/180)
        self._active = True   #Here protected attribute self._active is set to True
        self.x = random.randint(0+self.a_width,self.canvas.winfo_width()- self.a_width) #x is set to a random value along x axis starting at 0 + width and ending at the end of the width of the canvas - the width of the alien, this is so that the alien does not go out of the canvas
        self.y = 0                                                         #y is set to 0 (tkinter format) so top of the canvas
        self.alien = self.canvas.create_image(self.x + self.a_width/2,self.y+self.a_height/2, anchor = CENTER, image = self.image) #Here red alien is instantiated under self.alien as self.image anchored at the center using self.x + self.a_width/2 and self.y + self.a_height/2 (becauase image is anchored at center) as coordinates


        # contstructor to complete

    # to complete
        
###############################################################
###############################################################

class Alien_green(Alien_red):
    def __init__(self,canvas):
        self.image=PhotoImage(file="alien_green.png")
        width=self.image.width()              #Width is set to the width of the self.image
        height=self.image.height()            #Height is set to the height of the self.image
        Alien.__init__(self, canvas, 4, "green", width, height, 4)

    def next(self): 
        self._active = True 
        if self._active:      #If the protected variable is true then...
            wiggle = random.randint(-5,5) #Here the wiggle variable is instantiated as a random integer between -5 and 5 which will be used as the horizontal movement
            self.canvas.move(self.alien, wiggle, self.p_increment)   #Move the alien down the canvas by value of p_increment and horizontally by random value of wiggle
            self.y = self.y + self.p_increment   #Here self.y has its value reset to sel.y + p_increment, esentially reseting the y value to its current y value while moving for every increment

        if self.y +self.a_height > self.canvas.winfo_height():  #if the bottom of the square (self.y + a_height) ever goes above the canvas height (since in tkinter format y position increases as square moves down)...
            self.deactivate()         #Then call deactivate method         

    # to complete

###############################################################
###############################################################
                
class Alien_blue(Alien_red):
    def __init__(self,canvas):
        self.image=PhotoImage(file="alien_blue.png")
        width=self.image.width()              #Width is set to the width of the self.image
        height=self.image.height()            #Height is set to the height of the self.image
        Alien.__init__(self, canvas, 4, "blue", width, height, 3)   #constructor for class Alien_blue is set to values of p_increment = 4, color = "blue", width, height, and intrinsic_point = 3

    def next(self): 
        self._active = True 
        if self._active:      #If the protected variable is true then...
            self.canvas.move(self.alien, self.p_increment * math.cos(self.angle), self.p_increment * -math.sin(self.angle))   #Move the alien down the canvas by value of p_increment * -sin(self.angle) and horizontally by the p_increment * cos(self.angle) 
            self.y = self.y + (self.p_increment * -math.sin(self.angle))  #self.y is reset to a new self.y value + the self.p_increment * -math.sin(self,angle) for each increment of the alien
            self.x = self.x + (self.p_increment * math.cos(self.angle))   #self.x is reset to a new self.x value + the self.p_increment * math.cos(self,angle) for each increment of the alien

        if self.x + self.a_width >= self.canvas.winfo_width():  #If the current x value + self.a_width is more than or equal to the width of the canvas... (right bound)
            self.angle = math.pi - self.angle     #Then self.angle value changes to math.pi - self.angle
        elif self.x  <= 0:                      #If the current x value is less than or equal to the x starting position (0) of the canvas... (left bound)
            self.angle = (-self.angle - math.pi)      #Then self.angle value changes to -self.angle - math.pi

        if self.y +self.a_height > self.canvas.winfo_height():  #if the bottom of the square (self.y + a_height) ever goes above the canvas height (since in tkinter format y position increases as square moves down)...
            self.deactivate()         #Then call deactivate method  


class Alien_mine(Alien_red):
    def __init__(self,canvas):
        self.image = PhotoImage(file = "Alien_mine.png")
        width = self.image.width()
        height = self.image.height()
        Alien.__init__(self,canvas, 6, "purple", width, height, 4)

    def next(self): 
        self._active = True 
        if self._active:      #If the protected variable is true then...
            self.canvas.move(self.alien, self.p_increment * math.sin(30), self.p_increment * math.cos(30) )   #Move the alien down the canvas by value of p_increment * -sin(self.angle) and horizontally by the p_increment * cos(self.angle) 
            self.y = self.y + (self.p_increment *math.cos(30))  #self.y is reset to a new self.y value + the self.p_increment * -math.sin(self,angle) for each increment of the alien
            self.x = self.x + (self.p_increment * math.cos(30))   #self.x is reset to a new self.x value + the self.p_increment * math.cos(self,angle) for each increment of the alien

        if self.x + self.a_width >= self.canvas.winfo_width():  #If the current x value + self.a_width is more than or equal to the width of the canvas... (right bound)
            self.angle = math.pi - 30    #Then self.angle value changes to math.pi - self.angle
        elif self.x  <= 0:                      #If the current x value is less than or equal to the x starting position (0) of the canvas... (left bound)
            self.angle = (-30 - math.pi)      #Then self.angle value changes to -self.angle - math.pi

        if self.y +self.a_height > self.canvas.winfo_height():  #if the bottom of the square (self.y + a_height) ever goes above the canvas height (since in tkinter format y position increases as square moves down)...
            self.deactivate()         #Then call deactivate method  

    # to complete

###############################################################
################################################################
def shoot(alien,x,y):
    if alien.is_shot(x,y):  #If alien.is_shot(x,y) method is called using alien variable using x and y arguments 
        result="hit!" #Variable result is set to "hit!"
    else:             #In any other case:
        result="miss!"    #Result is set to "miss!"
    print(x,y,result)      #Prints the x and y coordinate as well as the result

def main(): 
        
        ##### create a window, canvas 
        root = Tk() # instantiate a tkinter window
        my_image=PhotoImage(file="space2.png")

        w=my_image.width()
        h=my_image.height()
        canvas = Canvas(root, width=w,height=h,bg="black") # create a canvas width*height

        canvas.create_image(0,0,anchor=NW,image=my_image)
        canvas.pack()
        root.update()   # update the graphic (neede to capture w and h for canvas)
        

        #Initialize alien
        #alien=Alien(canvas)
        #alien=Alien_red(canvas)
        alien=Alien_green(canvas)
        #alien=Alien_blue(canvas)
       # alien = Alien_mine(canvas)

        alien.activate()       #Calls activate method for alien variable 


        ####### Tkinter binding mouse actions
        root.bind("<Button-1>",lambda a:shoot(alien,a.x,a.y))
        
        ############################################
        ####### start simulation
        ############################################
        #t=0               # time clock
        while True:

            if (not alien.is_active()):
                alien.activate()
              
            alien.next() # next time step
                    
            root.update()   # update the graphic (redraw)
            time.sleep(0.01)  # wait 0.01 second (simulation
           
        root.mainloop() # wait until the window is closed
        

if __name__=="__main__":
    main()

