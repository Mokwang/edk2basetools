## @file
# This file is the loader of "Boot Loader Development Kit".
#
# INTEL CONFIDENTIAL
#
# Copyright (c) 2010 Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to 
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intels prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be
# express and approved by Intel in writing.
#
##


#string table starts here...

#strings are classified as following types
#    MSG_...: it is a message string
#    ERR_...: it is a error string
#    WRN_...: it is a warning string
#    LBL_...: it is a UI label (window title, control label, etc.)
#    MNU_...: it is a menu item label
#    HLP_...: it is a help string
#    CFG_...: it is a config string used in module. Do not need to translate it.
#    XRC_...: it is a user visible string from xrc file

MAP_FILE_COMMENT_TEMPLATE = \
"""
## @file
#
#  THIS IS AUTO-GENERATED FILE BY BPDG TOOLS AND PLEASE DO NOT MAKE MODIFICATION.
#
#  This file lists all VPD informations for a platform fixed/adjusted by BPDG tool.
# 
# Copyright (c) 2010, Intel Corporation. All rights reserved.<BR>
# This program and the accompanying materials
# are licensed and made available under the terms and conditions of the BSD License
# which accompanies this distribution.  The full text of the license may be found at
# http://opensource.org/licenses/bsd-license.php
#
# THE PROGRAM IS DISTRIBUTED UNDER THE BSD LICENSE ON AN "AS IS" BASIS,
# WITHOUT WARRANTIES OR REPRESENTATIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED.
#
"""



LBL_BPDG_LONG_UNI           = (u"Intel Binary Product Data Generation (BPDG) Application")
LBL_BPDG_VERSION            = (u"0.1")
LBL_BPDG_USAGE              = \
(
"""
Usage: bpdg options -o Filename.bin -m Filename.map Filename.txt
Intel(r) Binary Product Data Generation Tool (Intel(r) BPDG)
Copyright (c) 2010 Intel Corporation All Rights Reserved.

Required Flags:
  -o VPD_FILENAME, --vpd-filename=VPD_FILENAME
            Specify the file name for the VPD binary file
  -m FILENAME, --map-filename=FILENAME
            Generate file name for consumption during the build that contains 
            the mapping of Pcd name, offset, datum size and value derived 
            from the input file and any automatic calculations.
""" 
)

MSG_OPTION_HELP             = ("Show this help message and exit.")
MSG_OPTION_DEBUG_LEVEL      = ("Print DEBUG statements, where DEBUG_LEVEL is 0-9.")
MSG_OPTION_VERBOSE          = ("Print informational statements.")
MSG_OPTION_SILENT           = ("Only the exit code will be returned, all informational and error messages will not be displayed.")
MSG_OPTION_QUIET            = ("Returns the exit code and will display only error messages.")
MSG_OPTION_VPD_FILENAME     = ("Specify the file name for the VPD binary file.")
MSG_OPTION_MAP_FILENAME     = ("Generate file name for consumption during the build that contains the mapping of Pcd name, offset, datum size and value derived from the input file and any automatic calculations.")
MSG_OPTION_FORCE            = ("Disable prompting the user for overwriting files as well as for missing input content.")

ERR_INVALID_DEBUG_LEVEL     = ("Invalid level for debug message. Only "
                                "'DEBUG', 'INFO', 'WARNING', 'ERROR', "
                                "'CRITICAL' are supported for debugging "
                                "messages.")