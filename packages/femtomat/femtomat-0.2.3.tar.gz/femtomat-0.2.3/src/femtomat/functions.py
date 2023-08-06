import numpy as np

def nearest(array, value): 
    '''
    Returns index of element in array with value closest to the input value.

    :param array: Input array in which to find index.
    :param value: Value to search for in array.

    :return index: Returns index of element in array with value closest to the input value.
    '''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


#noise filtering functions for TA
def svd_reconstruction_E15(Data,k):
    '''
    Function which reconstructs a data matrix from eigenvectors and eigenvalues (determined by SVD) by only using the top :math:`k` eigenvalues and eigenvectors.

    :param Data: Data matrix which is decomposed and reconstructed.
    :param k: The number of eigenvectors and eigenvalues used to reconstruct the data matrix.

    :returns rec: Reconstructed data matrix.
    '''
    D = Data.shape[0]
    T = Data.shape[1]
    u, s, vh = np.linalg.svd(Data, full_matrices=False)
    rec = np.zeros_like(Data)
    for i in range(k):
        rec = rec + np.dot(u[:,i].reshape(D,1) * s[i], vh[i,:].reshape(1,T))
    return rec

def rmse_special(Data, rec):
    '''
    A  RSME calculator to calculate the Root Mean Square Error of the original data matrix and the reconstructed data matrix with a threshold of the :math:`\\sqrt{2/D}`. This is used to determine :math:`k`.

    :param Data: Original data matrix.
    :param rec: Reconstructed data matrix.
    
    :returns rmse: Returns either :math:`\\sqrt{2/D}` if the RMSE is greater than :math:`\\sqrt{2/D}` or the RMSE.
    '''
    D = Data.shape[0]
    temp = np.sqrt(np.sum((Data-rec)**2)/D)
    if temp >= np.sqrt(2/D):
        return temp
    else:
        return np.sqrt(2/D)

def k_opt(Data):
    '''
    Function returning the optimal number of eigenvectors and eigenvalues for reconstructing the a data matrix (:math:`k`).
    
    :param Data: Data matrix to find :math:`k` for.

    :returns :math:`k`: Optimal number of eigenvectors and eigenvalues for reconstructing the a data matrix.
    '''
    D = Data.shape[0]
    T = Data.shape[1]
    rms = [rmse_special(Data, svd_reconstruction_E15(Data,i)) for i in range(T)]
    tk = [(np.log(rms[i]) - np.log(np.sqrt(2/D)))/(np.log(rms[0]) - np.log(np.sqrt(2/D))) for i in range(T)]
    return np.where(np.array(tk) > 0.05)[0][-1]