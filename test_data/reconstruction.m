function reconstruction(inputFile, outputDirectory, configurationFile)
    %reconstruction front end for accessing all the different algorithms
    %   Arguments
    %   inputFile: Path to a Siemens TWIX file
    %   outputDirectory: Existing directory to place reconstructed images and
    %                    other output (e.g. debugging dumps)
    %   configurationFile(optional): Path to a JSON configuration as generated
    %                                by ReconConfiguration.m:writeConfigurationFile()
    %                                If not provided default parameters will be
    %                                used.
    arguments
       inputFile(1,:) char {mustBeFile}
       outputDirectory(1,:) char {mustBeFolder} % this enforces it exists
       configurationFile(1,:) char {mustBeEmptyOrFile} = '' % optional
    end

    % just add necessary path. we are not cleaning up afterwards
    run(fullfile(fileparts(mfilename('fullpath')), 'setReconstructionPaths'));

    if nargin < 2
        error('wrong number of arguments.');
    end

    %% read and modify configuration file
    % default config is provided via arguments block automatically.
    if ~isempty(configurationFile)
        config = ReconConfiguration.fromConfigurationFile(configurationFile);
    else
        config = ReconConfiguration();
    end
    % TODO: Add option to pass modifications to configuration as varargin or
    %       (Repeating) arguments block

    %% inputFile and outputDirectory
    % validation is done via arguments block
    [~, inputBaseName, ~] = fileparts(inputFile);
    config.rawDataPath = inputFile;
    config.fileBaseName = inputBaseName;
    config.outRoot = outputDirectory;

    %% read raw data inputFile
    mriData = MriDataMapVBVDImpl(config.rawDataPath, ...
                                 config, ...
                                 config.f0Correct ...
	);

    % TODO: apply navigators if applicable
    %       -> we need mutable MriData to move this step here
    % TODO: apply noise pre-whitening
    %       -> we need mutable MriData to move this step here

    %% choose and execute algorithm
    switch lower(config.method)
        case 'sense'
            % TODO: parpool handling

            % at this point everything is set. Make sure to preserve the current
            % configuration
            config.writeConfigurationFile(fullfile(config.outRoot, [config.fileBaseName '_config.json']))

            % execute the recon
            senseRecon(mriData, config);

        case 'loraks'
            % make sure to preserve the input configuration for replication
            config.writeConfigurationFile(fullfile(config.outRoot, [config.fileBaseName '_config.json']))

            % if requested, change LORAKS parameters based on heuristics of the data
            % these parameters will be written out to the json sidecar files
            if config.loraksConfig.automaticParameters
                config.loraksConfig = lookupOptimalLoraksUnfoldingParameters(mriData, config.loraksConfig);
            end

            % execute the recon
            loraksRecon(mriData, config);

        case 'fouriertransform'
            % at this point everything is set. Make sure to preserve the current
            % configuration
            config.writeConfigurationFile(fullfile(config.outRoot, [config.fileBaseName '_config.json']))

            % execute the recon
            fourierTransformRecon(mriData, config);

        otherwise
            error('unknown method \"%s\"', config.method);
    end
end

function mustBeEmptyOrFile(a)
    % mustBeEmptyOrFile argument validation for optional files
    if ~(isempty(a) || isfile(a))
        eidType = 'mustBeEmptyOrFile:notAValidFile';
        msgType = sprintf('The following files do not exist: ''%s''.', a);
        throwAsCaller(MException(eidType,msgType))
    end
end
