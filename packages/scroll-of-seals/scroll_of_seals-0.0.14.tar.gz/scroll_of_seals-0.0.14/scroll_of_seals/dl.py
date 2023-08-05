def img_size_convolved( img_px , padding_size, kernel_size, stride_size, square = True ):
    ''' 
    Function to find the size of a matrix after convolution.
    If square False, all the inputs must be lists

    Parameters
    ----------
    square : bool
        if True  = matrix is square, the inputs must be integers
        if False = matrix is rectangular, the inputs must be a list or tuple
                   rows/height = first element
                   column/width = second element

    img_px : int/list
        Image size (e.g, 91 or [91,91])
    padding_size : int/list
        padding size (e.g, 1 or [1,1])
    kernel_size
        kernell size (e.g, 3 or [3,3])
    stride_size
        stride size  (e.g, 1 or [1,1])

    Returns
    -------
    rows : int
        rows/height of matrix
    columns : int
        columns/weight of matrix


    Equation
    ----------

    Nh = np.floor( (Mh+2p-k)/Sh )+1
    Nw = np.floor( (Mw+2p-k)/Sw )+1

    h = height 
    w = width
    N = Number of pixels
    M = Number of pixels in previous layer
    p = padding
    K = Number of pixels in kernel
    S = Stride step

    Example
    ----------
    # Conv the image using a image of 91x91 px
    # padding = 1, kernel = 3 and stride = 1

    r,c = img_size_convolved(91,1,3,1)
    print(r,c)
    >>> 91,91

    # now apply a pooling layer into the result
    # pool of the result, 0 padding, 2x2 kernel
    # and stride = 2

    r,c = img_size_convolved(r,0,2,2)
    print(r,c)
    >>> 45,45

    See Also
    --------
    Developed by Tulio Almeida.
    https://github.com/tuliofalmeida/scroll-of-seals

    '''
    import numpy as np
    
    if square:
        rows    = np.floor( (img_px + 2*padding_size - kernel_size)/stride_size )+1
        columns = np.floor( (img_px + 2*padding_size - kernel_size)/stride_size )+1
    else:
        rows    = np.floor( (img_px[0] + 2*padding_size[0] - kernel_size[0])/stride_size[0] )+1
        columns = np.floor( (img_px[1] + 2*padding_size[1] - kernel_size[1])/stride_size[1] )+1
    return int(rows),int(columns)