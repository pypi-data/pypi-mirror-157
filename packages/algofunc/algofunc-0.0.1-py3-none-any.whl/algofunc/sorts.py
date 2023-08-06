# bitonic sort function: time complexity: O(n log^2 n)
def bitonic_sort(list):
    if len(list) <= 1:
        return list
    mid = len(list) // 2
    left = bitonic_sort(list[:mid])
    right = bitonic_sort(list[mid:])
    return merge(left, right)

# bubble sort function: time complexity: O(n^2)
def bubble_sort(list):
    for i in range(len(list)):
        for j in range(len(list) - 1):
            if list[j] > list[j + 1]:
                list[j], list[j + 1] = list[j + 1], list[j]
    return list

#bucket sort function: time complexity: O(n^2)
def bucket_sort(list):
    max_value = max(list)
    size = max_value / len(list)

    buckets_list = []
    for x in range(len(list)):
        buckets_list.append([])

    for i in range(len(list)):
        j = int(list[i] / size)
        if j != len(list):
            buckets_list[j].append(list[i])
        else:
            buckets_list[len(list) - 1].append(list[i])
    for z in range(len(list)):
        insertion_sort(buckets_list[z])
    output = []
    for x in range(len(list)):
        output = output + buckets_list[x]
    return output

#cocktail sort function: time complexity: O(n^2)
def cocktail_sort(list):
    swapped = True
    start = 0
    end = len(list) - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            if list[i] > list[i + 1]:
                list[i], list[i + 1] = list[i + 1], list[i]
                swapped = True
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            if list[i] > list[i + 1]:
                list[i], list[i + 1] = list[i + 1], list[i]
                swapped = True
        start += 1
    return list

# comb sort function: time complexity: O(n^2)
def comb_sort(list):
    gap = len(list)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap / 1.3))
        swapped = False
        for i in range(len(list) - gap):
            if list[i] > list[i + gap]:
                list[i], list[i + gap] = list[i + gap], list[i]
                swapped = True
    return list

#counting sort function: time complexity: O(n+k)
def counting_sort(list):
    max_value = max(list)
    size = max_value + 1
    buckets_list = [0] * size
    for i in range(len(list)):
        buckets_list[list[i]] += 1
    i = 0
    for j in range(size):
        while buckets_list[j] > 0:
            list[i] = j
            i += 1
            buckets_list[j] -= 1
    return list

# cycle sort function: time complexity: O(n^2)
def cycle_sort(list):
    for i in range(len(list)):
        for j in range(i + 1, len(list)):
            if list[i] > list[j]:
                list[i], list[j] = list[j], list[i]
    return list

# gnome sort function: time complexity: O(n^2)
def gnome_sort(list):
    i = 0
    while i < len(list):
        if i == 0 or list[i] >= list[i - 1]:
            i += 1
        else:
            list[i], list[i - 1] = list[i - 1], list[i]
            i -= 1
    return list

# heap sort function: time complexity: O(n log n)
def heap_sort(list):
    def heapify(list, i, size):
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < size and list[left] > list[largest]:
            largest = left
        if right < size and list[right] > list[largest]:
            largest = right
        if largest != i:
            list[i], list[largest] = list[largest], list[i]
            heapify(list, largest, size)
    size = len(list)
    for i in range(size // 2 - 1, -1, -1):
        heapify(list, i, size)
    for i in range(size - 1, 0, -1):
        list[0], list[i] = list[i], list[0]
        heapify(list, 0, i)
    return list

#insertion sort function: time complexity: O(n^2)
def insertion_sort(list):
    for i in range(len(list)):
        j = i
        while j > 0 and list[j] < list[j - 1]:
            list[j], list[j - 1] = list[j - 1], list[j]
            j -= 1
    return list

# merge sort function: time complexity: O(n log n)
def merge_sort(list):
    if len(list) <= 1:
        return list
    mid = len(list) // 2
    left = merge_sort(list[:mid])
    right = merge_sort(list[mid:])
    return merge(left, right)
def merge(left, right):
    result = []
    while len(left) > 0 and len(right) > 0:
        if left[0] <= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right

#odd-even sort function: time complexity: O(n^2)
def odd_even_sort(list):
    swapped = True
    while swapped:
        swapped = False
        for i in range(1, len(list), 2):
            if list[i] < list[i - 1]:
                list[i], list[i - 1] = list[i - 1], list[i]
                swapped = True
        for i in range(0, len(list), 2):
            if list[i] > list[i + 1]:
                list[i], list[i + 1] = list[i + 1], list[i]
                swapped = True
    return list

# pancake sort function: time complexity: O(n^2)
def pancake_sort(list):
    array_length = len(list)
    while array_length > 1:
        mi = list.index(max(list[0:array_length]))
        list = list[mi::-1] + list[mi+1:len(list)]
        list = list[array_length-1::-1] + list[array_length:len(list)]
        array_length -= 1
    return list

# quick sort function: time complexity: O(n log n)
def quick_sort(list):
    if len(list) <= 1:
        return list
    pivot = list[0]
    left = [x for x in list[1:] if x <= pivot]
    right = [x for x in list[1:] if x > pivot]
    return quick_sort(left) + [pivot] + quick_sort(right)

# radix sort function: time complexity: O(n+k)
def radix_sort(list):
    maxElement = max(list)

    countArrayLength = maxElement + 1

    countArray = [0] * countArrayLength

    for element in list:
        countArray[element] += 1

    for i in range(1, countArrayLength):
        countArray[i] += countArray[i - 1]

    output = [0] * len(list)
    i = len(list) - 1
    while i >= 0:
        current = list[i]
        countArray[current] -= 1
        newPosition = countArray[current]
        output[newPosition] = current
        i -= 1
    return output

# selection sort function: time complexity: O(n^2)
def selection_sort(list):
    for i in range(len(list)):
        min = i
        for j in range(i + 1, len(list)):
            if list[j] < list[min]:
                min = j
        list[i], list[min] = list[min], list[i]
    return list

#shell sort function: time complexity: O(n^2)
def shell_sort(list):
    gap = len(list) // 2
    while gap > 0:
        for i in range(gap, len(list)):
            j = i
            while j >= gap and list[j] < list[j - gap]:
                list[j], list[j - gap] = list[j - gap], list[j]
                j -= gap
        gap = gap // 2
    return list

# timsort function: time complexity: O(n log n)
def timsort(list):
    minrun = 32
    if len(list) <= minrun:
        insertion_sort(list)
        return list
    else:
        list = merge_sort(list)
        return list