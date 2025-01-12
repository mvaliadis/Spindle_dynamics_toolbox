function [X, BinData, ModelSpec,res_table] = preprocessToDesignMatrix(BinarySelect, InteractSelect, hist_choice, EEG, Fs, stage_val, stage_time)
    % Ensure required inputs are provided
    if isempty(EEG) || isempty(Fs) || isempty(stage_val) || isempty(stage_time)
        error('EEG, Fs, stage_val, and stage_time must be provided.');
    end

    disp('Data preprocessing started...');

    % Preprocess EEG data
    binsize = 0.1; % Bin size in seconds
    hard_cutoffs = [12, 16]; % Frequency range for fast spindles

    % Compute spindle events and their properties
    [res_table] = eegToEventSignal(EEG, Fs, stage_val, stage_time);

    % Convert event data to binned data
    [BinData] = rawToBinData(res_table, Fs, binsize, hard_cutoffs, hist_choice);
    disp('Data preprocessing complete.');

    % Define control points based on history choice
    switch lower(hist_choice)
        case 'short'
            hist_ord = 15 / binsize;
            control_pt = [0:15:90 120 hist_ord];
        case 'long'
            hist_ord = 90 / binsize;
            control_pt = [0:15:90 120 150:100:750 hist_ord];
    end

    % Specify model based on user inputs
    ModelSpec = specify_mdl(BinarySelect, InteractSelect, ...
                             'hist_choice', hist_choice, ...
                             'control_pt', control_pt);

    % Build design matrix for the specified model
    X = build_design_mt(ModelSpec, BinData);
    disp('Design Matrix complete.');
    
end
