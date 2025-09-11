% This script plots the boxplot for the Syntactic Similarity and
% Satisfaction Extent for all the case studies.

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

% Remove all entries that do not have weight [1, 1, 1]
resultsTable = resultsTable(strcmp(resultsTable.weights,"[1.0, 1.0, 1.0]"),:);

% Remove requirements with Correctness > 0
resultsTable = resultsTable(resultsTable.f_correctness == 0,:);

% Remove requirements with Semantic Integrity > 0
resultsTable = resultsTable(resultsTable.f_des_semantic == 0,:);

% Reorder columns of the table
resultsTable = movevars(resultsTable,"model","Before",1);
resultsTable = movevars(resultsTable,"requirement","After","model");
resultsTable = movevars(resultsTable,"aggregation_strategy","After","requirement");
resultsTable = movevars(resultsTable,"weights","After","aggregation_strategy");

% Delete temporary variables
clear("*Temp")

%% Make table with median values for each aggragation method and model

% Get list of aggregation methods and models
aggList = unique(string(resultsTable.aggregation_strategy));
modelList = unique(string(resultsTable.model));
modelList = sort(modelList);

% Create empty table for point coordinates
desTable = table('size', [length(aggList)*length(modelList) 5], ...
    'VariableTypes', ["string","string","string","double","double"], ...
    'VariableNames', ["aggregation","model","weight","syntactic","satisfaction"]);

% Add aggregation mode to table
strTemp = repmat(aggList,1,length(modelList));
desTable.aggregation = reshape(strTemp',[],1);

% Add model name to the table
desTable.model = repmat(modelList,length(aggList),1);

% Add weight to the table
desTable.weight = repmat("[1.0, 1.0, 1.0]",height(desTable),1);

% Loop over each row of the table
for ii = 1:height(desTable)

    % Filter out result table
    resultsTableTemp = resultsTable(strcmp(resultsTable.model,desTable.model(ii)) & ...
        strcmp(resultsTable.aggregation_strategy,desTable.aggregation(ii)), :);

    % Compute median values
    desTable.syntactic(ii) = median(resultsTableTemp.f_des_syntactic);
    desTable.satisfaction(ii) = median(resultsTableTemp.f_des_satisfaction);

    % Delete temporary variables
    clear("*Temp")
end

% Print out table
disp(desTable)

% Save table
writetable(desTable,"MedianDesirability.csv")

%% Loop over aggregation methods

% Set list of desirability properties
desirabilityList = ["f_des_syntactic"; "f_des_satisfaction"];
desirabilityShort = ["Synt"; "Satis"];
desirabilityStr = ["$Syntactic~Similarity$"; "$Satisfaction~extent$"];
% desirabilityList = "f_des_semantic";
% desirabilityShort = "Semant";
% desirabilityStr = "$Semantic~Integrity$";

% Loop over desirability properties
for ii = 1:length(desirabilityStr)

    % Create figure
    figure(ii)
    clf
    hold("on")
    grid("on")

    % Add ylabel
    ylabel(desirabilityStr(ii),"FontSize",16,"Interpreter","latex")
    set(gca,"TickLabelInterpreter","latex")
    set(gca,"FontSize",16)

    % Create boxchart
    aggrGroup = categorical(resultsTable.aggregation_strategy,aggList,["$No~Aggregation$","$Weighted~Sum$"]);
    boxchart(aggrGroup,resultsTable.(desirabilityList(ii)),"GroupByColor",resultsTable.model)
    legend("AutoUpdate","off")

    % Plot black line to split the aggragation methods
    plot([1.5,1.5],[0,1],"k","LineWidth",0.1,"DisplayName","")
    
    % Save boxplot
    saveas(gcf,"Figures" + filesep + sprintf("Boxplot_%s.pdf",desirabilityShort(ii)),"pdf");
    saveas(gcf,"Figures" + filesep + sprintf("Boxplot_%s.eps",desirabilityShort(ii)),"epsc");
end
