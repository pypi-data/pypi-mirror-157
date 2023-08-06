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

def data_spltit(data,labels, devset = True, batch = 32,proportion = [.1,.2]):
    ''' 
    Function to split a PyTorch tensor into train,dev,test in dataloaders.
    You must estimate the batchsize, the remainder of the batchsize will
    be automatically excluded.

    Parameters
    ----------
    data : torch.tensor
        array with data to split
    labels : torch.tensor
        single dimensional array with labels
    devset : bool
        if True  = will split data into Train,Dev,Test (.8|.1|.1 - according with the first term of proportion[0])
        if False = will split data into Train,Test (.8|.2 - according with the second term of proportion[1])
    batch : int
        The batch size for the train dataloader
    proportion : list
        List of proportions, the first is used if the 'devset = True' and the remainder is split in .5.
        if 'devset = False' the second term is used to split train/data.

    Returns
    -------
    if devset = True
        train_loader, dev_loader, test_loader : DataLoader
    else
        train_loader, test_loader : DataLoader

    See Also
    --------
    Developed by Tulio Almeida.
    https://github.com/tuliofalmeida/scroll-of-seals

    '''
    import torch
    from sklearn.model_selection import train_test_split
    from torch.utils.data import DataLoader,TensorDataset

    assert isinstance(data  ,type(torch.tensor([]))), 'Data must be a tensor'
    assert isinstance(labels,type(torch.tensor([]))), 'Labels must be a tensor'

    batchsize = batch

    if devset:
        # split the train and the temporary data/labels
        train_data,temp_data, train_labels,temp_labels = train_test_split(data, labels, test_size=proportion[0]) 
        # split the temporary data/labels into dev and test
        dev_data  ,test_data, dev_labels  ,test_labels = train_test_split(temp_data, temp_labels, test_size=.5)

        # create the train and the test datasets
        train_data = TensorDataset(train_data,train_labels)
        dev_data   = TensorDataset(dev_data,dev_labels)
        test_data  = TensorDataset(test_data,test_labels)

        # create the train and the test dataloader and apply the batchsize
        train_loader = DataLoader(train_data,batch_size=batchsize,shuffle=True,drop_last=True)
        dev_loader   = DataLoader(dev_data,batch_size=dev_data.tensors[0].shape[0])
        test_loader  = DataLoader(test_data,batch_size=test_data.tensors[0].shape[0])

        return train_loader, dev_loader, test_loader

    else:
        # split the train and the test data/labels
        train_data,test_data, train_labels,test_labels = train_test_split(data, labels, test_size=proportion[1])

        # create the train and the test datasets
        train_data = TensorDataset(train_data,train_labels)
        test_data  = TensorDataset(test_data,test_labels)

        # create the train and the test dataloader and apply the batchsize
        train_loader = DataLoader(train_data,batch_size=batchsize,shuffle=True,drop_last=True)
        test_loader  = DataLoader(test_data,batch_size=test_data.tensors[0].shape[0])

        return train_loader,test_loader