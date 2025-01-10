function [xlag,yhat,yu,yl] = plot_hist_curve(stats,ModelSpec,BinData)
% PLOT_HIST_CURVE computes history modulation value and plot history curve
% Input:
%       -stats (struct), results after model fitting 
%       -ModelSpec (struct), model specifications
%       -BinData, (struct), binned data
%
% Output:
%       -xlag (n x 1 vector), history time lag in sec
%       -yhat (n x k vector), history modulation value
%       -yu (n x k vector), history curve 95% confidence interval (upper)
%       -yl (n x k vector), history curve 95% confidence interval (lower)
%       Note: k = 1 when single history curve is computed
%             k = 2 when N2 and N3 history curve are computed, 
%               in which case, 1st col means N2 history, 2nd col means N3 history
%             n is determined by history lag and sp_resol (n = history lag in bin / sp_resol)
%
% Add Single History VS N2 N3 History
% Add History Features
%
% Created by SC 010625 SC
%******************************************************************************************************************************************
if ModelSpec.BinarySelect(4) == 1
%% Prepare for the figure
b = stats.beta;              % fitted parameters 
sp_resol = 0.1;              % Evaluate spline in a finer resolution
[sp_finer] = FinerModCardinalSpline(ModelSpec.hist_ord,ModelSpec.control_pt,.5,sp_resol);

% time lag in sec
xlag = (ModelSpec.binsize*sp_resol:ModelSpec.binsize*sp_resol:ModelSpec.hist_ord*ModelSpec.binsize)';

    %% Evaluate history modulation curve
    %--- If single history curve is specified
    if length(ModelSpec.InteractSelect)==1
        sizediff = length(b)-1 - size(BinData.sp,2); % num of non-history columns in design matrix
        [yhat0,yl0,yu0] = glmval(b,[zeros(ModelSpec.hist_ord/sp_resol,sizediff) sp_finer],'log',stats);
        yl = (yhat0 - yl0)/exp(b(1));
        yu = (yhat0 + yu0)/exp(b(1));
        yhat = yhat0/exp(b(1));
        
        % figure
        shadebounds(xlag,yhat,yu,yl,'k',[.5,.5,.5],[.9,.9,.9],.4);
        stem(BinData.isis, -0.2*ones(length(BinData.isis),1),'Color','k', 'Marker', 'none','linewidth',.05);
        yline(1,'k--')
        xlim([0 ModelSpec.hist_ord*ModelSpec.binsize])
        ylim([-0.2 2])
        xlabel('Time Lag (sec)')
        ylabel('Rate Multiplier')
        title('History Modulation');
        set(gca,'XTick',0:5:ModelSpec.hist_ord*ModelSpec.binsize,'fontsize',12)
    
    %--- If stage-dependent history is specified
    elseif length(ModelSpec.InteractSelect)==2
        sizediff = length(b)-1 - 3*size(BinData.sp,2); % num of non-history columns in design matrix
        % Compute N2 history curve
        [y2,yl2,yh2] = glmval(b,[zeros(ModelSpec.hist_ord/sp_resol,sizediff) sp_finer sp_finer zeros(size(sp_finer))],'log',stats);
        yl2 = (y2 - yl2)/exp(b(1));
        yu2 = (y2 + yh2)/exp(b(1));
        y2 = y2/exp(b(1));
        
        % Compute N3 history curve
        [y3,yl3,yh3] = glmval(b,[zeros(ModelSpec.hist_ord/sp_resol,sizediff) sp_finer zeros(size(sp_finer)) sp_finer],'log',stats);
        yl3 = (y3 - yl3)/exp(b(1));
        yu3 = (y3 + yh3)/exp(b(1));
        y3 = y3/exp(b(1));
    
        % Save results
        yl = [yl2 yl3];
        yu = [yu2 yu3];
        yhat = [y2 y3];
    
        % figure
        hold on;
        s1 = shadebounds(xlag,y2,yu2,yl2,'b','b','none',.2);
        s2 = shadebounds(xlag,y3,yu3,yl3,'m','m','none',.2);
        stem(BinData.isis, -0.2*ones(length(BinData.isis),1),'Color','k', 'Marker', 'none','linewidth',.05);
        yline(1,'k--')
        xlim([0 ModelSpec.hist_ord*ModelSpec.binsize])
        ylim([-0.2 2])
        xlabel('Time Lag (sec)')
        ylabel('Rate Multiplier')
        title('History Modulation');
        legend([s1,s2],{'N2 History Curve','N3 History Curve'})
        set(gca,'XTick',0:5:ModelSpec.hist_ord*ModelSpec.binsize,'fontsize',12)
    end

else
    error('History component is not selected by the user')
end


end