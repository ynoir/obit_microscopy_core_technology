"""
Created on Feb 20, 2014

@author: Aaron Ponti
"""

import java.io.File
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from BioFormatsProcessor import BioFormatsProcessor
from MicroscopySingleDatasetConfig import MicroscopySingleDatasetConfig
from MicroscopyCompositeDatasetConfig import MicroscopyCompositeDatasetConfig

class Processor:
    """The Processor class performs all steps required for registering datasets
    from the assigned dropbox folder."""

    # A transaction object passed by openBIS
    _transaction = None

    # The incoming folder to process (a java.io.File object)
    _incoming = ""

    # The logger
    _logger = None

    # Constructor
    def __init__(self, transaction, logger):

        # Store arguments
        self._transaction = transaction
        self._incoming = transaction.getIncoming()

        # Set up logger
        self._logger = logger


    def dictToXML(self, d):
        """Converts a dictionary into an XML string."""

        # Create an XML node
        node = ET.Element("MicroscopyFileSeries")

        # Add all attributes to the XML node
        for k, v in d.iteritems():
            key = k.encode('utf-8')
            value = v.encode('utf-8')
            node.set(key, value)

        # Convert to XML string
        xml = ET.tostring(node)

        # Return the XML string
        return xml

    def getCustomTimeStamp(self):
        """Create an univocal time stamp based on the current date and time
        (works around incomplete API of Jython 2.5)."""

        t = datetime.now()
        return t.strftime("%y%d%m%H%M%S") + unicode(t)[20:]

    def getSubFolders(self):
        """Return a list of subfolders of the passed incoming directory.

        @return list of subfolders (String)
        """

        incomingStr = self._incoming.getAbsolutePath()
        return [name for name in os.listdir(incomingStr)
                if os.path.isdir(os.path.join(incomingStr, name))]

    def getOrCreateExperiment(self, expId, expName,
                         expType="MICROSCOPY_EXPERIMENT"):
        """Get the experiment with given ID if it exists, or creates it.

        @param expID, the experiment ID
        @param expName, the experiment name
        @param expType, the experiment type that must already exist; optional,
        default is "MICROSCOPY_EXPERIMENT"
        """

        # Make sure to keep the code length within the limits imposed by
        # openBIS for codes
        if len(expId) > 60:
            expId = expId[0:60]

        # Try getting the experiment
        exp = self._transaction.getExperimentForUpdate(expId)
        if not exp:
            # Log
            msg = "PROCESSOR::getOrCreateExperiment(): " + \
            "The experiment with ID " + expId + " does not exist. Create."
            self._logger.info(msg)

            # Create the experiment
            exp = self._transaction.createNewExperiment(expId, expType)
            if not exp:
                msg = "PROCESSOR::getOrCreateExperiment(): " + \
                "Could not create experiment " + expId + "!"
                self._logger.error(msg)
                raise Exception(msg)
            else:
                self._logger.info("PROCESSOR::getOrCreateExperiment(): " + 
                                  "Created experiment with ID " + expId + ".")
        else:
            # Log
            msg = "PROCESSOR::getOrCreateExperiment(): " + \
            "Registering to already existing experiment with ID " + expId + "."
            self._logger.info(msg)

        # Store the name
        exp.setPropertyValue("MICROSCOPY_EXPERIMENT_NAME", expName)

        return exp

    def createExperiment(self, expId, expName, expType="MICROSCOPY_EXPERIMENT"):
        """Create an experiment with given Experiment ID extended with the addition
        of a string composed from current date and time.

        @param expID, the experiment ID
        @param expName, the experiment name
        @param expType, the experiment type that must already exist; optional,
        default is "MICROSCOPY_EXPERIMENT"
        """

        # Make sure to keep the code length within the limits imposed by
        # openBIS for codes
        if len(expId) > 41:
            expId = expId[0:41]

        # Create univocal ID
        expId = expId + "_" + self.getCustomTimeStamp()

        # Log
        self._logger.info("PROCESSOR::createExperiment(): " + 
                          "Register experiment %s" % expId)

        # Create the experiment
        exp = self._transaction.createNewExperiment(expId, expType)
        if not exp:
            msg = "PROCESSOR::createExperiment(): " + \
            "Could not create experiment " + expId + "!"
            self._logger.error(msg)
            raise Exception(msg)
        else:
            self._logger.info("PROCESSOR::createExperiment(): " + 
                              "Created experiment with ID " + expId + ".")

        # Store the name
        exp.setPropertyValue("MICROSCOPY_EXPERIMENT_NAME", expName)

        return exp

    def processExperiment(self, experimentNode,
                          openBISExpType="MICROSCOPY_EXPERIMENT"):
        """Register an IExperimentUpdatable based on the Experiment XML node.

        @param experimentNode An XML node corresponding to an Experiment
        @param openBISExpType The experiment type
        @return IExperimentUpdatable experiment
        """

        # Get the openBIS identifier
        openBISIdentifier = experimentNode.attrib.get("openBISIdentifier")

        # Get the experiment name
        expName = experimentNode.attrib.get("name")

        # Get the experiment date and reformat it to be compatible
        # with postgreSQL
        # TODO: Add this
        # expDate = self.formatExpDateForPostgreSQL(experimentNode.attrib.get("date"))

        # Get the description
        description = experimentNode.attrib.get("description")

        # Get the acquisition hardware
        # TODO: Add this
        # acqHardware = experimentNode.attrib.get("acq_hardware")

        # Get the acquisition software
        # TODO: Add this
        # acqSoftware = experimentNode.attrib.get("acq_software")

        # Get the owner name
        # TODO: Add this
        # owner = experimentNode.attrib.get("owner_name")

        # Get or create the experiment
        openBISExperiment = self.getOrCreateExperiment(openBISIdentifier,
                                                  expName, openBISExpType)
        if not openBISExperiment:
            msg = "PROCESSOR::processExperiment(): " + \
            "Could not create experiment " + openBISIdentifier
            self._logger.error(msg)
            raise Exception(msg)

        # Set the date
        # TODO: Add this
        # openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_DATE",
        #                                   expDate)

        # Set the description -- but only if is not empty. 
        # This makes sure that the description of an already existing experiment
        # is not overridden by an empty string.
        if description != "":
            openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_DESCRIPTION",
                                               description)
        else:
            currentDescription = openBISExperiment.getPropertyValue("MICROSCOPY_EXPERIMENT_DESCRIPTION")
            if (currentDescription is None or currentDescription == ""):
                openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_DESCRIPTION", "")

        # Get the series metadata from the XML file otherwise parse the file
        
        
        # TODO: Add this
        # openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_ACQ_HARDWARE",
        #                                   acqHardware)

        # Set the acquisition software
        # TODO: Add this
        # openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_ACQ_SOFTWARE",
        #                                   acqSoftware)

        # Set the experiment owner
        # TODO: Add this
        # openBISExperiment.setPropertyValue("MICROSCOPY_EXPERIMENT_OWNER",
        #                                   owner)

        # Return the openBIS Experiment object
        return openBISExperiment

    def processMicroscopyFile(self, microscopyFileNode, openBISExperiment):
        """Register the Microscopy File using the parsed properties file.

        @param microscopyFileNode An XML node corresponding to a microscopy
        file (dataset)
        @param openBISExperiment An ISample object representing an Experiment
        """

        # Assign the file to the dataset (we will use the absolute path)
        relativeFileName = microscopyFileNode.attrib.get("relativeFileName")
        fileName = os.path.join(self._incoming.getAbsolutePath(), relativeFileName)

        # Check if the series metadata has been extracted already (i.e. if
        # the microscopyFileNode has at least one child), otherwise
        # process it
        if len(microscopyFileNode) == 0:
            
            # Instantiate a BioFormatsProcessor
            bioFormatsProcessor = BioFormatsProcessor(fileName, self._logger)

            # Extract series metadata
            bioFormatsProcessor.parse()

            # Get the metadata for the series
            allSeriesMetadata = bioFormatsProcessor.getMetadata()

            # Get the number of series
            num_series = bioFormatsProcessor.getNumSeries()

            # Close the file
            bioFormatsProcessor.close()

        else:

            # Get the metadata for all series from the (processed) settings XML 
            allSeriesMetadata = []
            for series in microscopyFileNode:
                allSeriesMetadata.append(series.attrib)

            # Get the number of series
            num_series = len(microscopyFileNode)

        self._logger.info("PROCESSOR::processMicroscopyFile(): " + 
                          "File " + relativeFileName + " contains " + 
                           str(num_series) + " series.")

        # Get the correct space where to create the sample
        identifier = openBISExperiment.getExperimentIdentifier()
        sample_space = identifier[1:identifier.find('/', 1)]
        self._logger.info("Creating sample with auto-generated code in space " + sample_space)

        # Create a sample for the dataset
        sample = self._transaction.createNewSampleWithGeneratedCode(sample_space,
                                                                    "MICROSCOPY_SAMPLE_TYPE")

        # Set the sample name
        sample.setPropertyValue("MICROSCOPY_SAMPLE_NAME",
                                relativeFileName[relativeFileName.rfind('/') + 1:])
        
        # Set the sample description
        sampleDescr = microscopyFileNode.attrib.get("description")
        if sampleDescr is None:
            sampleDescr = ""
        sample.setPropertyValue("MICROSCOPY_SAMPLE_DESCRIPTION", sampleDescr)

        # Set the experiment
        sample.setExperiment(openBISExperiment)

        # Register all series in the file
        image_data_set = None
        for i in range(num_series):

            # Create a configuration object
            singleDatasetConfig = MicroscopySingleDatasetConfig(allSeriesMetadata,
                                                                self._logger, i)

            # Extract the metadata associated to this series and convert it to
            # XML to store it in the MICROSCOPY_IMG_CONTAINER_METADATA property
            # of the MICROSCOPY_IMG_CONTAINER_METADATA (series) dataset type
            seriesMetadataXML = self.dictToXML(allSeriesMetadata[i])
            
            # Log the content of the metadata
            self._logger.info("Series metadata (XML): " + str(seriesMetadataXML))

            if image_data_set is None:
                
                # Register the file for the first time (for series 0)
                
                # Log
                self._logger.info("PROCESSOR::processMicroscopyFile(): " + 
                                  "Creating new image dataset for file " + 
                                   str(fileName))

                # Create an image dataset
                image_data_set = self._transaction.createNewImageDataSet(singleDatasetConfig,
                                                                         java.io.File(fileName))

                # Store the metadata in the MICROSCOPY_IMG_CONTAINER_METADATA property
                image_data_set.setPropertyValue("MICROSCOPY_IMG_CONTAINER_METADATA", seriesMetadataXML)
                
                # Store the series name in the MICROSCOPY_IMG_CONTAINER_NAME property
                image_data_set.setPropertyValue("MICROSCOPY_IMG_CONTAINER_NAME", allSeriesMetadata[i]["name"])

                # Move the file
                self._transaction.moveFile(fileName, image_data_set)

            else:

                # Register subsequent series to point to the same file

                # Log
                self._logger.info("PROCESSOR::processMicroscopyFile(): " + 
                                  "Creating new image dataset for dataset " + 
                                  str(image_data_set))
                
                # Create an image dataset that points to an exising one
                # (and points to its file)
                dataset = self._transaction.createNewImageDataSetFromDataSet(singleDatasetConfig,
                                                                             image_data_set)

                # Store the metadata in the MICROSCOPY_IMG_CONTAINER_METADATA property
                dataset.setPropertyValue("MICROSCOPY_IMG_CONTAINER_METADATA",
                                         seriesMetadataXML)

                # Store the series name in the MICROSCOPY_IMG_CONTAINER_NAME property
                dataset.setPropertyValue("MICROSCOPY_IMG_CONTAINER_NAME", allSeriesMetadata[i]["name"])

            # Set the (common) sample for the series
            dataset.setSample(sample)


    def processMicroscopyCompositeFile(self, microscopyCompositeFileNode,
                                       openBISExperiment):
        """Register the Microscopy Composite File using the parsed properties file.

        @param microscopyCompositeFileNode An XML node corresponding to a microscopy
        file (dataset)
        @param openBISExperiment An ISample object representing an Experiment
        """

        # Make sure to have a supported composite file type
        compositeFileType = microscopyCompositeFileNode.attrib.get("compositeFileType")

        if compositeFileType != "Leica TIFF Series":

            msg = "PROCESSOR::processMicroscopyCompositeFile(): " + \
                      "Invalid composite file type found: " + compositeFileType
            self._logger.error(msg)
            raise Exception(msg)

        else:

            self._logger.info("PROCESSOR::processMicroscopyCompositeFile(): " + \
                              "Processing " + compositeFileType)

        # Get the correct space where to create the sample
        identifier = openBISExperiment.getExperimentIdentifier()
        sample_space = identifier[1:identifier.find('/', 1)]
        self._logger.info("Creating sample with auto-generated code in space " + sample_space)

        # Create a sample for the dataset
        sample = self._transaction.createNewSampleWithGeneratedCode(sample_space,
                                                                    "MICROSCOPY_SAMPLE_TYPE")

        # Set the sample name
        name = microscopyCompositeFileNode.attrib.get("name")
        sample.setPropertyValue("MICROSCOPY_SAMPLE_NAME", name)

        # Set the sample description
        sampleDescr = microscopyCompositeFileNode.attrib.get("description")
        if sampleDescr is None:
            sampleDescr = ""
        sample.setPropertyValue("MICROSCOPY_SAMPLE_DESCRIPTION", sampleDescr)

        # Get the series indices
        seriesIndices = microscopyCompositeFileNode.attrib.get("seriesIndices")
        seriesIndices = seriesIndices.split(",")

        # Set the experiment
        sample.setExperiment(openBISExperiment)

        # Get the relative path to the containing folder
        relativeFolder = microscopyCompositeFileNode.attrib.get("relativeFolder")
        fullFolder = os.path.join(self._incoming.getAbsolutePath(), relativeFolder)

        # Register all series in the file
        image_data_set = None
        for i in seriesIndices:

            self._logger.info("Processing series " + str(i))

            # Create a configuration object
            compositeDatasetConfig = MicroscopyCompositeDatasetConfig([],
                                                                      self._logger,
                                                                      i)

            # Create a dataset
            image_data_set = self._transaction.createNewImageDataSet(compositeDatasetConfig,
                                                                     java.io.File(fullFolder))

            # Store the metadata in the MICROSCOPY_IMG_CONTAINER_METADATA property
            # TODO: Get the store the metadata information
            image_data_set.setPropertyValue("MICROSCOPY_IMG_CONTAINER_METADATA", "")

            # Store the series name in the MICROSCOPY_IMG_CONTAINER_NAME property
            # TODO Get and store the correct series name
            image_data_set.setPropertyValue("MICROSCOPY_IMG_CONTAINER_NAME", "Series_" + str(i))

        # Move the file
        self._transaction.moveFile(fullFolder, image_data_set)

        # Set the (common) sample for the series
        image_data_set.setSample(sample)


    def register(self, tree):
        """Register the Experiment using the parsed properties file.

        @param tree ElementTree parsed from the properties XML file
        """

        # Get the root node (obitXML)
        root = tree.getroot()

        # Iterate over the children (Experiments)
        for experimentNode in root:

            # The tag of the immediate children of the root experimentNode
            # must be Experiment
            if experimentNode.tag != "Experiment":
                msg = "PROCESSOR::register(): " + \
                      "Expected Experiment node, found " + experimentNode.tag
                self._logger.error(msg)
                raise Exception(msg)

            # Process an Experiment XML node and get/create an IExperimentUpdatable
            openBISExperiment = self.processExperiment(experimentNode,
                                                       "MICROSCOPY_EXPERIMENT")

            # Process children of the Experiment
            for fileNode in experimentNode:

                if fileNode.tag == "MicroscopyFile":

                    # Process the MicroscopyFile node
                    self.processMicroscopyFile(fileNode, openBISExperiment)

                elif fileNode.tag == "MicroscopyCompositeFile":

                    # Process the MicroscopyCompositeFile node
                    self.processMicroscopyCompositeFile(fileNode, openBISExperiment)

                    # Inform
                    self._logger.info("Processed composite file")

                else:

                    msg = "PROCESSOR::register(): " + \
                    "Expected either MicroscopyFile or MicroscopyCompositeFile " + \
                    "node; found instead " + fileNode.tag + ")!"
                    self._logger.error(msg)
                    raise Exception(msg)

        # Log that we are finished with the registration
        self._logger.info("PROCESSOR::register(): " + 
                          "Registration completed")


    def run(self):
        """Run the registration."""

        # Make sure that incoming is a folder
        if not self._incoming.isDirectory():
            msg = "PROCESSOR::run(): " + \
            "Incoming MUST be a folder!"
            self._logger.error(msg)
            raise Exception(msg)

        # Log
        self._logger.info("PROCESSOR::run(): " + 
                          "Incoming folder: " + 
                          self._incoming.getAbsolutePath())

        # There must be just one subfolder: the user subfolder
        subFolders = self.getSubFolders()
        if len(subFolders) != 1:
            msg = "PROCESSOR::run(): " + \
            "Expected user subfolder!"
            self._logger.error(msg)
            raise Exception(msg)

        # Set the user folder
        userFolder = os.path.join(self._incoming.getAbsolutePath(),
                                  subFolders[0])

        # In the user subfolder we must find the data_structure.ois file
        dataFileName = os.path.join(userFolder, "data_structure.ois")
        if not os.path.exists(dataFileName):
            msg = "PROCESSOR::run(): " + \
            "File data_structure.ois not found!"
            self._logger.error(msg)
            raise Exception(msg)

        # Now read the data structure file and store all the pointers to
        # the properties files. The paths are stored relative to self._incoming,
        # so we can easily build the full file paths.
        propertiesFileList = []
        f = open(dataFileName)
        try:
            for line in f:
                line = re.sub('[\r\n]', '', line)
                propertiesFile = os.path.join(self._incoming.getAbsolutePath(),
                                              line)
                propertiesFileList.append(propertiesFile)
                self._logger.info("PROCESSOR::run(): " + 
                                  "Found: " + str(propertiesFile))
        finally:
            f.close()

        # Process (and ultimately register) all experiments
        for propertiesFile in propertiesFileList:
            # Log
            self._logger.info("PROCESSOR::run(): " + 
                              "Processing: " + propertiesFile)

            # Read the properties file into an ElementTree
            tree = ET.parse(propertiesFile)

            # Now register the experiment
            self.register(tree)
