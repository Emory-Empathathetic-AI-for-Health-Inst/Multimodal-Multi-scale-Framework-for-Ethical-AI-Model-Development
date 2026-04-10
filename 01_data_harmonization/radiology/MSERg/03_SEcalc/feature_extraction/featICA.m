function [ICs] = featICA(concateImage, mask, GRAYLEVELS,frequency)
%concateImage is the concated moving and fixed image, mask is the
%corresponding mask, graylevels is the 256 usually if it is uint8 image
%frequency,is the frequency used in the gabor feature: 1...windowsize
%3,2...windowsize 5....i windowsize 2i+1
  WS = 2*frequency+1;
  [mix,ica]= gabor_frequency(concateImage,mask,frequency);
  ica_GABOR = ica;
  [ica_h,feature] = ica_haralic (concateImage,mask,GRAYLEVELS,WS);
  ICs = [ica_GABOR;ica_h];
end
