function [stage,stagetrain] = stageraw2bin(stages_raw,stagetime_raw,bin,epoch,domaindivide)
%STAGERAW2BIN transforms stage time and stage val to binned stage

% sleep stage train
if bin<= epoch
    stagetrain = zeros(length(domaindivide)-1,1);
   for i = 1:length(stagetime_raw)
      stagetrain(epoch/bin*(i-1)+1:(epoch/bin)*i) = stages_raw(i); 
   end
else 
    stagetrain = stages_raw(histcounts(domaindivide,stagetime_raw)==1)';   % sleep stage train complete
end

% Transfer stage train to stage matrix
stage = zeros(length(domaindivide)-1,5);                       
stage(stagetrain==3,1)=1;                                   % N1
stage(stagetrain==2,2)=1;                                   % N2
stage(stagetrain==1,3)=1;                                   % N3
stage(stagetrain==4,4)=1;                                   % REM
stage(stagetrain==5|stagetrain==0|isnan(stagetrain),5)=1;   % WAKE

end