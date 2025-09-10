% This script plot the 6 Pareto front for the different configurations of
% the tool.

clearvars
clearvars -global
clearvars figIdx
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

% Remove all entries that do not have weight [1, 1, 1]
resultsTable = resultsTable(strcmp(resultsTable.weights,"[1.0, 1.0, 1.0]"),:);

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

%% Count reqs for No Aggregation

fprintf("\tNo Aggregation\n\n")

% Filter by aggreggation method
resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,"no_aggregation"),:);
fprintf("Number of repaired requirements: %i\n",height(resultsTableTemp));

% Filter by correctness
resultsTableTemp = resultsTableTemp(resultsTableTemp.f_correctness == 0,:);
fprintf("Number of repaired requirements (corr = 0): %i\n",height(resultsTableTemp));

% Filter by semantic integrity
resultsTableTemp = resultsTableTemp(resultsTableTemp.f_des_semantic == 0,:);
fprintf("Number of repaired requirements (corr = 0 & semantic = 0): %i\n",height(resultsTableTemp));

% Median syntactic similarity
fprintf("Median Syntactic Similarity (corr = 0 & semantic = 0): %.3f\n",median(resultsTableTemp.f_des_syntactic))

% Median satisfaction extent
fprintf("Median Satisfaction Extent (corr = 0 & semantic = 0): %.3f\n",median(resultsTableTemp.f_des_satisfaction))

%% Count reqs for Weighted Sum

fprintf("\n\n\tWeighted Sum\n\n")

% Filter by aggreggation method
resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,"weighted_sum"),:);
fprintf("Number of repaired requirements: %i\n",height(resultsTableTemp));

% Filter by correctness
resultsTableTemp = resultsTableTemp(resultsTableTemp.f_correctness == 0,:);
fprintf("Number of repaired requirements (corr = 0): %i\n",height(resultsTableTemp));

% Filter by semantic integrity
resultsTableTemp = resultsTableTemp(resultsTableTemp.f_des_semantic == 0,:);
fprintf("Number of repaired requirements (corr = 0 & semantic = 0): %i\n",height(resultsTableTemp));

% Median syntactic similarity
fprintf("Median Syntactic Similarity (corr = 0 & semantic = 0): %.3f\n",median(resultsTableTemp.f_des_syntactic))

% Median satisfaction extent
fprintf("Median Satisfaction Extent (corr = 0 & semantic = 0): %.3f\n",median(resultsTableTemp.f_des_satisfaction))

