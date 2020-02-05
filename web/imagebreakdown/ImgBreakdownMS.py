#Originally created by: Nick Phillips - 2014
#modified by Mike Shen - 2015
#edited from the ImgBreakdownMS.m file
from scipy.ndimage import imread
import numpy 

def ImgBreakdownMS(RGB):

	imsize = size(RGB)
	imrows = imsize(1)
	imcols = imsize(2)
	#breaks down image and saves as file for analysis. 
	data = zeros(size(RGB,1),size(RGB,2));

	#Write RGB Value of colors here, in order as they are placed on the 384PP
	#plate. Position in nx3 matrix, where n = # of colors.

	colors = [[255, 255, 255], #white
	        [0, 0, 255], #blue
	        [0,0,0], #black
	        [104, 45, 145], #purple
	        [255, 248, 0], #yellow
	        [238, 121, 16], #orange 
	        [255, 0, 255], #pink
	       [111, 108, 112]] #gray


	test1 = zeros(imsize)
	nlDisp = zeros(size(colors,1),1)
	for r in range(imrows):
		for c in range(imcols):
			temp = colors
			p = zeros(1,3)
			p[1] = RGB(r,c,1)
			p[2] = RGB(r,c,2)
			p[3] = RGB(r,c,3)
			for i in size(temp,1):
				temp[i,:] = temp[i,:]-p
			end     
			temp = temp^2
			distance = sqrt(sum(temp,2))
			[a,b] = min(distance)
			if(nlDisp(b,1) > 30000):
				bb = b+size(colors,1)
				data[r,c] = bb
			else:
				data[r,c] = b
			end
			nlDisp[b,1] = nlDisp[b,1]+2.5
			test1[r,c,1] = colors[b,1]
			test1[r,c,2] = colors[b,2]
			test1[r,c,3] = colors[b,3]
		end
	end


	return [data, test1]