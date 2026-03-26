// Copyright 2019-2020 CERN and copyright holders of ALICE O2.
// See https://alice-o2.web.cern.ch/copyright for details of the copyright holders.
// All rights not expressly granted are reserved.
//
// This software is distributed under the terms of the GNU General Public
// License v3 (GPL Version 3), copied verbatim in the file "COPYING".
//
// In applying this license CERN does not waive the privileges and immunities
// granted to it by virtue of its status as an Intergovernmental Organization
// or submit itself to any jurisdiction.
#if !defined(__CLING__) || defined(__ROOTCLING__)
#include <iostream>
#include <array>
#endif


R__LOAD_LIBRARY(libO2CommonUtils)
R__LOAD_LIBRARY(libO2DataFormatsFIT)

#include "CommonUtils/ConfigurableParamHelper.h"
#include "DataFormatsFIT/LookUpTable.h"
#include "Framework/Logger.h"
#include "CommonConstants/LHCConstants.h"

void printLUTFromTFile(const std::string filePath, const std::string objectName = "LookupTable")
{
  TFile file(filePath.c_str(), "READ");
  if(file.IsOpen() == false) {
    LOGP(error, "Failed to open {}", filePath);
    return;
  }
  LOGP(info, "Successfully opened {}", filePath);

  std::vector<o2::fit::EntryFEE>* lut = nullptr;
  file.GetObject<std::vector<o2::fit::EntryFEE>>(objectName.c_str(), lut);

  if(lut == nullptr) {
    LOGP(error, "Failed to read object {}", objectName);
    return;
  }
  LOGP(info, "Successfully get {} object", objectName);

  for(const auto& entry: (*lut)) {
    std::cout << entry << std::endl;
  }

  file.Close();
}