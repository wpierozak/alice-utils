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
R__LOAD_LIBRARY(libO2CCDB)
R__LOAD_LIBRARY(libO2DataFormatsFIT)

#include "CommonUtils/ConfigurableParamHelper.h"
#include "DataFormatsFIT/LookUpTable.h"
#include "CCDB/CcdbApi.h"
#include "CCDB/CCDBTimeStampUtils.h"
#include "Framework/Logger.h"
#include "CommonConstants/LHCConstants.h"

void updateLUT(bool dumpToFile = false)
{
  const string productionCCDBUrl = "http://alice-ccdb.cern.ch";
  const string testCCDBUrl = "http://ccdb-test.cern.ch:8080";

  o2::ccdb::CcdbApi productionCCDB;
  productionCCDB.init(productionCCDBUrl);
  const std::string ccdbPath = "FV0/Config/LookupTable";
  std::map<std::string, std::string> metadata;
  
  long timestamp = o2::ccdb::getCurrentTimestamp();

  std::unique_ptr<std::vector<o2::fit::EntryFEE>> lut(productionCCDB.retrieveFromTFileAny<std::vector<o2::fit::EntryFEE>>(ccdbPath, metadata, timestamp));

  if (!lut) {
    LOGP(fatal, "LUT object not found in {}/{} for timestamp {}.", productionCCDBUrl, ccdbPath, timestamp);
    return;
  }

  std::cout << "New lookup table: " << std::endl;
  for(const auto& entry: (*lut)) {
    std::cout << entry << std::endl;
  }

  o2::fit::EntryFEE FDentry;
  FDentry.mEntryCRU.mLinkID = 0;
  FDentry.mEntryCRU.mEndPointID = 0;
  FDentry.mEntryCRU.mCRUID = 0; //
  FDentry.mEntryCRU.mFEEID = 0x55ef; //
  FDentry.mChannelID = "50";
  FDentry.mLocalChannelID = "11";
  FDentry.mModuleType = "PM";
  FDentry.mModuleName = "A8";

  lut->push_back(FDentry);

  o2::ccdb::CcdbApi testCCDB;
  testCCDB.init(testCCDBUrl);

  int code = testCCDB.storeAsTFileAny(lut.get(), ccdbPath, metadata, 1772048004000, 1885802400000);
  if(code == 0) {
    LOGP(info, "Finished");
  } else {
    LOGP(fatal, "FAILED");
  }

  if(dumpToFile) {
    
  }
  std::cout << "New lookup table: " << std::endl;
  for(const auto& entry: (*lut)) {
    std::cout << entry << std::endl;
  }
}