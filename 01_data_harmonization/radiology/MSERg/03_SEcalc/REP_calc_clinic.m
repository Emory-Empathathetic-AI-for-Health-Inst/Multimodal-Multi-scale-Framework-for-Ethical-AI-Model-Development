function REP_calc_clinic(MRIpath,MRImask,outElastix,scaleIndex)
 fixed = imread(MRIpath);
 fixedmask = imread(MRImask);
%% feature extraction
concateImage = fixed;
mask =fixedmask(:,:,1)~=0;

GRAYLEVELS = 256;
scaleIndex =scaleIndex(scaleIndex~=0);
for i = 1:length(scaleIndex)
frequency =scaleIndex(i);
[ICs] = featICA(concateImage, mask, GRAYLEVELS,frequency);

fprintf('This scale: feature extration and ICA done. ')
%% spectral embedding
[out_emb,wsse]=graphembed_MSERg(ICs',3);
out_emb = rescale(out_emb)*255;
mask_vec = reshape(mask,[],1);
v_reshaped = zeros(size(mask_vec,1),3);
ICA_v = zeros(size(mask_vec,1),size(ICs,1));
subindex = 1;
for index = 1:size(mask_vec,1)
    if (mask_vec(index) ~= 0)
        v_reshaped(index,:) = out_emb(subindex,:);
        ICA_v(index,:) = ICs(:,subindex);
        subindex = subindex + 1;
    end
end
v(i,:,:,:) = reshape(v_reshaped(:,:,:), size(concateImage,1), size(concateImage,2), 3);
ICA{i} = {reshape(ICA_v(:,:,:), size(concateImage,1), size(concateImage,2), size(ICs,1))};
% fprintf('This scale: spectral embedding done. ')
end
save([outElastix,'/spectral_represent.mat'],'v','ICA')

end