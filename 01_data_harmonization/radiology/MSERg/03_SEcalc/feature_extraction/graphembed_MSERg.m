function [v,wsse] = graphembed(data,m)
% [v,wsse] = graphembed(vols,m) 
% [V,WSSE] = GRAPHEMBED(X,M) Graph Embedding
% 
% X is NxD matrix of N samples with D dimensions. V are the Nxm embeddings.
% WSSE are the weighted sum of squared errors for each column of V.
% James Monaco
% Edit - Uses PDIST to calculate distance matrix
% (SV)

    %addpath ~/Code/matlabcode/distmtx/

	debug = false;

    if m >= size(data,2)
        %error('m must be < size(X,2).');
         v = data;
         wsse = 0;
         1111111111111111111
    end
    if isa(data,'single'), data = double(data); end;

	% PDIST uses N x D
	W = squareform(pdist(real(data)));
	clear data
	W = exp(-W/max(W(:)));
	%W = exp(-W/1000);
    
    if debug
	    D = diag(sum(W));
	    %L = D - W; %#ok<NASGU>
    end
    
    if debug, disp('Calculating normalized cuts..'); end;
	ds = 1./sqrt(sum(W));

	%Right and left multiply by D^{-1/2}.
	for j=1:size(W,1)
	  W(j,:) = W(j,:).*ds;
	end
	for j=1:size(W,2)
	  W(:,j) = W(:,j).*ds';
	end

	options.disp = 0; options.isreal = 1; options.issym = 1;
    [v,d] = eigs(W,m+1,'LR',options);
	[d,sind] = sort(diag(d),'descend');
	v = v(:,sind(2:end));
	d = d(2:end);

	%Left multiply by D^{-1/2}.
	for j=1:m
	  v(:,j) = v(:,j).*ds';
	end

	wsse = 2*d;

	if debug
	    %L = diag(sum(W)) - W;
	    disp('********************* DEBUG ************************');
	    wsse/2 %#ok<NOPRT>
	    v'*D*v %#ok<NOPRT>
	    %v'*L*v %#ok<NOPRT>
	    disp('********************* DEBUG ************************');
	end

end
