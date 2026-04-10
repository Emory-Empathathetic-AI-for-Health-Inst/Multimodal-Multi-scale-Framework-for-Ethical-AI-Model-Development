%affine registration main
clear
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
addpath([parentFolder,'\01_preprocess'])
fixed = [parentFolder,'\example\mri.png'];
moving = [parentFolder,'\example\processed\histDS.png'];
anotation = [parentFolder,'\example\processed\histlandmarkDS.png'];
mask =  [parentFolder,'\example\processed\anotDS.png'];
outputdir = [parentFolder,'\example\processed\affine'];
mkdir (outputdir);
affineElastix(fixed,moving,anotation,mask,outputdir)
m = imread([outputdir,'/affine/image/result.tif']);
imwrite(rescale(m),[parentFolder,'\example\processed\affine_hist.png'])
m_annotation = imread([outputdir,'/affine/marker/result.tif']);
imwrite(m_annotation>50,[parentFolder,'\example\processed\affine_hist_landmark.png'])
m_mask = imread([outputdir,'/affine/mask/result.tif']);
imwrite(m_mask>50,[parentFolder,'\example\processed\affine_hist_mask.png'])
