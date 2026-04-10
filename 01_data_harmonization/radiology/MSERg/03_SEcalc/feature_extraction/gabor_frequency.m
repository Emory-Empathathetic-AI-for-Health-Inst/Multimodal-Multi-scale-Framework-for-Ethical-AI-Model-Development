function [submix,ica_out]=gabor_frequency(img,mask,i)
% i*0.5 is frequecy
%submix was the region of prostate
lambda= 0.5*i;
b=1;
psi= 0;
gamma=1;
[m,n]=size(img);
feature = zeros(m,n,10);
for k = 1:10
theta = k*pi/10;
[gb_c1,gb_s1]=gabor2dkerns(theta,lambda,b,psi,gamma);
feature(:,:,k) = rescale(imfilter(img,gb_c1,'same'))*255;
end
feature_vec = reshape(feature(:,:,1),[],1);
mix = feature_vec';
for l =2:10
    feature_vec = reshape(feature(:,:,l),[],1);
    mix = [mix;feature_vec'];
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

