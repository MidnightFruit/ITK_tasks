def search(arr: list[int], num: int) -> bool:
    """
    Бинарный поиск.
    
    :param arr: Входной массив в котором выполняется поиск.
    :type arr: list[int]
    :param num: Число которое требуется найти.
    :type num: int
    :return: True если число есть, False если числа нет.
    :rtype: bool
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == num:
            return True
        elif arr[mid] > num:
            right = mid - 1
        else:
            left = mid + 1
    return False
