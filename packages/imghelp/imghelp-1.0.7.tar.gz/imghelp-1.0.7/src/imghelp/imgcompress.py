import numpy as np
import matplotlib.pyplot as plt

def ImgCompress(img, method, level = 1):
    """
    Image compression using different compression method.
    This function compress image to a user defined compression level.
    
    SVD Method:
        SVD (Singular Value Decomposition) on RGB image. 
        Note: Actual image memory size is not changed from this function.
              It does not handle the Jpeg compression algorithm
    
    Resize:
        Resize image to different size using interval pixel selection method.
    
    Parameters
    ----------
    img : numpy.array
        Input image for compression.
    method : string
        Compression methods: Resize, SVD
    level : int
        Level of compression: 1-High, 2-Med, 3-Low
        
    Returns
    -------
    numpy.array
        The compressed image.
        
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from imghelp.ImgCompress import ImgCompress
    >>> image = plt.imread('../test_img/ubc.jpeg')
    >>> plt.imshow(image) #show the image
    >>> img_comp = ImgCompress(image, method='resize', level=1)
    >>> plt.imshow(img_comp) #show the compressed (resized) image
    """
    #Function input checks:
    assert type(img) == np.ndarray, "Invalid image type, expecting numpy.ndarray."
    assert np.min(img.shape[:2]) > 2 and len(img.shape) == 3 , "Input image has invalid dimension. Expecting a 3d array (RGB)."
    assert level in (1,2,3), "Invalid level, expecting 1, 2, 3"
    assert method.lower() in ('svd','resize'), "Invalid method, expecting 'SVD' or 'Resize'."
    
    #Calculate image size:
    h, w, c = img.shape

    #SVD image compression method:
    if method.lower() == "svd":
        level_scale = [0.05, 0.3, 0.90]
        img_comp = np.zeros(img.shape, dtype="uint8")        
        for i in range(c):
            U, S, D = np.linalg.svd(img[:,:,i])
            #x = int((h * w * level_scale[level-1]) / (h + w + 1))
            #x = (np.cumsum(S)/np.sum(S) < level_scale[level-1]).sum()
            x = max(int(len(S) * level_scale[level-1]), 2)            
            C = U[:, :x] @ np.diag(S[:x]) @ D[:x, :]
            img_comp[:,:,i] = C.astype("uint8")
        return img_comp
    
    #Resize method:
    elif method.lower() == "resize":
        level_scale = [0.3, 0.5, 0.70]
        h_new = int(h * level_scale[level-1])
        w_new = int(w * level_scale[level-1])        
        img_comp = np.zeros([w_new, h_new, c], dtype="uint8")
        for s in range(c):
            for i in range(w_new):
                for j in range(h_new):
                    img_comp[i, j, s] = img[int(i / level_scale[level-1]), int(j / level_scale[level-1]), s]

        return img_comp

    else:
        pass
