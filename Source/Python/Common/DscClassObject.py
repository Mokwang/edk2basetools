# Copyright (c) 2007, Intel Corporation
# All rights reserved. This program and the accompanying materials
# are licensed and made available under the terms and conditions of the BSD License
# which accompanies this distribution.    The full text of the license may be found at
# http://opensource.org/licenses/bsd-license.php
#
# THE PROGRAM IS DISTRIBUTED UNDER THE BSD LICENSE ON AN "AS IS" BASIS,
# WITHOUT WARRANTIES OR REPRESENTATIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED.

#
#This file is used to define each component of DSC file
#

import os
from String import *
from DataType import *
from Identification import *
from Dictionary import *
from CommonDataClass.PlatformClass import *
from CommonDataClass.CommonClass import SkuInfoClass
from BuildToolError import *

class DscObject(object):
    def __init__(self):
        object.__init__()

class DscDefines(DscObject):
    def __init__(self):
        self.DefinesDictionary = {
            #Req
            TAB_DSC_DEFINES_PLATFORM_NAME                         : [''],
            TAB_DSC_DEFINES_PLATFORM_GUID                         : [''],
            TAB_DSC_DEFINES_PLATFORM_VERSION                      : [''],
            TAB_DSC_DEFINES_DSC_SPECIFICATION                     : [''],
            TAB_DSC_DEFINES_OUTPUT_DIRECTORY                      : [''],
            TAB_DSC_DEFINES_SUPPORTED_ARCHITECTURES               : [''],
            TAB_DSC_DEFINES_BUILD_TARGETS                         : [''],
            TAB_DSC_DEFINES_SKUID_IDENTIFIER                      : [''],
            TAB_DSC_DEFINES_FLASH_DEFINITION                      : [''],
            TAB_DSC_DEFINES_BUILD_NUMBER                          : [''],
            TAB_DSC_DEFINES_MAKEFILE_NAME                         : ['']                        
        }

class DscSkuId(DscObject):
    def __init__(self):
        self.SkuId = {}         #{ [skuid : skuname], [skuid : skuname], ...}

class DscContents(DscObject):
    def __init__(self):
        self.SkuIds = []
        self.Libraries = []
        self.Components = []                #[['component name', [lib1, lib2, lib3], [bo1, bo2, bo3]], ...]
        self.LibraryClasses = []
        self.PcdsFixedAtBuild = []
        self.PcdsPatchableInModule = []
        self.PcdsFeatureFlag = []
        self.PcdsDynamicDefault = []
        self.PcdsDynamicVpd = []
        self.PcdsDynamicHii = []       
        self.PcdsDynamicExDefault = []
        self.PcdsDynamicExVpd = []
        self.PcdsDynamicExHii = []                
        self.BuildOptions = []

