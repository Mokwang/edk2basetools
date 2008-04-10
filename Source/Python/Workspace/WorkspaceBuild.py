## @file
# This file is used to create a database used by ECC tool
#
# Copyright (c) 2007 ~ 2008, Intel Corporation
# All rights reserved. This program and the accompanying materials
# are licensed and made available under the terms and conditions of the BSD License
# which accompanies this distribution.  The full text of the license may be found at
# http://opensource.org/licenses/bsd-license.php
#
# THE PROGRAM IS DISTRIBUTED UNDER THE BSD LICENSE ON AN "AS IS" BASIS,
# WITHOUT WARRANTIES OR REPRESENTATIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED.
#

##
# Import Modules
#
##
# Import Modules
#
import os

from CommonDataClass.DataClass import *
from WorkspaceDatabase import *
from Common import EdkLogger as EdkLogger
from Common import DataType
from Common.String import *
from Common.BuildToolError import *
from Common.Misc import sdict
from Common import GlobalData

DATABASE_PATH = "Conf/.cache/build.db"

## ItemBuild
#
# This Class defines Module/Platform/Package databases for build system
#
# @param object:          Inherited from object class
# @param Arch:            Build arch
# @param Platform:        Build Platform
# @param Package:         Build Package
# @param Module:          Build Module
#
# @var Arch:              To store value for Build Arch
# @var PlatformDatabase:  To store value for PlatformDatabase, it is a set structure as
#                         { [DscFileName] : PlatformBuildClassObject, ...}
# @var PackageDatabase:   To store value for PackageDatabase, it is a set structure as
#                         { [DecFileName] : PacakgeBuildClassObject, ...}
# @var ModuleDatabase:    To store value for ModuleDatabase, it is a list structure as
#                         { [InfFileName] : ModuleBuildClassObject, ...}
#
class ItemBuild(object):
    def __init__(self, Arch, Platform = None, Package = None, Module = None):
        self.Arch                    = Arch
        self.PlatformDatabase        = {}
        self.PackageDatabase         = {}
        self.ModuleDatabase          = {}

class WorkspaceBuild(object):
    def __init__(self, ActivePlatform, WorkspaceDir, Reparse=False, SkuId=''):
        self.WorkspaceDir            = NormPath(WorkspaceDir)
        self.SupArchList             = []
        self.BuildTarget             = []
        self.SkuId                   = SkuId
        self.Fdf                     = ''
        self.FdTargetList            = []
        self.FvTargetList            = []
        self.TargetTxt               = None
        self.ToolDef                 = None

        self.InfDatabase             = {}
        self.DecDatabase             = {}
        self.DscDatabase             = {}
        
        self.UnFoundPcdInDsc         = {}

        os.chdir(self.WorkspaceDir)
        #
        # Init build for all arches
        #
        self.Build                   = {}
        for Arch in DataType.ARCH_LIST:
            self.Build[Arch] = ItemBuild(Arch)

        #
        # Init build database
        #
        self.Db = WorkspaceDatabase(DATABASE_PATH, GlobalData.gGlobalDefines, Reparse)
        self.Db.InitDatabase()
        
        #
        # Get active platform
        #
        self.DscFileName = NormPath(ActivePlatform)
        File = os.path.join(self.WorkspaceDir, self.DscFileName)
        if not (os.path.exists(File) and os.path.isfile(File)):
            EdkLogger.error("AutoGen", FILE_NOT_FOUND, ExtraData = File)

        #
        # Parse platform to get module
        #
        Platform = self.Db.BuildObject[self.DscFileName, MODEL_FILE_DSC, 'COMMON']
        self.SupArchList = Platform.SupArchList
        self.BuildTarget = Platform.BuildTargets
        self.Fdf = Platform.FlashDefinition
        if self.SkuId == '':
            self.SkuId = Platform.SkuName
        for Arch in self.SupArchList:
            Platform = self.Db.BuildObject[self.DscFileName, MODEL_FILE_DSC, Arch]
            Platform.SkuName = self.SkuId
            self.Build[Arch].PlatformDatabase[self.DscFileName] = Platform
    
    ## GenBuildDatabase
    #
    # Generate build database for all arches
    #
    # @param PcdsSet: Pcd list for override from Fdf parse result
    # @param InfList: Inf list for override from Fdf parse result
    #
    def GenBuildDatabase(self, PcdsSet = {}, InfList = []):
        for Arch in self.SupArchList:
            Platform = self.Build[Arch].PlatformDatabase[self.DscFileName]

            for Name,Guid in PcdsSet:
                Platform.AddPcd(Name, Guid, PcdsSet[Name, Guid])

            for Inf in InfList:
                Platform.AddModule(Inf)

            #
            # Get all inf files
            #
            for Module in Platform.Modules:
                ModulePath = str(Module)
                if ModulePath in self.Build[Arch].ModuleDatabase:
                    continue 
                self.Build[Arch].ModuleDatabase[ModulePath] = Module

                for Key in Module.LibraryClasses:
                    ModulePath = Module.LibraryClasses[Key]
                    if ModulePath == None or ModulePath == '':
                        continue
                    self.Build[Arch].ModuleDatabase[ModulePath] = self.Db.BuildObject[ModulePath, MODEL_FILE_INF, Arch]

                for Package in Module.Packages:
                    PackagePath = str(Package)
                    if PackagePath in self.Build[Arch].PackageDatabase:
                        continue
                    self.Build[Arch].PackageDatabase[PackagePath] = Package

    def WorkspaceFile(self, Filename):
        return os.path.join(self.WorkspaceDir, Filename)
