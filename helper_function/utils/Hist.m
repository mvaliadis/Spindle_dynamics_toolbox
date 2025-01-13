function [SpikeHist] = Hist(lag,spiketrain)
%HIST generates indicator-basis history
% Input: 
%       - lag, (double): history lag in bin
%       - spiketrain, (double,vector): binary train
% Output:
%       - SpikeHist, (double,matrix): indicator-basis history
%
% Created by SChen

SpikeHist = zeros(length(spiketrain)-lag,lag);

for i = 1:lag
    SpikeHist(:,i) = spiketrain(lag-i+1:end-i);     % Shift the train
end

end