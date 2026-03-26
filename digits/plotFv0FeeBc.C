#if !defined(__CLING__) || defined(__ROOTCLING__)

#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TCanvas.h>

#include <memory>
#include "DataFormatsFV0/Digit.h"
#include <fairlogger/Logger.h>
#include "CommonConstants/LHCConstants.h"

void plotFv0FeeBc(std::string fv0DigitFile, std::string outFileName = "events-vs-bc.root")
{
  std::unique_ptr<TFile> digiFile(TFile::Open(digiFName.c_str()));
  if (!digiFile || digiFile->IsZombie()) {
    LOG(error) << "Failed to open input digits file " << digiFName;
    return;
  }

  TTree* digiTree = (TTree*)digiFile->Get("o2sim");
  if (!digiTree) {
    LOG(error) << "Failed to get digits tree";
    return;
  }

  std::vector<o2::fv0::Digit> fv0digit;
  std::vector<o2::fv0::Digit>*fv0digitPtr = &fv0digit;

  digiTree->SetBranchAddress("FV0DigitBC", &fv0digitPtr);
  size_t nEntries = digiTree->GetEntries();

  std::unique_ptr<TH1F> hist = std::make_unique<TH1F>("entryVsBc", "Entry vs BC", o2::constants::lhc::LHCMaxBunches, 0, o2::constants::lhc::LHCMaxBunches);
  for (UInt_t idx = 0; idx < nEntries; idx++) {
    digiTree->GetEntry(idx);
    int nbc = fv0digit.size();
    for (int ibc = 0; ibc < nbc; ibc++) {
      hist->Fill(fv0digit[ibc].getBC(), 1);
    }
  }

  hist->Draw();
  std::unique_ptr<TCanvas> canvas = std::make_unique<TCanvas>();
  canvas->SaveAs("entry-vs-bc.png");

  std::unique_ptr<TFile> outFile(TFile::Open(outFileName.c_str(), "RECREATE"));
  if (!outFile || outFile->IsZombie()) {
    LOG(error) << "Failed to open output file " << outFileName;
    return;
  }
  hist->Write();
  outFile->Close();
}
#endif