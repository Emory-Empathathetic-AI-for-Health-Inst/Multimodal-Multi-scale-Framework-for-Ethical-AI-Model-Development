%this file is used to downsample hist images
clear
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
inputdir =[parentFolder,'\example'];
outputdir =[parentFolder,'\example\processed'];
mkdir(outputdir);
MRIreference = imread([inputdir,'/mri.png']);
HistOri = imread([inputdir,'/hist.png']);
HistAnot_temp = imread([inputdir,'/hist_mask.png']);
[Histlandmark_temp] = imread([inputdir,'/hist_landmark.png']);
[MRIlandmark_temp] = imread([inputdir,'/mri_landmark.png']);
histlandmark = uint8(zeros(size(Histlandmark_temp(:,:,3))));
%blue
temp_b =Histlandmark_temp(:,:,3);
histlandmark(temp_b~=0) = 100;
%red green yellow
temp_RGY = Histlandmark_temp(:,:,2);
landmark_value = unique(temp_RGY);
if length(landmark_value)>3
    histlandmark(temp_RGY == landmark_value(2)) = 125;%red
    histlandmark(temp_RGY == landmark_value(3)) = 200;%yellow
    histlandmark(temp_RGY == landmark_value(4)) = 225;%green
else
    
    histlandmark(Histlandmark_temp(:,:,2)~=0) = 225;%green
    histlandmark(Histlandmark_temp(:,:,1)~=0) = 200;%red
end


mrilandmark = uint8(zeros(size(MRIlandmark_temp(:,:,3))));
%blue
temp_b = MRIlandmark_temp(:,:,3);
mrilandmark(temp_b~=0) = 100;
%red green yellow
temp_RGY = MRIlandmark_temp(:,:,2);
landmark_value = unique(temp_RGY);
if length(landmark_value)>3
    mrilandmark(temp_RGY == landmark_value(2)) = 125;%yellow
    mrilandmark(temp_RGY == landmark_value(3)) = 200;%red
    mrilandmark(temp_RGY == landmark_value(4)) = 225;%green
else
    
    mrilandmark(MRIlandmark_temp(:,:,2)~=0) = 225;%green
    mrilandmark(MRIlandmark_temp(:,:,1)~=0) = 200;%red
end

HistAnot = HistAnot_temp(:,:,1)~=0;
HistGray = rgb2gray(HistOri);
HistGray = double(HistGray).*double(HistAnot);

%manually corp the bounding box of prostate out of the histology and mri
%image, and according the size of bounding box to downsample the histology image 
[XData2,YData2] = imcrop(MRIreference);
width = abs(max(YData2)-min(YData2));
[XData,YData] = imcrop(HistGray);
scalesize = width/abs(max(YData)-min(YData))*2;
HistDS = imresize(HistGray,scalesize);
AnotDS = imresize(HistAnot,scalesize);


HistPad = padarray(HistDS,[floor((min(YData2)+max(YData2))/1.5),floor((min(YData2)+max(YData2))/1.5)]);
AnotPad = padarray(AnotDS,[floor((min(YData2)+max(YData2))/1.5),floor((min(YData2)+max(YData2))/1.5)]);
histlandmarkPad = zeros(size(HistPad));
if length(landmark_value)>3
    label = [100,125,200,225];%blue red yellow green
    for j = 1:length(label)
        temp_hist = double(histlandmark == label(j));
        landmarkDS = imresize(temp_hist,scalesize);
        histlandmarkPad_temp = padarray(landmarkDS,[floor((min(YData2)+max(YData2))/1.5),floor((min(YData2)+max(YData2))/1.5)]);
        histlandmarkPad_temp(histlandmarkPad_temp~=0)=label(j);
        histlandmarkPad = histlandmarkPad+histlandmarkPad_temp;
    end
else
    label =[100,200,225];%blue red green
    for j = 1:length(label)
        temp_hist = double(histlandmark == label(j));
        landmarkDS = imresize(temp_hist,scalesize);
        histlandmarkPad_temp = padarray(landmarkDS,[floor((min(YData2)+max(YData2))/1.5),floor((min(YData2)+max(YData2))/1.5)]);
        histlandmarkPad_temp(histlandmarkPad_temp~=0)=label(j);
        histlandmarkPad = histlandmarkPad+histlandmarkPad_temp;
    end   
end
imshow(HistPad,[])
title 'downsampled Histology image'
imwrite(rescale(HistPad),[outputdir,'/histDS.png']);
imwrite(AnotPad,[outputdir,'/anotDS.png']);
imwrite((uint8(histlandmarkPad)),[outputdir,'/histlandmarkDS.png']);
imwrite((mrilandmark),[outputdir,'/mrilandmarkDS.png']);

