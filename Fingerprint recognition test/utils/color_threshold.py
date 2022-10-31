from matplotlib import pyplot as plt
import cv2 as cv

def show_img_thresholds(img):
    ret,thresh1 = cv.threshold(img,127,255,cv.THRESH_BINARY_INV)
    ret,thresh2 = cv.threshold(img,127,255,cv.THRESH_OTSU)
    ret,thresh3 = cv.threshold(img,127,255,cv.THRESH_BINARY | cv.THRESH_OTSU)
    ret,thresh4 = cv.threshold(img,127,255,cv.THRESH_BINARY)
    ret,thresh5 = cv.threshold(img,127,255,cv.THRESH_TOZERO_INV)
    titles = ['Original Image','BINARY_INV','OTSU','BINARY|OTSU','BINARY','TOZERO_INV']
    images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]
    for i in range(6):
        plt.subplot(2,3,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()

    return thresh2

# def binarize(im):
#     gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
#     (retval, dst) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
#     return dst

# def binarize2(image, w=32):
#     """
#     Perform a local binarization of an image. For each cell of the given size
#     w, the average value is calculated. Every pixel that is below this value,
#     is set to 0, every pixel above, is set to 1.
#     :param image: The image to be binarized.
#     :param w:     The size of the cell.
#     :returns:     The binarized image.
#     """

#     image = np.copy(image)
#     height, width = image.shape
#     for y in range(0, height, w):
#         for x in range(0, width, w):
#             block = image[y : y + w, x : x + w]
#             threshold = np.average(block)
#             image[y : y + w, x : x + w] = np.where(block >= threshold, 1.0, 0.0)

#     return image