from algofunc.search import binary_search, fibonacci_search, jump_search, linear_search, ternary_search


# test binary search
def test_binary_search():
    list = [1, 2, 3, 4, 5, 6, 7, 8]
    assert binary_search(list, 1) == 0
    assert binary_search(list, 2) == 1
    assert binary_search(list, 8) == 7
    assert binary_search(list, 9) == -1

# test fibonacci search
def test_fibonacci_search():
    list = [1, 2, 3, 4, 5, 6, 7, 8]
    assert fibonacci_search(list, 0) == -1
    assert fibonacci_search(list, 3) == 2
    assert fibonacci_search(list, 7) == 6
    assert fibonacci_search(list, 10) == -1

# test jump search
def test_jump_search():
    list = [1, 2, 3, 4, 5, 6, 7, 8]
    assert jump_search(list, 0) == -1
    assert jump_search(list, 5) == 4

# test linear search
def test_linear_search():
    list = [1, 2, 3, 4, 5, 6, 7, 8]
    assert linear_search(list, 0) == -1
    assert linear_search(list, 3) == 2
    assert linear_search(list, 7) == 6
    assert linear_search(list, 10) == -1

# test ternary search
def test_ternary_search():
    list = [1, 2, 3, 4, 5, 6, 7, 8]
    assert ternary_search(list, 0) == -1
    assert ternary_search(list, 3) == 2
    assert ternary_search(list, 7) == 6
    assert ternary_search(list, 10) == -1


