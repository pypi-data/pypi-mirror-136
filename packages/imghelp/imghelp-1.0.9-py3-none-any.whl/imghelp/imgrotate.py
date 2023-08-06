import matplotlib.pyplot as plt
import numpy as np

def ImgRotate(img, degree):
    
    """
    Rotate an image either 90, 180, 270, 360 degrees counterclockwise. 
    
    Function takes an image and rotates it the user-defined amount.
    
    Parameters
    ----------
    
    img : numpy.array
        Input image.
    
    degree : int
        Desired degree to rotate img: 90, 180, 270, 360.
        
    Output 
    ------
    
     numpy.array
        Returns rotated image.
    
    Examples
    --------
     >>> import matplotlib.pyplot as plt
    >>> from imghelp.ImgRotate import ImgRotate
    >>> image = plt.imread('../test_img/ubc.jpeg')
    >>> plt.imshow(image) # show the image
    >>> ImgRotate(image, 270) # rotate image 270 degrees
    
    """
    
    # input checks
    assert type(img) == np.ndarray, "This function only takes numpy.ndarrays"
    assert len(img.shape) == 3, "Invalid image type, expecting numpy.3d array."
    assert img.shape[2] == 3, "Invalid image type, expecting a RGB image"
    assert degree <= 360, "Please enter a degree <= 360"
    assert degree % 90 == 0, "Please enter a degree divisble by 90"
    
    # rotate 90 degrees
    if degree == 90:
        rotated_img = img.swapaxes(0,1)[...,::1] # swap axes 
        rotated_img = rotated_img[::-1,::1]
        return rotated_img

    # rotate 180 degrees
    if degree == 180:
        
        # basically just rotate 90 degrees twice 
        rotated_img = img.swapaxes(0,1)[...,::1]
        rotated_img = rotated_img[::-1,::1]
        rotated_img = rotated_img.swapaxes(0,1)[...,::1]
        rotated_img = rotated_img[::-1,::1]
        return rotated_img
    
    
    # rotate 270 degree
    if degree == 270:
        rotated_img = img.swapaxes(1,0)
        rotated_img = rotated_img[::1,::-1]
        return rotated_img
    
    # rotate 360 degree
    if degree == 360:
        rotated_img = img
        return rotated_img
