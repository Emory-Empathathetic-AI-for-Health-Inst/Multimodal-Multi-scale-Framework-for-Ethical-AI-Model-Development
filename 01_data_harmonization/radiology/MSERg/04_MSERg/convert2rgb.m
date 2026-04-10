function I = convert2rgb(MSERgimg,mask)

a1 = MSERgimg.*mask;
a2 = MSERgimg.*mask;
a3=MSERgimg.*mask;
a1(find(a1~=0))=a1(find(a1~=0))+860;
a1 = rescale(a1)*249;
a2(find(a2~=0))=a2(find(a2~=0))+13;
a2 = rescale(a2)*255;
a3(find(a3~=0))=a3(find(a3~=0))+202;
a3 = rescale(a3)*252;
I = cat(3,a1,a2,a3);
I = uint8(I);
imshow(I)
end