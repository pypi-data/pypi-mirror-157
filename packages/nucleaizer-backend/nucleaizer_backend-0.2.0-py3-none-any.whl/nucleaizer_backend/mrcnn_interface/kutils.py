
import numpy as np
import skimage
import cv2

def RCNNConvertInputImage(pImageData):
    if pImageData.ndim < 2:
        raise ValueError("Invalid image")
    elif pImageData.ndim < 3:
        pImageData = skimage.color.gray2rgb(pImageData)
    if pImageData.shape[2] > 3:
        pImageData = pImageData[:, :, :3]

    # handle 16-bit images
    if pImageData.dtype==np.uint16:
        #print('uint16 image, stretching intensities before converting to uint8')
        imagetmp=np.zeros((pImageData.shape[0],pImageData.shape[1],3),dtype=np.uint8)
        for ch in range(3):
            tmp=pImageData[:,:,ch]
            imgg = tmp.astype(np.float)
            tmp=((imgg-np.amin(imgg))*255)/(np.amax(imgg)-np.amin(imgg));
            tmp=tmp.astype(np.uint8);
            imagetmp[:,:,ch]=tmp
        pImageData=imagetmp
    else:
        pImageData = pImageData.astype(np.uint8)

    return pImageData

def MergeMasks(pMasks):
    if pMasks.ndim < 3:
        raise ValueError("Invalid masks")

    maskCount = pMasks.shape[2]
    width = pMasks.shape[1]
    height = pMasks.shape[0]
    mask = np.zeros((height, width), np.uint16)

    for i in range(maskCount):
        mask[:,:] = np.where(pMasks[:,:,i] != 0, i+1, mask[:,:])

    return mask


def PadImageR(pImageData, pRatio):
    width = pImageData.shape[1]
    height = pImageData.shape[0]

    x = int(float(width) * float(pRatio))
    y = int(float(height) * float(pRatio))

    image = PadImageXY(pImageData, x, y)
    return image, (x, y)

def PadMask(image_shape, masks, pad_offsets):
    height = image_shape[0]
    width = image_shape[1]
    count = masks.shape[2]
    newMasks = np.zeros((height, width, count), np.uint8)
    offsetY = pad_offsets[0]
    offsetX = pad_offsets[1]
    for i in range(count):
        newMasks[:, :, i] = masks[offsetY: (offsetY + height), offsetX: (offsetX + width), i]
    
    return newMasks

def DilateMask(masks, dilate):
    count = masks.shape[2]
    dilatioKernel = skimage.morphology.disk(dilate)
    for i in range(count):
        masks[:, :, i] = skimage.morphology.binary_dilation(masks[:, :, i], dilatioKernel)
    return masks

def CavityFill(masks):
    count = masks.shape[2]
    for i in range(count):
        temp = cv2.bitwise_not(masks[:, :, i])
        _, temp = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        masks[:, :, i] = cv2.bitwise_not(temp)
    return masks

def SqueezeMask(masks):
    count = masks.shape[2]
    for i in range(count):
        masks[:, :, i] = np.where(masks[:, :, i] == 0, 0, 255)
    return masks

def PadImageXY(pImageData, pX, pY):
    width = pImageData.shape[1]
    height = pImageData.shape[0]

    paddedWidth = width + 2 * pX
    paddedHeight = height + 2 * pY


    if pImageData.ndim > 2:
        count = pImageData.shape[2]
        image = np.zeros((paddedHeight, paddedWidth, count), pImageData.dtype)
        for c in range(count):
            image[:, :, c] = np.lib.pad(pImageData[:, :, c], ((pY, pY), (pX, pX)), "reflect")

    else:
        image = np.lib.pad(pImageData, ((pY, pY), (pX, pX)), "reflect")

    return image
