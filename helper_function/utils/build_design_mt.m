function [X] = build_design_mt(ModelSpec,BinData)
% BUILD_DESIGN_MT constructs a design matrix based on the factors selected by the user.
% Factors with fixed order: SOphase, stage, SOpower,history
% 
% Input:
%       - ModelSpec, (struct): Model specifications
%       - BinData, (struct): All binned data 
%
% Output:
%       - X (double,matrix): Design matrix 
%
%
% Please provide the following citation for all use:
%       Shuqiang Chen,Mingjian He,Ritchie E. Brown, Uri T. Eden, Michael J Prerau, 
%       "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
%       PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
%
% Last updated, SChen 010725
%**********************************************************************************

%% Deal with inputs

% Extract model specifications
interactions = ModelSpec.InteractSelect;
BinarySelectStr = num2str(ModelSpec.BinarySelect, '%d');
BinarySelectStr = strrep(BinarySelectStr, ' ', ''); % Convert binary array to a string number

% Extract factors
sta = BinData.sta;
sop = BinData.sop;
phase = BinData.phase;
sp_hist = BinData.sp_hist;
RW = BinData.RW;

% Rescale SOP to avoid numerical issues in model fitting
% Alternative: Standardize SOP, more robust 
sop = sop/5;
scale_factor = 10;

% Initialize X
X = [];
%% Construct design matrix
% 1) Without interactions______________________________________________________
if isempty(interactions)
    switch BinarySelectStr
        % Single factor
        case '0000' % No factors, NREM sleep
            X = RW;                             
        case '1000' % phase alone
            X = [RW cos(phase) sin(phase)];     
        case '0100' % stage alone
            X = sta(:,[1 3:5]);                
        case '0010' % sop alone
            X = [RW sop (sop.^2)/scale_factor]; 
        case '0001' % history alone
            X = [RW sp_hist];                   
        % Two-factor
        case '1100' % phase + stage
            X = [sta(:,[1 3:5]) cos(phase) sin(phase)]; 
        case '1010' % phase + sop
            X = [RW sop (sop.^2)/scale_factor cos(phase) sin(phase)]; 
        case '1001' % phase + hist
            X = [RW cos(phase) sin(phase) sp_hist];      
        case '0101' % stage + hist
            X = [sta(:,[1 3:5]) sp_hist];                  
        case '0011' % sop + hist
            X = [RW sop (sop.^2)/scale_factor sp_hist];  
        % Three-factor
        case '1101' % sta,phase,hist
            X = [sta(:,[1 3:5]) cos(phase) sin(phase) sp_hist];
        case '1011' % sop,phase,hist
            X = [RW sop (sop.^2)/scale_factor cos(phase) sin(phase) sp_hist];
        otherwise
            error('The model components are not properly specified.')
    end

% 2) With only stage:SOphase interaction ______________________________________________________
elseif all(ismember_interaction(interactions,{'stage:SOphase'}))
     switch BinarySelectStr
        case '1100' % phase + stage
            X = [cos(phase) sin(phase) sta(:,[1 3:5]) sta(:,[1 3:5]).*cos(phase) sta(:,[1 3:5]).*sin(phase)];
        case '1101' % sta,phase,hist
            X = [cos(phase) sin(phase) sta(:,[1 3:5]) sta(:,[1 3:5]).*cos(phase) sta(:,[1 3:5]).*sin(phase) sp_hist];
     end

% 3) With only SOpower:SOphase interaction ______________________________________________________
elseif all(ismember_interaction(interactions,{'SOpower:SOphase'}))
    switch BinarySelectStr
        case '1010' % phase + sop
            X = [RW sop (sop.^2)/scale_factor cos(phase) sin(phase) ...
                 cos(phase).*sop  cos(phase).*(sop.^2)/scale_factor ...
                 sin(phase).*sop  sin(phase).*(sop.^2)/scale_factor];
        case '1011' % sop,phase,hist
            X = [RW sop (sop.^2)/scale_factor cos(phase) sin(phase) ...
                 cos(phase).*sop  cos(phase).*(sop.^2)/scale_factor ...
                 sin(phase).*sop  sin(phase).*(sop.^2)/scale_factor sp_hist];
    end

 % 4) With both stage：SOphase AND stage：history interactions ___________________________
 elseif all(ismember_interaction(interactions,{'stage:SOphase','stage:history'}))&&all(ModelSpec.BinarySelect == [1 1 0 1])
            X = [cos(phase) sin(phase) sta(:,[1 3:5]) sta(:,[1 3:5]).*cos(phase) sta(:,[1 3:5]).*sin(phase) ...
                 sp_hist sta(:,2).*sp_hist sta(:,3).*sp_hist];
 else
        error('Model component or interaction term is not properly specified')
end
 
if isempty(X)
    error('Model component or interaction term is not properly specified')
end

end