class Dsc(DscObject):
    def __init__(self, Filename = None, IsMergeAllArches = False, IsToPlatform = False, WorkspaceDir = None):
        self.Identification = Identification()
        self.Defines = DscDefines()
        self.Contents = {}
        self.UserExtensions = ''
        self.Platform = PlatformClass()
        self.WorkspaceDir = WorkspaceDir

        for Arch in DataType.ARCH_LIST_FULL:
            self.Contents[Arch] = DscContents()
        
        self.KeyList = [
            TAB_SKUIDS, TAB_LIBRARIES, TAB_LIBRARY_CLASSES, TAB_BUILD_OPTIONS, TAB_PCDS_FIXED_AT_BUILD_NULL, \
            TAB_PCDS_PATCHABLE_IN_MODULE_NULL, TAB_PCDS_FEATURE_FLAG_NULL, \
            TAB_PCDS_DYNAMIC_DEFAULT_NULL, TAB_PCDS_DYNAMIC_HII_NULL, TAB_PCDS_DYNAMIC_VPD_NULL, \
            TAB_PCDS_DYNAMIC_EX_DEFAULT_NULL, TAB_PCDS_DYNAMIC_EX_HII_NULL, TAB_PCDS_DYNAMIC_EX_VPD_NULL, \
            TAB_COMPONENTS
        ]
        
        if Filename != None:
            self.LoadDscFile(Filename)
            
        if IsMergeAllArches:
            self.MergeAllArches()
        
        if IsToPlatform:
            self.DscToPlatform()
        
    def ParseDsc(self, Lines, Key, KeyField):
        newKey = SplitModuleType(Key)
        if newKey[0].upper().find(TAB_LIBRARY_CLASSES.upper()) != -1:
            GetLibraryClassesWithModuleType(Lines, Key, KeyField, TAB_COMMENT_SPLIT)
        elif newKey[0].upper().find(TAB_COMPONENTS.upper()) != -1:
            GetComponents(Lines, Key, KeyField, TAB_COMMENT_SPLIT)
        elif newKey[0].upper().find(TAB_PCDS_DYNAMIC.upper()) != -1:
            GetDynamics(Lines, Key, KeyField, TAB_COMMENT_SPLIT)
        else:
            GetMultipleValuesOfKeyFromLines(Lines, Key, KeyField, TAB_COMMENT_SPLIT)
    
    def MergeAllArches(self):
        for key in self.KeyList:
            for arch in DataType.ARCH_LIST:
                Command = "self.Contents[arch]." + key + ".extend(" + "self.Contents['" + DataType.TAB_ARCH_COMMON + "']." + key + ")"
                eval(Command)
            
    def LoadDscFile(self, Filename):
        (Filepath, Name) = os.path.split(Filename)
        self.Identification.FileName = Name
        self.Identification.FileFullPath = Filename
        self.Identification.FileRelativePath = Filepath
        
        F = open(Filename, 'r').read()
        PreCheck(Filename, F, self.KeyList)
        Sects = F.split(DataType.TAB_SECTION_START)
        for Sect in Sects:
            TabList = GetSplitValueList(Sect.split(TAB_SECTION_END, 1)[0], DataType.TAB_COMMA_SPLIT)
            for Tab in TabList:
                if Tab.upper() == TAB_INF_DEFINES.upper():
                    GetSingleValueOfKeyFromLines(Sect, self.Defines.DefinesDictionary, TAB_COMMENT_SPLIT, TAB_EQUAL_SPLIT, True, TAB_VALUE_SPLIT)
                    continue
                for Arch in DataType.ARCH_LIST_FULL + [DataType.TAB_ARCH_NULL]:
                    for Key in self.KeyList:
                        if Arch != DataType.TAB_ARCH_NULL:
                            Target = (Key + DataType.TAB_SPLIT + Arch).upper()
                        else:
                            Target = Key.upper()
                        if SplitModuleType(Tab)[0].upper() == Target:
                            if Arch != DataType.TAB_ARCH_NULL:
                                Command = 'self.ParseDsc(Sect, Tab, self.Contents[Arch].' + Key + ')'
                                eval(Command)
                                continue
                            else:
                                Command = "self.ParseDsc(Sect, Tab, self.Contents['" + DataType.TAB_ARCH_COMMON + "']." + Key + ')'
                                eval(Command)
                                continue

    def DscToPlatform(self):
        #
        # Get value for Header
        #
        self.Platform.Header.Name = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_PLATFORM_NAME][0]
        self.Platform.Header.Guid = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_PLATFORM_GUID][0]
        self.Platform.Header.Version = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_PLATFORM_VERSION][0]
        self.Platform.Header.FileName = self.Identification.FileName
        self.Platform.Header.FullPath = self.Identification.FileFullPath
        self.Platform.Header.DscSpecification = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_DSC_SPECIFICATION][0]
        
        self.Platform.Header.SkuIdName = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_SKUID_IDENTIFIER]
        self.Platform.Header.SupArchList = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_SUPPORTED_ARCHITECTURES]
        self.Platform.Header.BuildTargets = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_BUILD_TARGETS]
        self.Platform.Header.OutputDirectory = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_OUTPUT_DIRECTORY][0]
        self.Platform.Header.BuildNumber = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_BUILD_NUMBER][0]
        self.Platform.Header.MakefileName = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_MAKEFILE_NAME][0]
        
        Fdf = PlatformFlashDefinitionFileClass()
        Fdf.FilePath = self.Defines.DefinesDictionary[TAB_DSC_DEFINES_FLASH_DEFINITION][0]
        self.Platform.FlashDefinitionFile = Fdf
        
        #BuildOptions
        BuildOptions = {}
        IncludeFiles = {}
        for Arch in DataType.ARCH_LIST:
            for Item in self.Contents[Arch].BuildOptions:
                if GenInclude(Item, IncludeFiles, Arch):
                    IncludeFile = CleanString(Item[Item.upper().find(DataType.TAB_INCLUDE.upper() + ' ') + len(DataType.TAB_INCLUDE + ' ') : ])
                    CheckFileExist(self.WorkspaceDir, IncludeFile, self.Platform.Header.FullPath, 'BuildOptions', Item)
                    for NewItem in open(WorkspaceFile(self.WorkspaceDir, IncludeFile), 'r').readlines():
                        MergeArches(BuildOptions, GetBuildOption(NewItem), Arch)
                    continue
                MergeArches(BuildOptions, GetBuildOption(Item), Arch)
        
        self.Platform.BuildOptions.IncludeFiles = IncludeFiles
        for Key in BuildOptions.keys():
            BuildOption = BuildOptionClass(Key[0], Key[1], Key[2])
            BuildOption.SupArchList = BuildOptions[Key]
            self.Platform.BuildOptions.BuildOptionList.append(BuildOption)
        
        #SkuIds
        IncludeFiles = {}
        self.Platform.SkuInfos.SkuInfoList['DEFAULT'] = '0'
        for Arch in DataType.ARCH_LIST:
            for Item in self.Contents[Arch].SkuIds:
                if GenInclude(Item, IncludeFiles, Arch):
                    IncludeFile = CleanString(Item[Item.upper().find(DataType.TAB_INCLUDE.upper() + ' ') + len(DataType.TAB_INCLUDE + ' ') : ])
                    CheckFileExist(self.WorkspaceDir, IncludeFile, self.Platform.Header.FullPath, 'SkuIds', Item)
                    for NewItem in open(WorkspaceFile(self.WorkspaceDir, IncludeFile), 'r').readlines():
                        List = GetSplitValueList(NewItem)
                        if len(List) != 2:
                            ErrorMsg = "Wrong statement '%s' found in section SkuIds in file '%s', correct format is '<Integer>|<UiName>'" % (Item, self.Platform.Header.FullPath)
                            raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                        else:
                            self.Platform.SkuInfos.SkuInfoList[List[1]] = List[0]
                    continue
                List = GetSplitValueList(Item)
                if len(List) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section SkuIds in file '%s', correct format is '<Integer>|<UiName>'" % (Item, self.Platform.Header.FullPath)
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    self.Platform.SkuInfos.SkuInfoList[List[1]] = List[0]
        self.Platform.SkuInfos.IncludeFiles = IncludeFiles
        
        #Libraries
        Libraries = {}
        IncludeFiles = {}
        Defines = {}
        for Arch in DataType.ARCH_LIST:
            for Item in self.Contents[Arch].Libraries:
                if GenInclude(Item, IncludeFiles, Arch):
                    IncludeFile = CleanString(Item[Item.upper().find(DataType.TAB_INCLUDE.upper() + ' ') + len(DataType.TAB_INCLUDE + ' ') : ])
                    CheckFileExist(self.WorkspaceDir, IncludeFile, self.Platform.Header.FullPath, 'Libraries', Item)
                    for NewItem in open(WorkspaceFile(self.WorkspaceDir, IncludeFile), 'r').readlines():
                        MergeArches(Libraries, Item, Arch)
                    continue
                Status = GenDefines(Item, Arch, Defines)
                if Status == 0:       # Find DEFINE statement
                    pass
                elif Status == -1:    # Find DEFINE statement but in wrong format
                    ErrorMsg = "Wrong DEFINE statement '%s' found in section Libraries in file '%s', correct format is 'DEFINE <VarName> = <PATH>'" % (Item, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                elif Status == 1:     # Not find DEFINE statement
                    MergeArches(Libraries, Item, Arch)
        self.Platform.Libraries.IncludeFiles = IncludeFiles
        for Key in Libraries.keys():
            Library = PlatformLibraryClass()
            Library.FilePath = Key
            Library.Define = Defines
            Library.SupArchList = Libraries[Key]
            self.Platform.Libraries.LibraryList.append(Library)
        
        #LibraryClasses
        LibraryClasses = {}
        IncludeFiles = {}
        Defines = {}
        for Arch in DataType.ARCH_LIST:
            for Item in self.Contents[Arch].LibraryClasses:
                if GenInclude(Item[0], IncludeFiles, Arch):
                    IncludeFile = CleanString(Item[0][Item[0].upper().find(DataType.TAB_INCLUDE.upper() + ' ') + len(DataType.TAB_INCLUDE + ' ') : ])
                    IncludeFilePath = WorkspaceFile(self.WorkspaceDir, IncludeFile)
                    CheckFileExist(self.WorkspaceDir, IncludeFile, self.Platform.Header.FullPath, 'LibraryClasses', Item[0])
                    for NewItem in open(IncludeFilePath, 'r').readlines():
                        MergeArches(LibraryClasses, self.GenLibraryClass([NewItem, Item[1]], IncludeFilePath), Arch)
                    continue
                Status = GenDefines(Item[0], Arch, Defines)
                if Status == 0:       # Find DEFINE statement
                    pass
                elif Status == -1:    # Find DEFINE statement but in wrong format
                    ErrorMsg = "Wrong DEFINE statement '%s' found in section LibraryClasses in file '%s', correct format is 'DEFINE <VarName> = <PATH>'" % (Item, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                elif Status == 1:     # Not find DEFINE statement
                    MergeArches(LibraryClasses, self.GenLibraryClass(Item, self.Platform.Header.FullPath), Arch)
        self.Platform.LibraryClasses.IncludeFiles = IncludeFiles
        for Key in LibraryClasses.keys():
            Library = PlatformLibraryClass()
            Library.Name = Key[0]
            Library.FilePath = Key[1]
            Library.SupModuleList = list(Key[2:])
            Library.Define = Defines
            Library.SupArchList = LibraryClasses[Key]
            self.Platform.LibraryClasses.LibraryList.append(Library)
        
        #Pcds
        self.GenPcds(DataType.TAB_PCDS_FIXED_AT_BUILD)
        self.GenPcds(DataType.TAB_PCDS_PATCHABLE_IN_MODULE)
        self.GenFeatureFlagPcds(DataType.TAB_PCDS_FEATURE_FLAG)
        self.GenDynamicDefaultPcds(DataType.TAB_PCDS_DYNAMIC_DEFAULT)
        self.GenDynamicDefaultPcds(DataType.TAB_PCDS_DYNAMIC_EX_DEFAULT)
        self.GenDynamicHiiPcds(DataType.TAB_PCDS_DYNAMIC_HII)
        self.GenDynamicHiiPcds(DataType.TAB_PCDS_DYNAMIC_EX_HII)
        self.GenDynamicVpdPcds(DataType.TAB_PCDS_DYNAMIC_VPD)
        self.GenDynamicVpdPcds(DataType.TAB_PCDS_DYNAMIC_EX_VPD)
        
        #Components
        Components = {}
        IncludeFiles = {}
        Defines = {}
        for Arch in DataType.ARCH_LIST:
            for Item in self.Contents[Arch].Components:
                if GenInclude(Item[0], IncludeFiles, Arch):
                    IncludeFile = CleanString(Item[0][Item[0].upper().find(DataType.TAB_INCLUDE.upper() + ' ') + len(DataType.TAB_INCLUDE + ' ') : ])
                    IncludeFilePath = WorkspaceFile(self.WorkspaceDir, IncludeFile)
                    CheckFileExist(self.WorkspaceDir, IncludeFile, self.Platform.Header.FullPath, 'Components', Item[0])
                    NewItems = []
                    GetComponents(open(IncludeFilePath, 'r').read(), TAB_COMPONENTS, NewItems, TAB_COMMENT_SPLIT)
                    for NewItem in NewItems:
                        MergeArches(Components, self.GenComponent(NewItem, IncludeFilePath), Arch)
                    continue
                Status = GenDefines(Item[0], Arch, Defines)
                if Status == 0:       # Find DEFINE statement
                    pass
                elif Status == -1:    # Find DEFINE statement but in wrong format
                    ErrorMsg = "Wrong DEFINE statement '%s' found in section LibraryClasses in file '%s', correct format is 'DEFINE <VarName> = <PATH>'" % (Item, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                elif Status == 1:     # Not find DEFINE statement
                    MergeArches(Components, self.GenComponent(Item, self.Platform.Header.FullPath), Arch)
        self.Platform.Modules.IncludeFiles = IncludeFiles
        for Key in Components.keys():
            Key.Define = Defines
            Key.SupArchList = Components[Key]
            self.Platform.Modules.ModuleList.append(Key)
        
    #End of DscToPlatform
    
    #
    # Gen Library Class
    #
    def GenLibraryClass(self, Item, ContainerFile):
        List = GetSplitValueList(Item[0])
        if len(List) != 2:
            ErrorMsg = "Wrong statement '%s' found in section LibraryClasses in file '%s', correct format is '<LibraryClassKeyWord>|<LibraryInstance>'" % (Item, ContainerFile) 
            raise ParserError(PARSER_ERROR, msg = ErrorMsg)
        else:
            CheckFileType(List[1], '.Inf', ContainerFile, 'library class instance', Item[0])
            CheckFileExist(self.WorkspaceDir, List[1], ContainerFile, 'LibraryClasses', Item[0])
            if Item[1] == ['']:
                Item[1] = DataType.SUP_MODULE_LIST
        return (List[0], List[1]) + tuple(Item[1])
    
    #
    # Gen Component
    #
    def GenComponent(self, Item, ContainerFile):
        (InfFilename, ExecFilename) = GetExec(Item[0])
        CheckFileType(InfFilename, '.Inf', ContainerFile, 'component name', Item[0])
        CheckFileExist(self.WorkspaceDir, InfFilename, ContainerFile, 'component', Item[0])
        LibraryClasses = Item[1]
        BuildOptions = Item[2]
        Pcds = Item[3]
        Component = PlatformModuleClass()
        Component.FilePath = InfFilename
        Component.ExecFilePath = ExecFilename
        for Lib in LibraryClasses:
            List = GetSplitValueList(Lib)
            if len(List) != 2:
                ErrorMsg = "Wrong LibraryClass statement '%s' found in section Components in file '%s', correct format is '<ClassName>|<InfFilename>'" % (Lib, ContainerFile) 
                raise ParserError(PARSER_ERROR, msg = ErrorMsg)
            CheckFileType(List[1], '.Inf', ContainerFile, 'library instance of component ', Lib)
            CheckFileExist(self.WorkspaceDir, List[1], ContainerFile, 'library instance of component', Lib)
            Component.LibraryClasses.LibraryList.append(PlatformLibraryClass(List[0], List[1]))
        for BuildOption in BuildOptions:
            Key = GetBuildOption(BuildOption)
            Component.ModuleSaBuildOption.BuildOptionList.append(BuildOptionClass(Key[0], Key[1], Key[2]))
        for Pcd in Pcds:
            Type = Pcd[0]
            List = GetSplitValueList(Pcd[1])
            
            #
            # For FeatureFlag
            #
            if Type == DataType.TAB_PCDS_FEATURE_FLAG:
                if len(List) != 2:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>|TRUE/FALSE'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>|TRUE/FALSE'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    Component.PcdBuildDefinitions.append(PcdClass(TokenInfo[1], '', TokenInfo[0], '', '', List[1], Type, [], {}, []))
            #
            # For FixedAtBuild or PatchableInModule
            #
            if Type == DataType.TAB_PCDS_FIXED_AT_BUILD or Type == DataType.TAB_PCDS_PATCHABLE_IN_MODULE:
                List.append('')
                if len(List) < 3:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>|<Value>[|<MaxDatumSize>]'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>|<Value>[|<MaxDatumSize>]'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    Component.PcdBuildDefinitions.append(PcdClass(TokenInfo[1], '', TokenInfo[0], '', List[2], List[1], Type, [], {}, []))
            
            #
            # For Dynamic or DynamicEx
            #
            if Type == DataType.TAB_PCDS_DYNAMIC or Type == DataType.TAB_PCDS_DYNAMIC_EX:
                if len(List) != 1:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong Pcds%s statement '%s' found in section Components in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<PcdTokenName>'" % (Type, Pcd[1], ContainerFile) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    Component.PcdBuildDefinitions.append(PcdClass(TokenInfo[1], '', TokenInfo[0], '', '', '', Type, [], {}, []))                        
        
        return Component
    #End of GenComponent
    
    def GenFeatureFlagPcds(self, Type = ''):
        Pcds = {}
        Items = []
        for Arch in DataType.ARCH_LIST:
            if Type == DataType.TAB_PCDS_FEATURE_FLAG:
                Items = self.Contents[Arch].PcdsFeatureFlag
            else:
                pass
            
            for Item in Items:
                List = GetSplitValueList(Item)
                if len(List) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|TRUE/FALSE'" % (Item, Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|TRUE/FALSE'" % (Item, Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                MergeArches(Pcds, (TokenInfo[1], TokenInfo[0], List[1], Type), Arch)
        for Key in Pcds:
            Pcd = PcdClass(Key[0], '', Key[1], '', '', Key[2], Key[3], [], {}, [])
            Pcd.SupArchList = Pcds[Key]
            self.Platform.DynamicPcdBuildDefinitions.append(Pcd)
    
    def GenPcds(self, Type = ''):
        Pcds = {}
        Items = []
        for Arch in DataType.ARCH_LIST:
            if Type == DataType.TAB_PCDS_PATCHABLE_IN_MODULE:
                Items = self.Contents[Arch].PcdsPatchableInModule
            elif Type == DataType.TAB_PCDS_FIXED_AT_BUILD:
                Items = self.Contents[Arch].PcdsFixedAtBuild
            else:
                pass
            
            for Item in Items:
                List = GetSplitValueList(Item + DataType.TAB_VALUE_SPLIT * 2)
                if len(List) < 4:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<Value>[|<Type>|<MaximumDatumSize>]'" % (Item, Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<Value>[|<Type>|<MaximumDatumSize>]'" % (Item, Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    MergeArches(Pcds, (TokenInfo[1], TokenInfo[0], List[1], List[2], List[3], Type), Arch)
        for Key in Pcds:
            Pcd = PcdClass(Key[0], '', Key[1], Key[3], Key[4], Key[2], Key[5], [], {}, [])
            Pcd.SupArchList = Pcds[Key]
            self.Platform.DynamicPcdBuildDefinitions.append(Pcd)
    
    def GenSkuInfoList(self, SkuNameList, SkuInfo, VariableName = '', VariableGuid = '', VariableOffset = '', HiiDefaultValue = '', VpdOffset = '', DefaultValue = ''):
        if SkuNameList == None or SkuNameList == [] or SkuNameList == ['']:
            SkuNameList = ['DEFAULT']
        SkuInfoList = {}
        for Item in SkuNameList:
            if Item not in SkuInfo:
                return False, Item
            Sku = SkuInfoClass(Item, SkuInfo[Item], VariableName, VariableGuid, VariableOffset, HiiDefaultValue, VpdOffset, DefaultValue)
            SkuInfoList[Item] = Sku
        
        return True, SkuInfoList
            
    def GenDynamicDefaultPcds(self, Type = ''):
        Pcds = {}
        Items = []
        SkuInfoList = {}
        for Arch in DataType.ARCH_LIST:
            if Type == DataType.TAB_PCDS_DYNAMIC_DEFAULT:
                Items = self.Contents[Arch].PcdsDynamicDefault
            elif Type == DataType.TAB_PCDS_DYNAMIC_EX_DEFAULT:
                Items = self.Contents[Arch].PcdsDynamicExDefault
            else:
                pass
            
            for Item in Items:
                List = GetSplitValueList(Item[0] + DataType.TAB_VALUE_SPLIT)
                if len(List) < 3:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<Value>'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section Pcds%s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<Value>'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    MergeArches(Pcds, (TokenInfo[1], TokenInfo[0], List[1], List[2], Type), Arch)
        for Key in Pcds:
            (Status, SkuInfoList) = self.GenSkuInfoList(Item[1], self.Platform.SkuInfos.SkuInfoList, '', '', '', '', '', Key[2])
            if Status == False:
                ErrorMsg = "SKUID '%s' of '%s' not defined in file '%s'" % (SkuInfoList, Type, self.Platform.Header.FullPath) 
                raise ParserError(PARSER_ERROR, msg = ErrorMsg)
            Pcd = PcdClass(Key[0], '', Key[1], '', Key[3], Key[2], Key[4], [], SkuInfoList, [])
            Pcd.SupArchList = Pcds[Key]
            self.Platform.DynamicPcdBuildDefinitions.append(Pcd)
         
    def GenDynamicHiiPcds(self, Type = ''):
        Pcds = {}
        Items = []
        SkuInfoList = {}
        for Arch in DataType.ARCH_LIST:
            if Type == DataType.TAB_PCDS_DYNAMIC_HII:
                Items = self.Contents[Arch].PcdsDynamicHii
            elif Type == DataType.TAB_PCDS_DYNAMIC_EX_HII:
                Items = self.Contents[Arch].PcdsDynamicExHii
            else:
                pass
            
            for Item in Items:
                List = GetSplitValueList(Item[0] + DataType.TAB_VALUE_SPLIT * 2)
                if len(List) < 6:
                    ErrorMsg = "Wrong statement '%s' found in section %s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<String>|<VariableGuidCName>|<VariableOffset>[|<DefaultValue>[|<MaximumDatumSize>]]'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section %s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<String>|<VariableGuidCName>|<VariableOffset>[|<DefaultValue>[|<MaximumDatumSize>]]'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    MergeArches(Pcds, (TokenInfo[1], TokenInfo[0], List[1], List[2], List[3], List[4], List[5], Type), Arch)
        for Key in Pcds:
            (Status, SkuInfoList) = self.GenSkuInfoList(Item[1], self.Platform.SkuInfos.SkuInfoList, Key[2], Key[3], Key[4], Key[5], '', '')
            if Status == False:
                ErrorMsg = "SKUID '%s' of '%s' not defined in file '%s'" % (SkuInfoList, Type, self.Platform.Header.FullPath) 
                raise ParserError(PARSER_ERROR, msg = ErrorMsg)
            Pcd = PcdClass(Key[0], '', Key[1], '', Key[6], Key[5], Key[7], [], SkuInfoList, [])
            Pcd.SupArchList = Pcds[Key]
            self.Platform.DynamicPcdBuildDefinitions.append(Pcd)
    
    def GenDynamicVpdPcds(self, Type = ''):
        Pcds = {}
        Items = []
        SkuInfoList = {}
        for Arch in DataType.ARCH_LIST:
            if Type == DataType.TAB_PCDS_DYNAMIC_VPD:
                Items = self.Contents[Arch].PcdsDynamicVpd
            elif Type == DataType.TAB_PCDS_DYNAMIC_EX_VPD:
                Items = self.Contents[Arch].PcdsDynamicExVpd
            else:
                pass
            
            for Item in Items:
                List = GetSplitValueList(Item[0] + DataType.TAB_VALUE_SPLIT)
                if len(List) < 3:
                    ErrorMsg = "Wrong statement '%s' found in section %s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<VpdOffset>[|<MaximumDatumSize>]'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                
                TokenInfo = GetSplitValueList(List[0], DataType.TAB_SPLIT)
                if len(TokenInfo) != 2:
                    ErrorMsg = "Wrong statement '%s' found in section %s in file '%s', correct format is '<PcdTokenSpaceGuidCName>.<TokenCName>|<VpdOffset>[|<MaximumDatumSize>]'" % (Item[0], Type, self.Platform.Header.FullPath) 
                    raise ParserError(PARSER_ERROR, msg = ErrorMsg)
                else:
                    MergeArches(Pcds, (TokenInfo[1], TokenInfo[0], List[1], List[2], Type), Arch)
        for Key in Pcds:
            (Status, SkuInfoList) = self.GenSkuInfoList(Item[1], self.Platform.SkuInfos.SkuInfoList, '', '', '', '', Key[2], '')
            if Status == False:
                ErrorMsg = "SKUID '%s' of '%s' not defined in file '%s'" % (SkuInfoList, Type, self.Platform.Header.FullPath) 
                raise ParserError(PARSER_ERROR, msg = ErrorMsg)
            Pcd = PcdClass(Key[0], '', Key[1], '', Key[3], '', Key[4], [], SkuInfoList, [])
            Pcd.SupArchList = Pcds[Key]
            self.Platform.DynamicPcdBuildDefinitions.append(Pcd)
    
    def ShowDsc(self):
        print TAB_SECTION_START + TAB_INF_DEFINES + TAB_SECTION_END
        printDict(self.Defines.DefinesDictionary)

        for key in self.KeyList:
            for arch in DataType.ARCH_LIST_FULL:
                Command = "printList(TAB_SECTION_START + '" + \
                                    key + DataType.TAB_SPLIT + arch + \
                                    "' + TAB_SECTION_END, self.Contents[arch]." + key + ')'
                eval(Command)
       
    def ShowPlatform(self):
        m = self.Platform
        print 'Filename =', m.Header.FileName
        print 'FullPath =', m.Header.FullPath
        print 'BaseName =', m.Header.Name
        print 'Guid =', m.Header.Guid
        print 'Version =', m.Header.Version
        print 'DscSpecification =', m.Header.DscSpecification
        print 'SkuId =', m.Header.SkuIdName
        print 'SupArchList =', m.Header.SupArchList
        print 'BuildTargets =', m.Header.BuildTargets
        print 'OutputDirectory =', m.Header.OutputDirectory
        print 'BuildNumber =', m.Header.BuildNumber
        print 'MakefileName =', m.Header.MakefileName
        print 'Fdf =', m.FlashDefinitionFile.FilePath
        print '\nBuildOptions =', m.BuildOptions, m.BuildOptions.IncludeFiles
        for Item in m.BuildOptions.BuildOptionList:
            print '\t', Item.ToolChainFamily, Item.ToolChain, Item.Option, Item.SupArchList
        print '\nSkuIds =', m.SkuInfos.SkuInfoList, m.SkuInfos.IncludeFiles
        print '\nLibraries =', m.Libraries, m.Libraries.IncludeFiles
        for Item in m.Libraries.LibraryList:
            print '\t', Item.FilePath, Item.SupArchList, Item.Define
        print '\nLibraryClasses =', m.LibraryClasses, m.LibraryClasses.IncludeFiles
        for Item in m.LibraryClasses.LibraryList:
            print '\t', Item.Name, Item.FilePath, Item.SupModuleList, Item.SupArchList, Item.Define
        print '\nPcds =', m.DynamicPcdBuildDefinitions
        for Item in m.DynamicPcdBuildDefinitions:
            print '\tCname=', Item.CName, 'TSG=', Item.TokenSpaceGuidCName, 'Value=', Item.DefaultValue, 'Token=', Item.Token, 'Type=', Item.ItemType, 'Datum=', Item.DatumType, 'Size=', Item.MaxDatumSize, 'Arch=', Item.SupArchList, Item.SkuInfoList
            for Sku in Item.SkuInfoList.values():
                print '\t\t', str(Sku)
        print '\nComponents =', m.Modules.ModuleList, m.Modules.IncludeFiles
        for Item in m.Modules.ModuleList:
            print '\t', Item.FilePath, Item.ExecFilePath, Item.SupArchList
            for Lib in Item.LibraryClasses.LibraryList:
                print '\t\tLib:', Lib.Name, Lib.FilePath
            for Bo in Item.ModuleSaBuildOption.BuildOptionList:
                print '\t\tBuildOption:', Bo.ToolChainFamily, Bo.ToolChain, Bo.Option
            for Pcd in Item.PcdBuildDefinitions:
                print '\t\tPcd:', Pcd.CName, Pcd.TokenSpaceGuidCName, Pcd.MaxDatumSize, Pcd.DefaultValue, Pcd.ItemType
    
if __name__ == '__main__':
    w = os.getenv('WORKSPACE')
    f = os.path.join(w, 'Nt32Pkg/Nt32Pkg.dsc')
    p = Dsc(os.path.normpath(f), True, True, w)
    p.ShowPlatform()
