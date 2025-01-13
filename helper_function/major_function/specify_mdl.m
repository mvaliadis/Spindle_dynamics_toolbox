function [ModelSpec] = specify_mdl(BinarySelect,InteractSelect,varargin)
% SPECIFY_MDL wraps model specifications provided by user into a ModelSpec struct.
% 
% Input:
%       <Required inputs>
%       - BinarySelect: (1x4 vector, double), indicates which factors are selected by the user
%         Factors are with fixed order: SOphase, stage, SOpower,history
%         e.g., [1,1,0,1] means select SOphase, stage, and history as model components 
%       - InteractSelect: (1xn cell), each entry contains an interaction term in the form of A:B 
%         It is case,order-insensitive, and accept multipler separators including:':', '&', and '-'
%         n is the number of interactions. For example, we can add 2 interactions
%         e.g., {'stage:SOphase', 'stage:history'} 
%
%       <Optional inputs>
%       - hist_choice: (string), it is either 'short'(default) or 'long'
%                   'short': Short term history (up to 15 secs, this option runs fast)
%                   'long': Long term history (up to 90 secs, use this to show infraslow structure)
%       - control_pt: (1xk vector,double), spline control point location, k is the number of control points
%                    default: [0:15:90 120 150]
%       - binsize: (double), point process bin size in sec, default: 0.1 sec
%       - hard_cutoffs:(1x2 vector,double), frequency cutoff in Hz
%                      default:[12 16], choose events in 12 to 16 Hz as fast spindles
%       
% Output:
%       ModelSpec: A struct that contains all model specifications
%
% Example 1: BinarySelect = [1,1,0,1];                     
%            InteractSelect = {'stage:SOphase'};          
%            [ModelSpec] = specify_mdl_factor(BinarySelect,InteractSelect);
%
% Please provide the following citation for all use:
%       Shuqiang Chen,Mingjian He,Ritchie E. Brown, Uri T. Eden, Michael J Prerau, 
%       "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
%       PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
%
% Updated SChen 010725
%***********************************************************************************

%% Parse inputs
p = inputParser;
p.KeepUnmatched = true;

% Required inputs
addRequired(p, 'BinarySelect', @(x) validateattributes(x, {'numeric', 'vector'}, {'real','nonempty','numel', 4}));
addRequired(p, 'InteractSelect', @(x) isempty(x) || iscell(x));

% Optional inputs
addOptional(p, 'hist_choice','short', @(x) isempty(x) || any(validatestring(x, {'short', 'long'})));
addOptional(p, 'control_pt', [0:15:90 120 150],@(x) isempty(x) || (isnumeric(x) && isvector(x) && all(isfinite(x)) && isreal(x)));
addOptional(p, 'binsize',0.1,@(x) validateattributes(x, {'numeric', 'vector'}, {'real','nonempty','nonnan','positive'}));
addOptional(p, 'hard_cutoffs',[12 16], @(x) validateattributes(x, {'numeric', 'vector'}, {'real','nonempty','nonnan','nonnegative'}));

parse(p, BinarySelect, InteractSelect,varargin{:});
parser_results = p.Results;

%% Save Model Spec

% Add factors selected into the model spec
AllFactors = {'SOphase','stage','SOpower','history'};
FactorSelect = AllFactors(parser_results.BinarySelect==1);      % Selected model components
ModelSpec = parser_results; 
ModelSpec.FactorSelect = strjoin(FactorSelect, ', ');

% Add hist_ord to the model spec
if ~isempty(parser_results.control_pt)
    ModelSpec.hist_ord = parser_results.control_pt(end);        % history order in bin
    ModelSpec.hist_ord_s = parser_results.control_pt(end)*parser_results.binsize; % hist order in sec
end

% Report selected components and interactions
disp(['Selected modeling components: ', strjoin(FactorSelect, ', ')]);
if isempty(parser_results.InteractSelect)
    disp('Selected interactions -> None')
elseif ~isempty(parser_results.InteractSelect)&&any(ismember_interaction(parser_results.InteractSelect,{'stage:SOphase','SOpower:SOphase','stage:history'}))
    disp(['Selected interactions -> ', strjoin(parser_results.InteractSelect, ', ')]);
else
    error('Interaction term is not properly specified. It must be specified as a cell array containing a subset of the valid options: {''stage:SOphase'', ''SOphase:SOpower'', ''stage:history''}');
end

end

  