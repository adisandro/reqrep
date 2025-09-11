% This script plot the 6 scatter plots for the different configurations of
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

%% Loop over the plot configurations

% Get list of aggregation strategies and desirability metrics.
aggregationList = unique(string(resultsTable.aggregation_strategy));
desirabilityList = ["f_des_semantic"; "f_des_syntactic"; "f_des_satisfaction"];

% Define string list for aggregation and desirability
aggregationStr = ["$No~Aggregation$"; "$Weighted~Sum$"];
desirabilityStr = ["$Semantic~Integrity$"; "$Syntactic~Similarity$"; "$Satisfaction~extent$"];
weightStr = ["0, 1, 1"; "1, 0, 1"; "1, 1, 0"; "1, 1, 1"];

% Define list of markers and colors
markerList = ["o"; "+"; "x"; "*"; "^"; "square"]; % One marker for each model
colorList = ["b"; "r"; "m"; "c"]; % One color for each weight

% Loop over aggregation strategies
for ii = 1:length(aggregationList)

    % Filter results only related to the chosen aggregation strategy
    resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,aggregationList(ii)),:);

    % Get list of models and weights for the filtered table
    modelList = unique(string(resultsTableTemp.model));
    weightList = unique(resultsTableTemp.weights);
    weightStrTemp = weightStr(end-length(weightList)+1:end);

    % Loop over the desirability metrics
    for jj = 1:length(desirabilityList)

        % Create figure
        figure((ii-1)*length(desirabilityList)+jj)
        hold("on")
        grid("on")
        xlim([0,0.7])
        ylim([0,0.6])
        xlabel("Correctness","FontSize",16,"Interpreter","latex")
        ylabel(desirabilityStr(jj),"FontSize",16,"Interpreter","latex")
        title(aggregationStr(ii),"FontSize",16,"Interpreter","latex")

        % Loop over model
        for kk = 1:length(weightList)
            
            % Loop over weight
            for mm = 1:length(modelList)

                % Get all repairs corresponding to this case
                resultsTemp = resultsTableTemp(strcmp(resultsTableTemp.model, modelList(mm)) & ...
                    strcmp(resultsTableTemp.weights, weightList(kk)), :);

                % Get average correctness and desirability metrics
                correctTemp = mean(resultsTemp.f_correctness);
                desireTemp = mean(resultsTemp.(desirabilityList(jj)));

                % Add point on the plot
                scatter(correctTemp,desireTemp,100,markerList(mm),colorList(kk), ...
                    "LineWidth",2,"DisplayName",sprintf("%s - %s",modelList(mm),weightStrTemp(kk)))
            end
        end

        % Activate legend
        legend("Location","eastoutside","FontSize",12,"Box","off")
        saveas(gcf,"Figures" + filesep + sprintf("Scatter_%i.pdf",(ii-1)*length(desirabilityList)+jj),"pdf");
        saveas(gcf,"Figures" + filesep + sprintf("Scatter_%i.eps",(ii-1)*length(desirabilityList)+jj),"epsc");
    end

    % Delete temporary variables
    clear("*Temp")
    
end




