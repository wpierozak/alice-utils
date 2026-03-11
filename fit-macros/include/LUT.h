#include "CommonUtils/ConfigurableParamHelper.h"
#include "DataFormatsFIT/LookUpTable.h"
#include "Framework/Logger.h"
#include "CommonConstants/LHCConstants.h"

std::vector<o2::fit::EntryFEE> readLUTFromFile(const std::string filePath, const std::string objectName)
{
    TFile file(filePath.c_str(), "READ");
    if(file.IsOpen() == false) {
    LOGP(fatal, "Failed to open {}", filePath);
    }
    LOGP(info, "Successfully opened {}", filePath);

    std::vector<o2::fit::EntryFEE>* lut = nullptr;
    file.GetObject<std::vector<o2::fit::EntryFEE>>(objectName.c_str(), lut);

    if(lut == nullptr) {
    LOGP(fatal, "Failed to read object {}", objectName);
    }
    LOGP(info, "Successfully get {} object", objectName);

    std::vector<o2::fit::EntryFEE> lutCopy = *lut;
    file.Close();

    return std::move(lutCopy);
}

inline bool operator==(const o2::fit::EntryFEE& lhs, const o2::fit::EntryFEE& rhs)
{
  auto comparer = [](const o2::fit::EntryFEE& e) { 
    return std::tie(
      e.mEntryCRU.mLinkID, e.mEntryCRU.mEndPointID, e.mEntryCRU.mCRUID, e.mEntryCRU.mFEEID,
      e.mChannelID, e.mLocalChannelID, e.mModuleType, e.mModuleName, 
      e.mBoardHV, e.mChannelHV, e.mSerialNumberMCP, e.mCableHV, e.mCableSignal
    ); 
  };
  return comparer(lhs) == comparer(rhs);
}
