%MSERg main
clear
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
addpath([parentFolder,'/01_preprocess']);
inputDir = [parentFolder,'/example/processed'];
outputDir = [parentFolder,'/example/processed/MSERg'];
tic
MSERgFun_clinic([2,3,8],inputDir,outputDir);
toc

cd(currentFolder);
%% visualization
mri = (imread([parentFolder,'/example/mri_whole.png']));
mriLandmark = double(imread([inputDir,'/mrilandmarkDS.png']));
MSERgimg = double(imread([outputDir,'/image/result.tif']));
temp = zeros(size(MSERgimg));
MSERgLandmark = double(imread([outputDir,'/marker/result.tif']));
[com_MSERg] = visualization(mri,temp,mriLandmark,MSERgLandmark,2);
Background = imcrop(MSERgimg);
thresh = mean(mean(Background));
mask = MSERgimg>thresh;
mask = double(mask);
I = convert2rgb(MSERgimg,mask);
background = cat(3,mri,mri,mri);
hist = (I).*0.5;
overlap = background*0.7+hist;
figure
subplot(1,2,1)
imshow(com_MSERg,[]);
title('landMark visulaization')
subplot(1,2,2)
imshow(overlap,[]);
title('overlap')
