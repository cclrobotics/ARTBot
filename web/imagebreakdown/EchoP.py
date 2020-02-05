#{Originally created by:
#Nick Phillips 2014
#EchoK prints .csv file breakdown of image for echo transfer
#Enter name of image when prompted (ie img.png).
#}

from scipy.ndimage import imread
import numpy 

def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))


imName = str(input('Enter image file name.\n'))
startWell = str(input('Enter the well position for first color (ie A1):\n'))
startRow = hex2dec(startWell(1))-9
if(length(startWell)==2):
    startCol = str2num(startWell(2))
elif(length(startWell)==3):
    startCol = str2num(startWell[2:3])
end

dropSize = 1000
RGB = imread(imName)
#RGB = imrotate(RGB,90);
numRows = size(RGB,1)
numCols = size(RGB,2)
if (numRows>128) or (numCols>192):
    if (numCols/numRows) > (192/128):
        RGB = imresize[RGB, [float(nan), 192]]
    else:
        RGB = imresize[RGB, [128, float(nan)]]
    end
end

[data,test] = ImgBreakdownMS(RGB)
wells = size[data,1]*size[data,2]
output = zeros[wells,5]
i = 1
# {
# STEP 4
# TO DEFINE POSITION OF COLORS
# TO DEFINE FIRST COLOR COLUMN ON 384PP PLATE
# NOTE: All colors must be placed sequentially, without skipping wells, on the same row of the 384PP source plate
# Change const = col number-1 
# (ie for first color in B1, change const = 0
# for first color in A3, change const = 2)

# TO DEFINE COLOR ROW ON 384PP PLATE
# Change output(i,1) = row number
# (ie for colors in row B, output(i,1) = 2
# for colors in row D, output(i,1) = 4;

# TO CHANGE TRANSFER SIZE IN ECHO
# change output(i,5) = 2.5 to a multiple of 2.5
# This is the value of the drop size in the echo
# }
const = startCol-1
const
for r in size[data,1]:
    for c in size[data,2]:
        output[i,1] = startRow
        output[i,2] = data(r,c)+const
        output[i,3] = r
        output[i,4] = c
        output[i,5] = dropSize
        i = i+1
    end

end

c = blockshaped(output,wells,5)

# %STEP 5
# %Uncomment if you want to not print whitespace. 
# %Change line output(i,2)~= 2+const
# %Change the 2+const in that line to const+whatever col white is in
# %(ie for white in col 4, change to output(i,2) ~= 4+const
# %Not printing whitespace substantially reduces print time. 


# % 
# % parsedOut = [];
# % for i = 1:size(output,1)
# %     if output(i,2) ~= 8+const 
# %          parsedOut = [parsedOut;output(i,:)];
# %     end
# % end
# %   output = parsedOut;


header = ['Source Row,' 'Source Column,' 'Destination Row,' 'Destination Column,' 'Transfer Volume']
csvwrite('echoProgram.csv',output)