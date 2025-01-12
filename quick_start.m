function quick_start
    % Create a separate floating window for options
    optionsFig = uifigure('Name', 'Quick Start GUI', 'Position', [1050, 100, 300, 500]);

    % Data loading options
    uilabel(optionsFig, 'Position', [20, 450, 200, 20], 'Text', '1. Load Data:');
    btnExampleData = uibutton(optionsFig, 'Text', 'Load Example Data', ...
        'Position', [20, 420, 120, 30], ...
        'ButtonPushedFcn', @(btn, event) loadExampleData());
    btnUserData = uibutton(optionsFig, 'Text', 'Load User Data', ...
        'Position', [150, 420, 120, 30], ...
        'ButtonPushedFcn', @(btn, event) loadUserData());

    % Display data status
    dataStatusLabel = uilabel(optionsFig, 'Position', [20, 390, 260, 20], ...
        'Text', 'No data loaded', 'HorizontalAlignment', 'left');

    % Checkboxes for selecting factors
    uilabel(optionsFig, 'Position', [20, 360, 200, 20], 'Text', '2. Select Factors:');
    cbSOphase = uicheckbox(optionsFig, 'Text', 'SOphase', 'Position', [20, 330, 100, 20]);
    cbStage = uicheckbox(optionsFig, 'Text', 'Stage', 'Position', [120, 330, 100, 20]);
    cbSOpower = uicheckbox(optionsFig, 'Text', 'SOpower', 'Position', [20, 300, 100, 20]);
    cbHistory = uicheckbox(optionsFig, 'Text', 'History', 'Position', [120, 300, 100, 20], ...
        'ValueChangedFcn', @(src, event) toggleHistoryChoice());

    % Radio buttons for history choice
    uilabel(optionsFig, 'Position', [20, 270, 200, 20], 'Text', '3. History Choice:');
    bgHist = uibuttongroup(optionsFig, 'Position', [20, 220, 200, 40], 'Enable', 'off'); % Initially disabled
    rbShort = uiradiobutton(bgHist, 'Text', 'Short-term (15 sec)', 'Position', [10, 20, 150, 20]);
    rbLong = uiradiobutton(bgHist, 'Text', 'Long-term (90 sec)', 'Position', [10, 0, 150, 20]);
    rbLong.Value = true; % Default to "long"

    % Dropdown for interaction terms
    uilabel(optionsFig, 'Position', [20, 190, 200, 20], 'Text', '4. Select Interactions:');
    ddInteract = uidropdown(optionsFig, 'Position', [20, 160, 200, 22], ...
        'Items', {'None', 'stage:SOphase', 'SOpower:SOphase', 'stage:SOphase, stage:history'}, ...
        'Value', 'None'); % Default to "None"

    % "Run Model" button
    btnRun = uibutton(optionsFig, 'Text', 'Run the Model', ...
                      'Position', [20, 50, 150, 30], ...
                      'ButtonPushedFcn', @(btn, event) runModel());

    % Initialize variables to store data
    dataLoaded = false;
    EEG = [];
    Fs = [];
    stage_val = [];
    stage_time = [];

    % Function to toggle History Choice availability
    function toggleHistoryChoice()
        if cbHistory.Value
            bgHist.Enable = 'on';  % Enable history choice options
        else
            bgHist.Enable = 'off'; % Disable history choice options
        end
    end

    % Function to load example data
    function loadExampleData()
        data_path = 'example_data/';
        load([data_path, 'example_data1.mat'], 'EEG', 'Fs', 'stage_val', 'stage_time'); % Replace with your actual variables
        dataLoaded = true;
        dataStatusLabel.Text = 'Example data loaded successfully!';
    end

    % Function to load user data
    function loadUserData()
        [file, path] = uigetfile('*.mat', 'Select Data File');
        if isequal(file, 0)
            dataStatusLabel.Text = 'User canceled data selection.';
        else
            try
                loadedData = load(fullfile(path, file)); % Load user-selected file
                if isfield(loadedData, 'EEG') && isfield(loadedData, 'Fs') && ...
                   isfield(loadedData, 'stage_val') && isfield(loadedData, 'stage_time')
                    EEG = loadedData.EEG;
                    Fs = loadedData.Fs;
                    stage_val = loadedData.stage_val;
                    stage_time = loadedData.stage_time;
                    dataLoaded = true;
                    dataStatusLabel.Text = ['User data loaded: ', file];
                else
                    uialert(optionsFig, 'Invalid data format. Expected variables: EEG, Fs, stage_val, stage_time.', 'Load Error');
                end
            catch ME
                uialert(optionsFig, ['Error loading file: ', ME.message], 'Load Error');
            end
        end
    end

    % Function to run the model and generate a separate figure
    function runModel()
        % Ensure data is loaded
        if ~dataLoaded
            uialert(optionsFig, 'No data loaded. Please load example or user data.', 'Data Missing');
            return;
        end

        % Get user inputs
        factors = [cbSOphase.Value, cbStage.Value, cbSOpower.Value, cbHistory.Value];
        selectedInteraction = ddInteract.Value;
        switch selectedInteraction
            case 'None'
                InteractSelect = {};
            case 'stage:SOphase'
                InteractSelect = {'stage:SOphase'};
            case 'SOpower:SOphase'
                InteractSelect = {'SOpower:SOphase'};
            case 'stage:SOphase, stage:history'
                InteractSelect = {'stage:SOphase', 'stage:history'};
        end
        hist_choice = 'long'; % Default to 'long'
        if rbShort.Value
            hist_choice = 'short';
        end

        % Validate inputs
        if ~any(factors)
            uialert(optionsFig, 'Please select at least one factor.', 'Input Error');
            return;
        end

        % Call preprocessing and fitting function
        BinarySelect = double(factors); % Convert logical to numeric
        [X, BinData, ModelSpec, res_table] = preprocessToDesignMatrix(BinarySelect, InteractSelect, hist_choice, EEG, Fs, stage_val, stage_time);

        % Generate the overview figure in a new window
        plot_overview(EEG, res_table, X, BinData, ModelSpec);
    end
end
