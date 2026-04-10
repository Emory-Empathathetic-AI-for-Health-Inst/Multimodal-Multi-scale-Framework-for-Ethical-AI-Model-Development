
function [com_g] = visualization(imag1,imag2,landm1,landm2,type)
addpath('//csehomes/csehome$/lxl477/Desktop/matlab/general');
%landm1 and landm2 are landmark annotations
%imag1 are treated as background image
%type = 1, does not show the image overlap
mri = imag1;
hist = imag2;

mask = double(landm2>50);
hist_marker = double(landm2).*mask;
mri_marker = landm1;
groundtrue = (double(mri_marker)~=0)*255;
ground_img = rescale(mri)*255;
ground_hist = double(hist);
ground_h = double(hist_marker);
com_glmk = imfuse(ground_h,groundtrue,'falsecolor','Scaling','joint','ColorChannels',[1 2 2]);
com_ground = imfuse(ground_img,ground_hist,'blend');
if type == 1
com_g = imfuse(ground_img,com_glmk,'blend');
else
    com_g = imfuse(com_ground,com_glmk,'blend');
end

end