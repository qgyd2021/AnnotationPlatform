#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cv2 as cv


def show_image(image, win_name='input image'):
    # cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    cv.namedWindow(win_name, cv.WINDOW_AUTOSIZE)

    cv.imshow(win_name, image)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return


if __name__ == '__main__':
    pass
