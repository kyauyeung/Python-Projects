import random

def insertion_sort(A):            # Where A is a randomized array 
    for i in range(1, len(A)):
        key = A[i]                 # Makes new varaiable key as index of array
        j = i - 1                   # Sets variable j to value of index - 1
        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]             # Index of array j + 1 is equal to A of index j
            j = j - 1
        A[j + 1] = key      # New index of array is equal to the key 


random_list = [random.randint(50, 1000) for _ in range(10)] # Generate random array
print("Original list:", random_list)     # Prints original list


insertion_sort(random_list) #Sorts original list
print("Sorted list:", random_list)          # Prints new list
