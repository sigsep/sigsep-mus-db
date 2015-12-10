function [SDR,ISR,SIR,SAR] = bss_eval(ie,i,win,ove)

[nsampl,~,nsrc] = size(ie);
nwin = floor((nsampl-win+1+ove)/ove);
SDR = zeros(nsrc,nwin);
ISR = zeros(nsrc,nwin);
SIR = zeros(nsrc,nwin);
SAR = zeros(nsrc,nwin);
for k = 1:nwin
    K = (k-1)*ove+1:(k-1)*ove+win;
    [SDR(:,k),ISR(:,k),SIR(:,k),SAR(:,k)] = bss_eval_images(ie(K,:,:),i(K,:,:));
end

function [SDR,ISR,SIR,SAR] = bss_eval_images(ie,i)

nsrc = size(ie,3);
SDR = zeros(nsrc,1);
ISR = zeros(nsrc,1);
SIR = zeros(nsrc,1);
SAR = zeros(nsrc,1);
for j = 1:nsrc
    [s_true,e_spat,e_interf,e_artif] = bss_decomp_mtifilt(ie(:,:,j),i,j,512);
    [SDR(j,1),ISR(j,1),SIR(j,1),SAR(j,1)] = bss_image_crit(s_true,e_spat,e_interf,e_artif);
end

function [s_true,e_spat,e_interf,e_artif] = bss_decomp_mtifilt(se,s,j,flen)

nchan = size(se,2);
s_true = [s(:,:,j);zeros(flen-1,nchan)];
e_spat = project(se,s(:,:,j),flen)-s_true;
e_interf = project(se,s,flen)-s_true-e_spat;
e_artif = [se;zeros(flen-1,nchan)]-s_true-e_spat-e_interf;

function sproj = project(se,s,flen)

[nsampl,nchan,nsrc] = size(s);
s = reshape(s,[nsampl,nchan*nsrc]);
s = [s;zeros(flen-1,nchan*nsrc)];
se = [se;zeros(flen-1,nchan)];
fftlen = 2^nextpow2(nsampl+flen-1);
sf = fft(s',fftlen,2);
sef = fft(se',fftlen,2);

G = zeros(nchan*nsrc*flen);
for k1 = 0:nchan*nsrc-1
    for k2 = 0:k1
        ssf = sf(k1+1,:).*conj(sf(k2+1,:));
        ssf = real(ifft(ssf));
        ss = toeplitz(ssf([1,fftlen:-1:fftlen-flen+2]),ssf(1:flen));
        G(k1*flen+1:k1*flen+flen,k2*flen+1:k2*flen+flen) = ss;
        G(k2*flen+1:k2*flen+flen,k1*flen+1:k1*flen+flen) = ss';
    end
end

D = zeros(nchan*nsrc*flen,nchan);
for k = 0:nchan*nsrc-1
    for i = 1:nchan
        ssef = sf(k+1,:).*conj(sef(i,:));
        ssef = real(ifft(ssef,[],2));
        D(k*flen+1:k*flen+flen,i) = ssef(:,[1,fftlen:-1:fftlen-flen+2])';
    end
end

C = G\D;
C = reshape(C,flen,nchan*nsrc,nchan);
sproj = zeros(nsampl+flen-1,nchan);
for k = 1:nchan*nsrc
    for i = 1:nchan
        sproj(:,i) = sproj(:,i)+fftfilt(C(:,k,i),s(:,k));
    end
end

function [SDR,ISR,SIR,SAR] = bss_image_crit(s_true,e_spat,e_interf,e_artif)

s_true = s_true(:);
e_spat = e_spat(:);
e_interf = e_interf(:);
e_artif = e_artif(:);
SDR = 10*log10(sum(s_true.^2)/sum((e_spat+e_interf+e_artif).^2));
ISR = 10*log10(sum(s_true.^2)/sum(e_spat.^2));
SIR = 10*log10(sum((s_true+e_spat).^2)/sum(e_interf.^2));
SAR = 10*log10(sum((s_true+e_spat+e_interf).^2)/sum(e_artif.^2));
