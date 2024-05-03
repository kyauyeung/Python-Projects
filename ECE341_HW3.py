# Kyle Auyeung 
# Created 2/28/2024

# HW 3 SUBMISSION 

# Question 1

# Stack ADT that matches delimiters based on when they enter the stack using variables to determine if they are right delimiters or left
# Then using boolean logic to compare indexes of delimitiers on right and left side

class Stack:
    def __init__(self):
        self.items = []     #items defined as a list

    def push(self, item):
        self.items.append(item)     # Adds argument to list

    def pop(self):
        return self.items.pop()      # Takes out top of the stack

    def peek(self):
        if self is not self.is_empty():         # If the stack is not empty 
            return self.items[-1]               # Return most recent item
        else:
            None                             # Else do nothing

    def is_empty(self):
        return len(self.items) == 0      # If the stack is empty return the length as 0

def is_matched(expression):
    stack = Stack()
    left_delimiters = "({["     
    right_delimiters = ")}]"

    for char in expression:
        if char in left_delimiters:    
            stack.push(char)                   # If theres characters in the variable left_delimiters then push them
        elif char in right_delimiters:         # Case with right delimiters
            if stack.is_empty():
                return False, f"Unmatched {char}, expected {left_delimiters[right_delimiters.index(char)]}"  
            elif left_delimiters.index(stack.pop()) != right_delimiters.index(char):  # If the character of index in the left does not match the character of the index on the right
                return False, f"Mismatched {stack.pop()} and {char}"   # Returns false and gives mismatched characters
    
    if stack.is_empty():
        return True, "Delimiters match correctly"   # If the stack is empty then...
    else:
        return False, f"Unmatched {stack.peek()}, expected {right_delimiters[left_delimiters.index(stack.peek())]}"

# User input for the string to test
expression = input("Enter a string with delimiters to test: ")

result, message = is_matched(expression)     # Results in message being defined as the output of the function is_matched with user input as argument
print(message)

while expression:     # While expression is true
    expression2 = input("Would you like to try more strings? Enter Y or N:  ")
    if expression2 == "Y":
        expression = input("Enter a string with delimiters to test: ")   # Prompts user to do more strings with Y until N is typed
        result, message = is_matched(expression)
        print(message)
        expression2
    elif expression2 == "N":     # When N is typed the loop breaks and says thank you
        print("Thank you")
        break


