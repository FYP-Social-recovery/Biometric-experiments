import math
import numpy as np
import cv2 
from math import pi
from scipy import stats

def Eight_field_Direction(img):
	# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_2 = np.pad(img, 4, mode='constant')
	Size = img_2.shape
	G = np.zeros(9)
	G_diff = np.zeros(5)
	FloatImage = np.float32(img_2)
	im3 = np.zeros(img.shape) 
	im_out = np.zeros(img.shape)
	im_out_2 = np.zeros(img.shape) 
	for x in range (4, Size[0]-4):
		for y in range (4,Size[1]-4):
			for i in range (1,9):

				if(i == 1):
					G[i] = (FloatImage[x+2][y]+ FloatImage[x-2][y]+ FloatImage[x+4][y]+ FloatImage[x-4][y])/4.0
					
				elif(i == 2):
					G[i] = (FloatImage[x-1][y+2]+ FloatImage[x-2][y+4]+ FloatImage[x+1][y-2]+ FloatImage[x+2][y-4])/4.0
				elif(i == 3):
					G[i] = (FloatImage[x-2][y+2]+ FloatImage[x+2][y-2]+ FloatImage[x-4][y+4]+ FloatImage[x+4][y-4])/4.0
				elif(i == 4):
					G[i] = (FloatImage[x-2][y+1]+ FloatImage[x-4][y+2]+ FloatImage[x+2][y-1]+ FloatImage[x+4][y-2])/4.0	
				elif(i == 5):
					G[i] = (FloatImage[x-2][y]+ FloatImage[x-4][y]+ FloatImage[x+2][y]+ FloatImage[x+4][y])/4.0
				elif(i == 6):
					G[i] = (FloatImage[x-2][y-1]+ FloatImage[x+2][y+1]+ FloatImage[x-4][y-2]+ FloatImage[x+4][y+2])/4.0
				elif(i == 7):
					G[i] = (FloatImage[x-2][y-2]+ FloatImage[x-4][y-4]+ FloatImage[x+2][y+2]+ FloatImage[x-4][y-4])/4.0
				else:
					G[i] = (FloatImage[x+1][y+2]+ FloatImage[x+2][y+4]+ FloatImage[x-1][y-2]+ FloatImage[x-2][y-4])/4.0
			for k in range (1,5):
				G_diff[k] = abs(G[k] - G[k+4])
			i_max = np.argmax(G_diff)
			if (abs(FloatImage[x][y]-G[i_max]) < abs(FloatImage[x][y]-G[i_max+4])):
				im3[x-4][y-4] = i_max
			else:
				im3[x-4][y-4] = i_max+4
	w1 = 4
	im_current = im3
	im_next = im3
	
	for x in range (0, img.shape[0]):
		for y in range (0, img.shape[1]):
			x_start = max (0, x-w1 ) 
			x_end = min(img.shape[0]-1, x+w1)
			y_start = max(0, y-w1 ) 
			y_end = min(img.shape[1]-1, y+w1)

			sub_img = im_next[x_start:x_end:1, y_start:y_end:1] 
			z = stats.mode(sub_img, axis=None)
			im_out_2[x][y] = z[0][0]
			
	im_out_2 = (im_out_2 - np.ones(im_out_2.shape))*pi/8.0
	return im_out_2

import cv2
import numpy as np
import math
from matplotlib import pyplot as plt

f = lambda x,y: 2*x*y
g = lambda x,y: x**2 - y**2

def get_line_ends(x, y, tang, block_size, offset=0):
	x, y = x*block_size, y*block_size
	half_block = (block_size/float(2))

	if offset < 0:
		offset = 0
	elif offset > block_size/2:
		offset = block_size/2

	if -1 <= tang <= 1:
		x1 = x + offset
		y1 = y + half_block - (tang * half_block)
		x2 = x + block_size - offset
		y2 = y + half_block + (tang * half_block)
	else:
		x1 = x + half_block + (half_block/(2*tang))
		y1 = y + block_size - offset
		x2 = x + half_block - (half_block/(2*tang))
		y2 = y + offset

	return (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2)))

def draw_lines(h, w, c, angles, block_size):
	im = np.empty((h, w, c), np.uint8)
	# white background
	im[:] = 255

	for i in range(w/block_size):
		for j in range(h/block_size):
			angle = angles.item(j, i)
			
			if angle != 0:
				angle = -1/math.tan(math.radians(angle))
				p1, p2 = get_line_ends(i, j, angle, block_size, 2)
				cv2.line(im, p1, p2, (0,0,255), 1)
	return im

def orientation2(img, block_size, smooth=False):
	h, w = img.shape

	# make a reflect border frame to simplify kernel operation on borders
	borderedImg = cv2.copyMakeBorder(img, block_size,block_size,block_size,block_size, cv2.BORDER_DEFAULT)

	# apply a gradient in both axis
	sobelx = cv2.Sobel(borderedImg, cv2.CV_64F, 1, 0, ksize=3)
	sobely = cv2.Sobel(borderedImg, cv2.CV_64F, 0, 1, ksize=3)

	angles = np.zeros((h/block_size, w/block_size), np.float32)

	for i in range(w/block_size):
		for j in range(h/block_size):
			nominator = 0.
			denominator = 0.

			# calculate the summation of nominator (2*Gx*Gy)
			# and denominator (Gx^2 - Gy^2), where Gx and Gy
			# are the gradient values in the position (j, i)
			for k in range(block_size):
				for l in range(block_size):
					posX = block_size-1 + (i*block_size) + k
					posY = block_size-1 + (j*block_size) + l
					valX = sobelx.item(posY, posX)
					valY = sobely.item(posY, posX)

					nominator += f(valX, valY)
					denominator += g(valX, valY)
			
			# if the strength (norm) of the vector 
			# is not greater than a threshold
			if math.sqrt(nominator**2 + denominator**2) < 1000000:
				angle = 0.
			else:
				if denominator >= 0:
					angle = cv2.fastAtan2(nominator, denominator)
				elif denominator < 0 and nominator >= 0:
					angle = cv2.fastAtan2(nominator, denominator) + math.pi
				else:
					angle = cv2.fastAtan2(nominator, denominator) - math.pi
				angle /= float(2)

			angles.itemset((j, i), angle)
	
	if smooth:
		angles = cv2.GaussianBlur(angles, (3,3), 0, 0)
	return angles

def draw_orientation(h, w, angles, block_size):
	im = np.zeros((h, w), np.uint8)

	for i in range(w/block_size):
		for j in range(h/block_size):	
			dangle = 2*angles.item(j, i)
			v = int(round(dangle * (255/float(360))))
			for k in range(block_size):
				for l in range(block_size):
					im.itemset((j*block_size+l,i*block_size+k), v)
	return im


# filename = "temp01.jpg"
# # filename = "imgs/2.jpg"
# KSIZE = 11

# img = cv2.imread(filename)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# angles = orientation2(gray, KSIZE)

# h, w = gray.shape
# orientationImg = draw_lines(h, w, 3, angles, KSIZE)

# cv2.imshow('src', orientationImg)
# # cv2.imshow('dst', orientationImg)
# if cv2.waitKey(0) & 0xFF == 27:
#     cv2.destroyAllWindows()