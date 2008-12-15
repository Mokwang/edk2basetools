## @file
# This file is for installed package information database operations
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
import sqlite3
import os
import time
import EdkLogger as EdkLogger

from CommonDataClass import DistributionPackageClass

## IpiDb
#
# This class represents the installed package information databse
# Add/Remove/Get installed distribution package information here.
# 
# 
# @param object:      Inherited from object class
# @param DbPath:      A string for the path of the database
#
# @var Conn:          Connection of the database
# @var Cur:           Cursor of the connection
#
class IpiDb(object):
    def __init__(self, DbPath):
        self.Conn = sqlite3.connect(DbPath)
        self.Cur = self.Conn.cursor()
        self.DpTable = 'DpInfo'
        self.PkgTable = 'PkgInfo'
        self.ModInPkgTable = 'ModInPkgInfo'
        self.StandaloneModTable = 'StandaloneModInfo'
    
    ## Initialize build database
    #
    #
    def InitDatabase(self):
        EdkLogger.verbose("\nInitialize IPI database started ...")
        
        #
        # Create new table
        #
        SqlCommand = """create table IF NOT EXISTS %s (DpGuid TEXT NOT NULL,
                                                       DpVersion TEXT NOT NULL,
                                                       InstallTime REAL NOT NULL,
                                                       PkgFileName TEXT,
                                                       PRIMARY KEY (DpGuid, DpVersion)
                                                      )""" % self.DpTable
        self.Cur.execute(SqlCommand)
        
        SqlCommand = """create table IF NOT EXISTS %s (PackageGuid TEXT NOT NULL,
                                                       PackageVersion TEXT NOT NULL,
                                                       InstallTime REAL NOT NULL,
                                                       DpGuid TEXT,
                                                       DpVersion TEXT,
                                                       InstallPath TEXT,
                                                       PRIMARY KEY (PackageGuid, PackageVersion)
                                                      )""" % self.PkgTable
        self.Cur.execute(SqlCommand)
        
        SqlCommand = """create table IF NOT EXISTS %s (ModuleGuid TEXT NOT NULL,
                                                       ModuleVersion TEXT NOT NULL,
                                                       InstallTime REAL NOT NULL,
                                                       PackageGuid TEXT,
                                                       PackageVersion TEXT,
                                                       InstallPath TEXT,
                                                       PRIMARY KEY (ModuleGuid, ModuleVersion)
                                                      )""" % self.ModInPkgTable
        self.Cur.execute(SqlCommand)
        
        SqlCommand = """create table IF NOT EXISTS %s (ModuleGuid TEXT NOT NULL,
                                                       ModuleVersion TEXT NOT NULL,
                                                       InstallTime REAL NOT NULL,
                                                       DpGuid TEXT,
                                                       DpVersion TEXT,
                                                       InstallPath TEXT,
                                                       PRIMARY KEY (ModuleGuid, ModuleVersion)
                                                      )""" % self.StandaloneModTable
        self.Cur.execute(SqlCommand)
        
        self.Conn.commit()
        
        EdkLogger.verbose("Initialize IPI database ... DONE!")

    ## Add a distribution install information from DpObj
    #
    # @param DpObj:
    #
    def AddDPObject(self, DpObj):
        self.AddDp(DpObj.Header.Guid, DpObj.Header.Version, DpObj.Header.FileName)
        for PkgKey in DpObj.PackageSurfaceArea.keys():
            PkgGuid = PkgKey[0]
            PkgVersion = PkgKey[1]
            PkgInstallPath = PkgKey[2]
            self.AddPackage(PkgGuid, PkgVersion, DpObj.Header.Guid, DpObj.Header.Version, PkgInstallPath)
            PkgObj = DpObj.PackageSurfaceArea[PkgKey]
            for ModKey in PkgObj.Modules.keys():
                ModGuid = ModKey[0]
                ModVersion = ModKey[1]
                ModInstallPath = ModKey[2]
                self.AddModuleInPackage(ModGuid, ModVersion, PkgGuid, PkgVersion, ModInstallPath)

        for ModKey in DpObj.ModuleSurfaceArea.keys():
            ModGuid = ModKey[0]
            ModVersion = ModKey[1]
            ModInstallPath = ModKey[2]
            self.AddStandaloneModule(ModGuid, ModVersion, DpObj.Header.Guid, DpObj.Header.Version, ModInstallPath)
            
            
    ## Add a distribution install information
    #
    # @param Guid:  
    # @param Version:
    # @param PkgFileName:
    #
    def AddDp(self, Guid, Version, PkgFileName = None):
        
        if Version == None or len(Version.strip()) == 0:
            Version = 'N/A'
        
        #
        # Add newly installed DP information to DB.
        #
        if PkgFileName == None or len(PkgFileName.strip()) == 0:
            PkgFileName = 'N/A'
        (Guid, Version, PkgFileName) = self.__ConvertToSqlString((Guid, Version, PkgFileName))
        CurrentTime = time.time()
        SqlCommand = """insert into %s values('%s', '%s', %s, '%s')""" % (self.DpTable, Guid, Version, CurrentTime, PkgFileName)
        self.Cur.execute(SqlCommand)
        self.Conn.commit()
        
        
    ## Add a package install information
    #
    # @param Guid:  
    # @param Version:
    # @param DpGuid:  
    # @param DpVersion:
    # @param Path
    #
    def AddPackage(self, Guid, Version, DpGuid = None, DpVersion = None, Path = ''):
        
        if Version == None or len(Version.strip()) == 0:
            Version = 'N/A'
        
        if DpGuid == None or len(DpGuid.strip()) == 0:
            DpGuid = 'N/A'
        
        if DpVersion == None or len(DpVersion.strip()) == 0:
            DpVersion = 'N/A'
        
        #
        # Add newly installed package information to DB.
        #
        (Path) = self.__ConvertToSqlString((Path))
        CurrentTime = time.time()
        SqlCommand = """insert into %s values('%s', '%s', %s, '%s', '%s', '%s')""" % (self.PkgTable, Guid, Version, CurrentTime, DpGuid, DpVersion, Path)
        self.Cur.execute(SqlCommand)
        self.Conn.commit()
        
    ## Add a module that from a package install information
    #
    # @param Guid:  
    # @param Version:
    # @param PkgFileName:
    #
    def AddModuleInPackage(self, Guid, Version, PkgGuid = None, PkgVersion = None, Path = ''):
        
        if Version == None or len(Version.strip()) == 0:
            Version = 'N/A'
        
        if PkgGuid == None or len(PkgGuid.strip()) == 0:
            PkgGuid = 'N/A'
        
        if PkgVersion == None or len(PkgVersion.strip()) == 0:
            PkgVersion = 'N/A'
        
        #
        # Add module from package information to DB.
        #
        (Path) = self.__ConvertToSqlString((Path))
        CurrentTime = time.time()
        SqlCommand = """insert into %s values('%s', '%s', %s, '%s', '%s', '%s')""" % (self.ModInPkgTable, Guid, Version, CurrentTime, PkgGuid, PkgVersion, Path)
        self.Cur.execute(SqlCommand)
        self.Conn.commit()
    
    ## Add a module that is standalone install information
    #
    # @param Guid:  
    # @param Version:
    # @param PkgFileName:
    #
    def AddStandaloneModule(self, Guid, Version, DpGuid = None, DpVersion = None, Path):
        
        if Version == None or len(Version.strip()) == 0:
            Version = 'N/A'
        
        if DpGuid == None or len(DpGuid.strip()) == 0:
            DpGuid = 'N/A'
        
        if DpVersion == None or len(DpVersion.strip()) == 0:
            DpVersion = 'N/A'
        
        #
        # Add module standalone information to DB.
        #
        (Path) = self.__ConvertToSqlString((Path))
        CurrentTime = time.time()
        SqlCommand = """insert into %s values('%s', '%s', %s, '%s', '%s', '%s')""" % (self.StandaloneModTable, Guid, Version, CurrentTime, DpGuid, DpVersion, Path)
        self.Cur.execute(SqlCommand)
        self.Conn.commit()
        
    ## Remove a distribution install information, if no version specified, remove all DPs with this Guid.
    #
    # @param DpObj:  
    #
    def RemoveDpObj(self, DpObj):
        
        DpGuid = DpObj.Header.Guid
        DpVersion = DpObj.Header.Version
        
        SqlCommand = """delete from %s where DpGuid ='%s' and DpVersion = '%s'""" % (self.DpTable, DpGuid, DpVersion)
        self.Cur.execute(SqlCommand)
        
        SqlCommand = """delete from %s where DpGuid ='%s' and DpVersion = '%s'""" % (self.StandaloneModTable, DpGuid, DpVersion)
        self.Cur.execute(SqlCommand)
        
        SqlCommand = """delete from %s as t1, %s as t2 where 
                        t1.PackageGuid = t2.PackageGuid and t1.PackageVersion = t2.PackageVersion and t2.DpGuid ='%s' and t2.DpVersion = '%s')""" % (self.ModInPkgTable, self.PkgTable, DpGuid, DpVersion)
        self.Cur.execute(SqlCommand)
        
        
        self.Conn.commit()
        
        
    ## Get a list of distribution install information.
    #
    # @param Guid:  
    # @param Version:  
    #
    def GetDp(self, Guid, Version):
        
        if Version == None or len(Version.strip()) == 0:
            Version = 'N/A'
            EdkLogger.verbose("\nGetting list of DP install information started ...")
            (DpGuid, DpVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where DpGuid ='%s'""" % (self.Table, DpGuid)
            self.Cur.execute(SqlCommand)
        
        else:
            EdkLogger.verbose("\nGetting DP install information started ...")
            (DpGuid, DpVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where DpGuid ='%s' and DpVersion = '%s'""" % (self.DpTable, DpGuid, DpVersion)
            self.Cur.execute(SqlCommand)

        DpList = []
        for DpInfo in self.Cur:
            DpGuid = DpInfo[0]
            DpVersion = DpInfo[1]
            InstallTime = DpInfo[2]
            PkgFileName = DpInfo[3]
            DpList.append((DpGuid, DpVersion, InstallTime, PkgFileName))
        
        EdkLogger.verbose("Getting DP install information ... DONE!")
        return DpList
    
    ## Get a list of package information.
    #
    # @param Guid:  
    # @param Version:  
    #
    def GetPackage(self, Guid, Version, DpGuid = '', DpVersion = ''):
        
        if DpVersion == '' or DpGuid == '':

            (PackageGuid, PackageVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where PackageGuid ='%s' and PackageVersion = '%s'""" % (self.PkgTable, PackageGuid, PackageVersion)
            self.Cur.execute(SqlCommand)
        
        elif Version == None or len(Version.strip()) == 0:
            
            SqlCommand = """select * from %s where PackageGuid ='%s'""" % (self.PkgTable, Guid)
            self.Cur.execute(SqlCommand)
        else:
            (PackageGuid, PackageVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where PackageGuid ='%s' and PackageVersion = '%s'
                            and DpGuid = '%s' and DpVersion = '%s'""" % (self.PkgTable, PackageGuid, PackageVersion, DpGuid, DpVersion)
            self.Cur.execute(SqlCommand)

        PkgList = []
        for PkgInfo in self.Cur:
            PkgGuid = PkgInfo[0]
            PkgVersion = PkgInfo[1]
            InstallTime = PkgInfo[2]
            InstallPath = PkgInfo[5]
            PkgList.append((PkgGuid, PkgVersion, InstallTime, DpGuid, DpVersion, InstallPath))
        
        return PkgList
    
    ## Get a list of module in package information.
    #
    # @param Guid:  
    # @param Version:  
    #
    def GetModInPackage(self, Guid, Version, PkgGuid = '', PkgVersion = ''):
        
        if PkgVersion == '' or PkgGuid == '':

            (ModuleGuid, ModuleVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where ModuleGuid ='%s' and ModuleVersion = '%s'""" % (self.ModInPkgTable, ModuleGuid, ModuleVersion)
            self.Cur.execute(SqlCommand)
        
        else:
            (ModuleGuid, ModuleVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where ModuleGuid ='%s' and ModuleVersion = '%s' and PackageGuid ='%s' and PackageVersion = '%s'
                            """ % (self.ModInPkgTable, ModuleGuid, ModuleVersion, PkgGuid, PkgVersion)
            self.Cur.execute(SqlCommand)

        ModList = []
        for ModInfo in self.Cur:
            ModGuid = ModInfo[0]
            ModVersion = ModInfo[1]
            InstallTime = ModInfo[2]
            InstallPath = ModInfo[5]
            ModList.append((ModGuid, ModVersion, InstallTime, PkgGuid, PkgVersion, InstallPath))
        
        return ModList
    
    ## Get a list of module standalone.
    #
    # @param Guid:  
    # @param Version:  
    #
    def GetStandaloneModule(self, Guid, Version, DpGuid = '', DpVersion = ''):
        
        if PkgVersion == '' or PkgGuid == '':

            (ModuleGuid, ModuleVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where ModuleGuid ='%s' and ModuleVersion = '%s'""" % (self.StandaloneModTable, ModuleGuid, ModuleVersion)
            self.Cur.execute(SqlCommand)
        
        else:
            (ModuleGuid, ModuleVersion) = self.__ConvertToSqlString((Guid, Version))
            SqlCommand = """select * from %s where ModuleGuid ='%s' and ModuleVersion = '%s' and DpGuid ='%s' and DpVersion = '%s'
                            """ % (self.StandaloneModTable, ModuleGuid, ModuleVersion, DpGuid, DpVersion)
            self.Cur.execute(SqlCommand)

        ModList = []
        for ModInfo in self.Cur:
            ModGuid = ModInfo[0]
            ModVersion = ModInfo[1]
            InstallTime = ModInfo[2]
            InstallPath = ModInfo[5]
            ModList.append((ModGuid, ModVersion, InstallTime, DpGuid, DpVersion, InstallPath))
        
        return ModList
    
    ## Close entire database
    #
    # Close the connection and cursor
    #
    def CloseDb(self):
        
        self.Cur.close()
        self.Conn.close()

    ## Convert To Sql String
    #
    # 1. Replace "'" with "''" in each item of StringList
    # 
    # @param StringList:  A list for strings to be converted
    #
    def __ConvertToSqlString(self, StringList):
        return map(lambda s: s.replace("'", "''") , StringList)
##
#
# This acts like the main() function for the script, unless it is 'import'ed into another
# script.
#
if __name__ == '__main__':
    EdkLogger.Initialize()
    EdkLogger.SetLevel(EdkLogger.DEBUG_0)
    
    Db = IpiDb(DATABASE_PATH)
    Db.InitDatabase()

    