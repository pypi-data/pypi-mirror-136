import numpy as np
import matplotlib.pyplot as plt

def Crop(image, width, height):
    """
    This function crops image based on the input width and height.
      Parameters
      ---------
      image : numpy.ndarray
              An image, which is represented as a 3D numpy array in python
      width : int
              The desired width of the output image
      height : int
              The desired height of the output image
      Returns
      -------
      numpy array :
      croped image as 3D array
      Examples
      -------
      >>> import matplotlib.pyplot as plt
      >>> from img.Crop import Crop
      >>> image = plt.imread('../test_img/ubc.jpeg')
      >>> plt.imshow(image) #show the image
      >>> img_crop = Crop(image, 300, 300)
      >>> plt.imshow(img_comp) #show the cropped image
      """
    # varify if the input format is appropriate, print out 
    # the corresponding information
    if (type(image) != np.ndarray) or (len(image.shape) != 3):
        raise TypeError('Error: Image must be expressed as a 3D array')
    elif (width % 1 != 0) or (height % 1 != 0):
        raise TypeError('Error: Height and width for the desired image must be integer')
    elif (height <= 0 or width <= 0):
        raise ValueError('Desired height and width must be greater than 1')
    elif (height > image.shape[0] or width > image.shape[1]):
        raise ValueError(
            'Desired height and width cannot exceeds original height and \
             width')
    else:
        print(f"Converting the original image to the width {width} and height {height}...")

    #the number of rows and columns to be cropped
    new_height = image.shape[0] - height
    new_width = image.shape[1] - width
 
    #manipulations on rows
    if new_height % 2 == 0:
        start_row = int(new_height/2) + 1
        end_row = start_row + height 
    else:
        start_row = int((new_height - 1)/2) + 1
        end_row = start_row + height 

    #manipulations on columns
    if new_width % 2 == 0:
        start_col = int(new_width/2) + 1
        end_col = start_col + width 
    else:
        start_col = int((new_width - 1)/2) + 1
        end_col = start_col + width 

    #crop image by cropping rows and columns using 
    #slicing in numpy
    new_image = image[start_row:end_row, start_col:end_col, :]
    print("Done!")

    return new_image

