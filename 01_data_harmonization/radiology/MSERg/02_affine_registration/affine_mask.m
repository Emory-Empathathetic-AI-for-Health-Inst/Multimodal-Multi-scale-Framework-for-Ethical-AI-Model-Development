%this file is used to generate affine image mask
clear
addpath('//csehomes/csehome$/lxl477/Desktop/matlab/general')
for i =11
    %caseID
    affineDir = sprintf('D:/MICCAI/Data/clinical/uppen/croped/case%d/affine/image/result.tif',i);
    anoDir = sprintf('D:/MICCAI/Data/clinical/uppen/croped/case%d/affine/marker/result.tif',i);
    affine_hist = uint8(imread(affineDir));  
    annotation = uint8(imread(anoDir));  
    
    background = imcrop(affine_hist);
    threshold = mean(reshape(background,1,[]));
    mask = (affine_hist > threshold);
    imshow(mask,[])
    filename =sprintf('D:/MICCAI/Data/clinical/uppen/croped/case%d',i);
    imwrite(rescale(mask),[filename,'/affine_mask.png']);
    imwrite(affine_hist,[filename,'/affine_hist.png']);
       imwrite(annotation,[filename,'/affine_landmark.png']); 
    
end