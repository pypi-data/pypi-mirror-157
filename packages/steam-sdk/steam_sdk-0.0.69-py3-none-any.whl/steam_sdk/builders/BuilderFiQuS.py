import math
import pandas as pd

from steam_sdk.data import DataModelMagnet as dM
from steam_sdk.data import DataRoxieParser as dR
from steam_sdk.data import DataFiQuS as dF


class BuilderFiQuS:
    """
        Class to generate FiQuS models
    """

    def __init__(self,
                 input_model_data: dM.DataModelMagnet = None,
                 input_roxie_data: dR.RoxieData = None,
                 flag_build: bool = True,
                 verbose: bool = True):
        """
            Object is initialized by defining FiQuS variable structure and file template.
            If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.model_data: dM.DataModelMagnet = input_model_data
        self.roxie_data: dR.RoxieData = input_roxie_data

        # Data structure
        self.data_FiQuS_geo = dF.FiQuSGeometry()
        self.data_FiQuS_set = dF.FiQuSSettings()
        self.data_FiQuS = dF.FiQuSData()

        if not self.model_data and flag_build:
            raise Exception('Cannot build model instantly without providing DataModelMagnet')

        if flag_build:
            # Build data structures
            self.buildData()

    def buildData(self):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """

        self.data_FiQuS_geo.Roxie_Data = dR.RoxieData(**self.roxie_data.dict())

        self.data_FiQuS_set.Model_Data_GS.general_parameters.I_ref =\
            [self.model_data.Options_LEDET.field_map_files.Iref] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        for cond in self.model_data.Conductors:
            if cond.cable.type == 'Rutherford':
                self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] =\
                    dF.ConductorFiQuS(cable=dF.RutherfordFiQuS(type=cond.cable.type))
            conductor = self.data_FiQuS_set.Model_Data_GS.conductors[cond.name]
            conductor.cable.bare_cable_width = cond.cable.bare_cable_width
            conductor.cable.bare_cable_height_mean = cond.cable.bare_cable_height_mean


