"""Print a nice progress bar that can be used for example to show the
progress in a loop:

    from __future__ import division, print_function

    for i in range(n):
        print(progress_bar((i + 1) / n), end="")
    print()

"""

def progress_bar(fraction):
    return '\r[{0:50s}] {1:.1%}'.format('#' * int((fraction * 50)), fraction)
