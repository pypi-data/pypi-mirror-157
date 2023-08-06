def consecutive_numbers(start: int, end: int = None):
    """
    Returns consecutive numbers

    Python range() in disguise

    Examples
    --------
    ```python
    from pythonesque import consecutive_numbers
    # or specify sub-modules:
    # from pythonesque.series import consecutive_numbers

    # 1,2,3 ... 10
    consecutive_numbers(10)

    # 1,2,3 ... 10
    consecutive_numbers(1, 10)

    # 10,9,8 ... 1
    consecutive_numbers(10, 1)

    # countdown from 10 to 1
    for count in consecutive_numbers(10, 1):
        print(count)
    ```


    Parameters
    ----------
    start: int
        First number of consecutive sequence

    end: int
        Last number of consecutive sequence


    Returns
    -------
    immutable sequence
        ie. range()

        Used in a for loop


    """

    if end is None:
        # end not specified,
        # eg. consecutive_numbers(10)
        # assume start=1, end=start+1
        return range(1, start + 1)

    if end > start:
        # start, end are specified, count up
        # eg. consecutive_numbers(1, 10)
        return range(start, end + 1)
    else:
        # start, end are specified, count down
        # eg. consecutive_numbers(10, 1)
        return range(start, end - 1, -1)


# if __name__ == "__main__":
#    for i in consecutive_numbers(10):
#        print(i)
#    print()
#
#    for i in consecutive_numbers(1, 10):
#        print(i)
#    print()
#
#    for i in consecutive_numbers(10, 1):
#        print(i)
#    print()
#
#    # print(consecutive_numbers(1,10))
