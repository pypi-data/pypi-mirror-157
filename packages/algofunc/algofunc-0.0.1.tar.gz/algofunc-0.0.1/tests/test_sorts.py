from algofunc.sorts import bitonic_sort, bubble_sort, bucket_sort, cocktail_sort, comb_sort, heap_sort, insertion_sort, \
    merge_sort, quick_sort, selection_sort, shell_sort, timsort


def test_bitonic_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert bitonic_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_bubble_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert bubble_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_bucket_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert bucket_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_cocktail_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert cocktail_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_comb_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert comb_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_heap_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert heap_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_insertion_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert insertion_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_merge_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert merge_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_quick_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert quick_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_selection_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert selection_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_shell_sort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert shell_sort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

def test_timsort():
    list = [6, 5, 3, 1, 8, 7, 2, 4]
    assert timsort(list) == [1, 2, 3, 4, 5, 6, 7, 8]

