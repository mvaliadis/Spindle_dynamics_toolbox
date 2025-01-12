function plot_overview(EEG,res_table,X, BinData, ModelSpec)
   % Prepare data for figure
    binsize = ModelSpec.binsize;
    xtime = BinData.real_time + binsize/2;        % bin data time stamps 
    sta = BinData.sta;                            % stage binary matrix [N1,N2,N3,REM,Wake]  
    stagetrain = 3*sta(:,1)+ 2*sta(:,2)+ sta(:,3)+4*sta(:,4)+5*sta(:,5); % stagetrain in bin
    y = BinData.y;                                % spindle binary train
    sop = BinData.sop;                            % SO power in bin  
    phase = BinData.phase;                        % SO phase in bin  
    Fs = BinData.Fs;
    hard_cutoffs = ModelSpec.hard_cutoffs;

    % Compute multitaper spectrogram
    dsfreqs = 0.1;
    nfft = 2^(nextpow2(Fs/dsfreqs));
    [mt, stimes, sfreqs] = multitaper_spectrogram_mex(EEG, Fs,[8,19],[2,3],[1,0.05],nfft,'constant',[],false,false);
    
    % Extract fast spindle raw time and freq
    fast_inds = (res_table.peak_freqs{:} >= hard_cutoffs(1)) & (res_table.peak_freqs{:}< hard_cutoffs(2));
    spindletime_all = res_table.peak_ctimes{:};
    freq_all  = res_table.peak_freqs{:};
    fast_pt = spindletime_all(fast_inds);
    fast_pf = freq_all(fast_inds);
    
    % Extract raw SO power and phase
    phase_raw = cell2mat(res_table.SOphase);      % SO phase raw
    sop_raw = cell2mat(res_table.SOpow);          % SO power raw

    % Fit GLM Model
    disp('Model fitting ...')
    [b, ~, stats] = glmfit(X, y, 'poisson');
    disp('Model fitted')

    %% Generate the overview figure
    disp('Figure generating ...')
    figure('Name', 'Spindle Dynamics Overview', 'Position', [100, 50, 1400, 1000]);

    % --------------------------- Left Panel ---------------
    % 1) Spectrogram
    ax1 = subplot(7, 3, [1 2 4 5]); % Merge subplots
    hold on;
    imagesc(stimes, sfreqs, nanpow2db(mt));
    axis xy;
    ylabel('Frequency (Hz)');
    climscale;
    c = colorbar_noresize;
    colormap(gca, rainbow4);
    ylabel(c, 'Power (dB)');
    axis tight;
    plot(fast_pt, fast_pf, 'o', 'markersize', 6, 'MarkerFaceColor', 'm', 'MarkerEdgeColor', 'k', 'LineWidth', 1.5);
    title('Sleep EEG Spectrogram');
    scaleline(ax1, 10, '10 s');
    xlabel(" "+newline+" ")
    
    % 2) Spindle train
    ax2 = subplot(7, 3, [7 8]); % Merge subplots
    stem(fast_pt, ones(size(fast_pt)), 'Color', 'k', 'Marker', 'none', 'LineWidth', 1.5);
    set(ax2,'XTick', [],'YColor', 'none','box','off');
    ylim(ax2, [0 1.3]);
    title('Sleep Spindle Train');
    xlabel(" "+newline+"   ")

    % 3) Stage train
    ax3 = subplot(7, 3, [10 11]); % Merge subplots
    hold on;
    hypnoplot(xtime, stagetrain);
    plot(xtime(y == 1), stagetrain(y == 1), 'o', 'markersize', 6, 'MarkerFaceColor', 'm', 'MarkerEdgeColor', 'k', 'LineWidth', 1.5);
    title('Sleep Stage');
    xlabel(" "+newline+"   ")
    set(ax3, 'XTick', [])

    % 4) SO power
    ax5 = subplot(7, 3, [13 14]); % Merge subplots
    hold on;
    t = (0:length(EEG)-1)/Fs;
    plot(t, sop_raw, 'LineWidth', 1.5, 'Color', 'k');
    plot(xtime(y == 1), sop(y == 1), 'o', 'markersize', 6, 'MarkerFaceColor', 'm', 'MarkerEdgeColor', 'k', 'LineWidth', 1.5);
    ylabel('Power');
    title('Continuous Sleep Depth (SO Power)');
    set(ax5, 'XTick', [])

    % 5) SO phase
    ax6 = subplot(7, 3, [16 17]); % Merge subplots
    hold on;
    plot(t, phase_raw, 'k', 'LineWidth', 1.5);
    phase = wrapToPi(phase);
    plot(xtime(y == 1), phase(y == 1), 'o', 'markersize', 6, 'MarkerFaceColor', 'm', 'MarkerEdgeColor', 'k', 'LineWidth', 1.5);
    set(ax6, 'XTick', [],'YTick', [-pi 0 pi], 'YTickLabels', {'-\pi', '0', '\pi'}, 'ylim', [-pi pi]);
    yline(0, 'k--');
    ylabel('Phase');
    title('Cortical Up/Down State (SO Phase)');
   

    % 6) CIF
    ax7 = subplot(7, 3, [19 20]); % Merge subplots
    [CIF_sta, ~, ~] = glmval(b, X, 'log', stats); % Compute instantaneous spindle rate
    hold on;
    plot(xtime, CIF_sta * 60 / binsize, 'color', 'k', 'LineWidth', 2);
    plot(xtime(y == 1), CIF_sta(y == 1) * 60 / binsize, 'o', 'markersize', 6, ...
         'MarkerFaceColor', 'm', 'MarkerEdgeColor', 'k', 'LineWidth', 2);
    title(sprintf('Density = f (%s)', ModelSpec.FactorSelect));
    xlabel('Time (s)', 'FontSize', 12);
    ylabel({'Spindle Density'; '(events/min)'}, 'FontSize', 12);
    
    % Adjust position for CIF plot
    pos = get(ax7, 'Position');
    pos(4) = pos(4) + 0.05;
    pos(2) = pos(2) - 0.05;
    set(ax7, 'Position', pos);
    %scaleline(ax7, 5, '5 secs');
    
    % Link x-axes and scrollzoompan
    linkaxes([ax1, ax2, ax3, ax5, ax6, ax7], 'x');
    scrollzoompan(ax7, 'x');

        %--------------------- Right panel -----------------------
    % 1) Plot Polarhistogram
    ax4 = subplot(7, 3, [3 6 9]); % Define subplot location
    phasehistogram(phase(y==1),1,'NumBins',50); 
    rlim([0 .4])
    rticks(0:0.1:0.4)
    title('Spindle SO Phase Histogram',FontSize=12)
    
    % 2) Plot history Curve
    ax8 = subplot(7, 3, [12 15 18]); % Define subplot location
    if ModelSpec.BinarySelect(4)==1
        [xlag,yhat,yu,yl] = plot_hist_curve(stats,ModelSpec,BinData);
    end
        
    % Store axes handles in a cell array
    axesHandles = {ax1, ax2, ax3, ax5, ax6, ax7};
    
    % Loop through each axis and adjust properties
    for i = 1:length(axesHandles)
        currentAx = axesHandles{i};
        title(currentAx, currentAx.Title.String, 'FontSize', 10, 'FontWeight', 'bold'); 
        set(currentAx, 'FontSize', 10, 'box', 'off');
    end

end