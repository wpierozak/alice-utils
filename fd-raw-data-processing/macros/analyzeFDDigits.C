#if !defined(__CLING__) || defined(__ROOTCLING__)

// ROOT
#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TFitResult.h>

// CCDB
#include "CCDB/BasicCCDBManager.h"
#include "DataFormatsParameters/GRPLHCIFData.h"
#include "CommonDataFormat/BunchFilling.h"

#include <memory>
#include "DataFormatsFV0/Digit.h"
#include <fairlogger/Logger.h>
#include "CommonConstants/LHCConstants.h"

#include "FillingSchema.h"

TTree* getTree(TFile& file)
{
    return (TTree*) file.Get("o2sim");
}

void analyzeFDDigits(const std::string fdDigitsFileName, const int runNumber, const bool onlyCollBc = false)
{
  std::unique_ptr<o2::BunchFilling> bcPattern = getBcPattern(runNumber);
  if(bcPattern == nullptr && onlyCollBc) {
    return;
  }

  std::unique_ptr<TFile> fdDigits(TFile::Open(fdDigitsFileName.c_str(), "READ"));
  if (!fdDigits || fdDigits->IsZombie()) {
    LOG(error) << "Failed to open input digits file " << fdDigitsFileName;
    return;
  }

  TTree* fdTree = getTree(*fdDigits);
  if(!fdTree) {
    LOG(error) << "Failed to get FD digits tree";
    return;
  }

  std::vector<o2::fv0::Digit> digits;
  std::vector<o2::fv0::Digit>* digitPtr = &digits;

  std::vector<o2::fv0::ChannelData> channelData;
  std::vector<o2::fv0::ChannelData>* channelDataPtr = &channelData;

  fdTree->SetBranchAddress("FV0DigitBC", &digitPtr);
  fdTree->SetBranchAddress("FV0DigitCh", &channelDataPtr);
  
  size_t nEntries = fdTree->GetEntries();

  std::string outputfilename = Form("fd_analysis_run%i_collBC%i.root", runNumber, onlyCollBc);

  std::unique_ptr<TFile> results = std::make_unique<TFile>(outputfilename.c_str(), "RECREATE");
  std::unique_ptr<TCanvas> canvas = std::make_unique<TCanvas>();
  std::unique_ptr<TH1D> adcMip = std::make_unique<TH1D>("adc_mip", "ADC and MIP estimation", 4096, 0, 4096);
  std::unique_ptr<TH1D> eventsVsBc = std::make_unique<TH1D>("events_vs_bc", "Events vs BC",  o2::constants::lhc::LHCMaxBunches, 0,  o2::constants::lhc::LHCMaxBunches);
  std::unique_ptr<TH2D> timeVsCharge = std::make_unique<TH2D>("time_vs_charge", "Time vs Charge",  4096, 0, 4096, 4096, -2048, 2047);
  std::unique_ptr<TH1D> timeHist = std::make_unique<TH1D>("time_hist", "CFD time",  4096, -2048, 2047);

  for (size_t idx = 0; idx < nEntries; idx++) {
    fdTree->GetEntry(idx);
    size_t digitsSize = digits.size();

    for (size_t digitIdx = 0; digitIdx < digitsSize; digitIdx++) {
      const o2::fv0::Digit& digit = digits[digitIdx];

      if(onlyCollBc && !bcPattern->testBC(digit.getBC())) {
        continue;
      }

      const auto& bcChannelData = digit.getBunchChannelData(channelData);
      eventsVsBc->Fill(digit.getBC());

      // There is only one channel for FD
      for(const auto& data: channelData) {
        adcMip->Fill(data.QTCAmpl);
        timeVsCharge->Fill(data.QTCAmpl, data.CFDTime);
        timeHist->Fill(data.CFDTime);
      }      
    }
  }

  // Mip calculation

  double mostCommonAdcValue = adcMip->GetMaximumBin();
  double lowB = mostCommonAdcValue - 0.28 * mostCommonAdcValue;
  double upperB = mostCommonAdcValue + 0.28 * mostCommonAdcValue;

  std::unique_ptr<TF1> gauss = std::make_unique<TF1>("restricted_gaus", "gaus", lowB, upperB);
  gauss->SetParameters(adcMip->GetMaximum(), mostCommonAdcValue, mostCommonAdcValue * 0.1);
  TFitResultPtr mipFit = adcMip->Fit(gauss.get(), "SR");

  adcMip->Draw();
  mipFit->Draw("SAME");
  canvas->SaveAs("hist.png");

  adcMip->Write();
  eventsVsBc->Write();
  timeVsCharge->Write();
  timeHist->Write();
}
#endif