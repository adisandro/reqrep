% This script plot the 6 Pareto front for the different configurations of
% the tool.

clearvars
clearvars -global
close("all")
clc

%% Load results

% Define location of results file
fileOutput = "ToolOutput" + filesep + "results.csv";

% Read file
resultsTable = readtable(fileOutput,"VariableNamingRule","preserve");

% Drop last four columns
resultsTable.f_sem_taut = [];
resultsTable.f_sem_var_type = [];
resultsTable.f_sat_vertical = [];
resultsTable.f_sat_horizontal = [];

%% Get model name and requirement for each run

% Get config id column
configTemp = string(resultsTable.config_id);

% Split config id
strTemp = split(configTemp,"_");

% Save model, and requirement
resultsTable.model = strTemp(:,1);
resultsTable.requirement = strTemp(:,2);

% Reorder columns of the table
resultsTable = movevars(resultsTable,"model","Before",1);
resultsTable = movevars(resultsTable,"requirement","After","model");
resultsTable = movevars(resultsTable,"aggregation_strategy","After","requirement");
resultsTable = movevars(resultsTable,"weights","After","aggregation_strategy");

% Delete temporary variables
clear("*Temp")

%% Create table for plot points

% Get list of aggregation strategies and desirability metrics.
aggregationList = unique(string(resultsTable.aggregation_strategy));
desirabilityList = ["f_des_semantic"; "f_des_syntactic"; "f_des_satisfaction"];
modelList = unique(string(resultsTable.model));
weightList = unique(string(resultsTable.weights));

% Create empty table for point coordinates
pointTable = table('size', [length(aggregationList)*length(modelList)*length(weightList) 8], ...
    'VariableTypes', ["string","string","string",repmat("double",1,4),"string"], ...
    'VariableNames', ["aggregation","model","weight","f_correctness",desirabilityList',"label"]);

% Add aggregation mode to table
strTemp = repmat(aggregationList,1,length(modelList)*length(weightList));
pointTable.aggregation = reshape(strTemp',[],1);

% Add model name to table
strTemp = repmat(modelList,1,length(weightList));
pointTable.model = repmat(reshape(strTemp',[],1),length(aggregationList),1);

% Add weights to the table
pointTable.weight = repmat(weightList,length(aggregationList)*length(modelList),1);

% Delete temporary variables
clear("*Temp")

%% Fill table with points coordinates

% Define abbreviations for labels
aggregationStr = ["na"; "ws"];
weightStr = ["0, 1, 1"; "1, 0, 1"; "1, 1, 0"; "1, 1, 1"];

% Loop over each table row

%% Plot the graphs

% Define string list for desirability properties
desirabilityStr = ["$Semantic~Integrity$"; "$Syntactic~Similarity$"; "$Satisfaction~extent$"];

% Define list of markers and colors
markerList = ["o"; "+"; "x"; "*"; "^"; "square"]; % One marker for each model
colorList = ["b"; "r"; "m"; "c"]; % One color for each weight





