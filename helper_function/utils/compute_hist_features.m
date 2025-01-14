function [hist_features] = compute_hist_features(xlag,yhat,yl,yu)
%COMPUTE_HIST_FEATURES computes history features from the history curve
% Input:
%      -yhat (double): history curve values
%      -yl (double): 95% CI lower bound
%      -yu (double): 95% CI upper bound
% Output:
%      -hist_features: A struct that has all history features, including
%          --ref_period： refractory period (s)
%          --exc_period: excited period(s)
%          --p_time: peak time (s)
%          --p_height: peak height
%          --AUC_is: area under infraslow period (40 - 70) sec
%       
% Last updated, SChen 010725
%******************************************************************************************************************************************

%% Compute hist features 
xbin = xlag(2)-xlag(1);

% compute upper bound gradient
yu_g = gradient(yu);

% sig ref period
idx_over1= find(yu>1&yu_g>=0&yhat<1,1);
ref_period = xlag(idx_over1);

% find all peaks
[p_h,p_locs,~,~] = findpeaks(yhat,'MinPeakHeight',1,'WidthReference','halfheight');

%---- choose the first sig peak----
% 1) compute periods with LB >= 1
[run_len, run_inds, yes_vector] = consecutive_runs(yl>=1, 1, inf, 1);

% 2) valid peaks
valid_peak = yes_vector(p_locs)== 1;

% 3) Find first valid peak idx
valid_peak_idx = find(valid_peak==1,1);

% 4) if LB is always< 1, choose first peak as the peak, set pw = 0, compute pt and ph
if isempty(valid_peak_idx)||xlag(p_locs(valid_peak_idx))>=8  
    [m_h,m_idx] = max(yhat(1:800));
    p_height = min(1,m_h);
    p_time = xlag(m_idx);
    exc_period = 0;

else % Find corresponding runs contains valid peak, use run length as peak width
    p_height = p_h(valid_peak_idx);
    p_time = xlag(p_locs(valid_peak_idx));
    idx_contain_pk = []; 
    for j = 1:length(run_inds)
        if any(run_inds{j} == p_locs(valid_peak_idx))
            idx_contain_pk = j;
            break;
        end
    end
    exc_period = run_len(idx_contain_pk)*xbin;
end

% Save results
hist_features = struct();
hist_features.ref_period = ref_period;
hist_features.exc_period = exc_period;
hist_features.p_time = p_time;
hist_features.p_height = p_height;

% Save infraslow multiplier only when 
if xlag(end) > 1500
    is_left = 40/xbin;
    is_right = 70/xbin;
    is_length = (is_right-is_left)*xbin;
    AUC_is = sum((yhat(is_left:is_right))*xbin)/is_length;
    hist_features.AUC_is = AUC_is;
end

end