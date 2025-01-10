function [SpikeHist] = Hist(lag,spiketrain)

SpikeHist = zeros(length(spiketrain)-lag,lag);

for i=1:lag
    SpikeHist(:,i)=spiketrain(lag-i+1:end-i);
end

end