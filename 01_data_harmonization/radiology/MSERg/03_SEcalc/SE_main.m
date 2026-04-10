clear all
%%the spectral embedding representation calculation
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
addpath([currentFolder,'/feature_extraction']);
HISTURL = [parentFolder,'/example/processed/affine_hist.png'];  
HISTmask = [parentFolder,'/example/processed/affine_hist_mask.png'];   
RegOutputFolder = [parentFolder,'\example/processed/hist_rep'];
mkdir(RegOutputFolder);
scaleIndex =[1,2,3,4,5,6,7,8];% set the scale size that needed in the multiscale resolution
REP_calc_clinic(HISTURL, HISTmask,RegOutputFolder,scaleIndex)
HISTURL = [parentFolder,'/example/mri.png'];  
HISTmask = [parentFolder,'/example/mri_mask.png'];   
RegOutputFolder = [parentFolder,'\example/processed/mri_rep'];
mkdir(RegOutputFolder);
scaleIndex =[1,2,3,4,5,6,7,8];% set the scale size that needed in the multiscale resolution
REP_calc_clinic(HISTURL, HISTmask,RegOutputFolder,scaleIndex)
load ([parentFolder,'\example/processed/mri_rep/spectral_represent.mat']);
mriSE = v;
load ([parentFolder,'\example/processed/hist_rep/spectral_represent.mat']);
histSE = v;
for j = 1:8
    scalename = sprintf('scale%d',j);
    writeDIR = [parentFolder,'\example/processed/Scale_rep/',scalename];
    mkdir(writeDIR)
    for seindex = 1:3
    histSEname = sprintf('histSE_%d.png',seindex);
    mriSEname = sprintf('mriSE_%d.png',seindex);
    histSEtemp = rescale(squeeze(histSE(j,:,:,seindex)));
    mriSEtemp = rescale(squeeze(mriSE(j,:,:,seindex)));
    imwrite(histSEtemp,[writeDIR,'/',histSEname])
    imwrite(mriSEtemp,[writeDIR,'/',mriSEname])       
    end
end
