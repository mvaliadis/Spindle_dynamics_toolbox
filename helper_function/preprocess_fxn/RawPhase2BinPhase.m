function [SO_phase] = RawPhase2BinPhase(phase_raw,Fs,spindletime_raw,spindletrain,domaindivide)
%% Transform raw SO phase to align with binned spindle train
% s.t. SO phase is the exact value when spindle occurs
%      SO phase is the cir_mean value when no spindles occurs
%   Fs is the sampling freq of Raw phase, e.g. in MESA, SO: 256, resp: 32
% SC 040924

%% SO phase   
%phase_raw = cell2mat(res_table.SOphase);                % SO phase raw
phase_raw = unwrap(phase_raw);                          % unwrap the phase for taking avg
phase_time_raw = 1/Fs:1/Fs:length(phase_raw)/Fs;        % phase time

% Construct SO phase train
% 1) For phase train with spindle events, find the exact phase for each spindle 
spindle_idx = find(histcounts(spindletime_raw,phase_time_raw));
spindle_phase = phase_raw(spindle_idx);

% 2) For phase train without spindle events, take the mean of those falling into each bin 
bincount_phase = histcounts(phase_time_raw,domaindivide)';  
bincount_phase2 = cumsum(bincount_phase);
bincount_phase3 = bincount_phase2 - (bincount_phase-1);

phase_train1 = zeros(length(spindletrain),1);
for i = 1:length(phase_train1)
    phase_train1(i) = mean(phase_raw(bincount_phase3(i):bincount_phase2(i)));
end

% 3) Replace the exact phase when spindle occurs
SO_phase = phase_train1;
total_spikes = length(find(spindletrain==1));
SO_phase(spindletrain==1) = spindle_phase(1:total_spikes);

end