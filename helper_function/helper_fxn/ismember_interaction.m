function tf = ismember_interaction(targetInteraction, interactionsList)
%ISMEMBER_INTERACTION finds which target interaction is in the list
%
% This function is generalized to:
% * Be case-insensitive: Comparisons ignore capitalization.
% * Be order-insensitive: The order of components (e.g., 'A:B' and 'B:A') does not matter.
% * Handle multiple separators: Recognizes and treats ':', '&', and '-' as equivalent split symbols.
%
% Example:
%         interactions = {'stage:SOphase', 'stage:history'};
%         target_interaction = {'soPHASE&stage','stage:SOpower'};
%         tf = ismember_interaction(target_interaction, interactions);
% This will output tf as [1 0], a 1x2 logical array
%                        where logical 1 means target(1) is in the list
%                              logical 0 means target(2) is not in the list
%
% Accompanying with Chen et al., PNAS, 2025
% Created SC 111524
% Updated SC 123024
% ********************************************************************

%%
    % Function to normalize the string
    normalize = @(s) strjoin(sort(split(regexprep(lower(s), '[:&-]', ':'), ':')), ':');
    
    % Normalize the list of interactions
    normalizedInteractionsList = cellfun(normalize, interactionsList, 'UniformOutput', false);
    
    % Normalize the target interaction(s)
    if iscell(targetInteraction)
        % If targetInteraction is a cell array, normalize each element
        normalizedTarget = cellfun(normalize, targetInteraction, 'UniformOutput', false);
    else
        % If targetInteraction is a single string, normalize directly
        normalizedTarget = {normalize(targetInteraction)};
    end
    
    % Check for matches for all normalized target interactions
    tf = ismember(normalizedTarget, normalizedInteractionsList);
end
