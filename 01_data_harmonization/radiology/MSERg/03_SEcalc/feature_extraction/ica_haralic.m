
function [ica_out,feature] = ica_haralic (IMAGE,mask,GRAYLEVELS,WS)
%   IMAGE is a 2D input image
%
%   GRAYLEVELS is how many graylevels you are considering for co-occurrence
%   NOTE: You should "rescale" your IMAGE to utilize the range of
%   graylevels you are utilizing
%   e.g. image = round(rescale_range(image,0,127));
%   In this example, GRAYLEVELS = 128.
%   WS is the window-size within which statistics are calculated
%   e.g. WS = 5 will use a 5 x 5 window, i.e. 2 pixels in all directions
%   around the "center pixel"
%
%   DIST is how many co-occurring neighbors you want to utilize around 
%   each pixel within the window (defined by WS), for determining the
%   co-occurence matrix
%   e.g. DIST = 1 will use a 3 x 3 block around each pixel inside the
%   window to calculate co-occurrences
%   NOTE: You can utilize different values for WS and DIST.
%
%   BACKGROUND is the value of "background" intensities which will be
%   ignored during all calculations.
%
%   FEATURES will be a X x Y x 13 matrix, where X,Y are the input
%   dimensions of IMAGE
DIST = 1 ;
BACKGROUND = 0;
feature = haralick2mex(double(IMAGE),GRAYLEVELS,WS,DIST,BACKGROUND);
 feat_vec = reshape(feature(:,:,1),[],1);
 mix = feat_vec';  
for i = 2:size(feature,3)
 feat_vec = reshape(feature(:,:,i),[],1);
 mix = [mix;feat_vec'];
end
mask_vec = reshape(mask,[],1);
mask_vec = mask_vec';
for k = 1: size(mix,1)
    mixvec = mix(k,:);
    submix(k,:)= mixvec(mask_vec~=0);
end
B = jadeICA(submix);%% change the variance percentage in pca part
ica_out = B*submix;
end
 
 
 