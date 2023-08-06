# binary search
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

# fibonacci search
def fibonacci_search(arr, target):
    fib1 = 0
    fib2 = 1
    fib = fib1 + fib2
    while fib < len(arr):
        fib1 = fib2
        fib2 = fib
        fib = fib1 + fib2
    while fib > 1:
        if arr[fib // 2 - 1] <= target < arr[fib // 2]:
            fib = fib // 2
        else:
            fib = fib // 2 - 1
    while fib < len(arr) and arr[fib] != target:
        fib += 1
    if fib < len(arr):
        return fib
    return -1

# jump search
def jump_search(arr, target):
    step = len(arr) // 2
    while step > 0:
        if arr[step] == target:
            return step
        elif arr[step] < target:
            step += len(arr) // 2
        else:
            step -= len(arr) // 2
    return -1

#linear search
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# ternary search
def ternary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid1 = (low + high) // 3
        mid2 = (low + high) // 3 * 2
        if arr[mid1] == target:
            return mid1
        elif arr[mid2] == target:
            return mid2
        elif arr[mid1] < target:
            low = mid1 + 1
        elif arr[mid2] < target:
            low = mid2 + 1
        else:
            high = mid1 - 1
    return -1