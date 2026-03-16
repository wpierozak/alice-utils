#if !defined(__CLING__) || defined(__ROOTCLING__)

#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <algorithm> // Required for std::max

#include <memory>
#include "DataFormatsFV0/Digit.h"
#include <fairlogger/Logger.h>
#include "CommonConstants/LHCConstants.h"

void compareFDFV0BC(const std::string fdHistogramsFileName, const std::string fv0HistogramFileName, const std::string pm)
{
  std::unique_ptr<TFile> fdHistogramFile(TFile::Open(fdHistogramsFileName.c_str()));
  if (!fdHistogramFile || fdHistogramFile->IsZombie()) {
    LOG(error) << "Failed to open input digits file " << fdHistogramsFileName;
    return;
  }

  std::unique_ptr<TFile> fv0HistogramFile(TFile::Open(fv0HistogramFileName.c_str()));
  if (!fv0HistogramFile || fv0HistogramFile->IsZombie()) {
    LOG(error) << "Failed to open input digits file " << fv0HistogramFileName;
    return;
  }

  TH1F* fdHistogram = nullptr; 
  fdHistogramFile->GetObject("entryVsBc", fdHistogram);
  if(fdHistogram == nullptr) {
    LOG(error) << "Failed to get FD histogram";
    return;
  }

  TH2F* fv0Histogram = nullptr;
  fv0HistogramFile->GetObject("ccdb_object", fv0Histogram);
  if(fv0Histogram == nullptr) {
    LOG(error) << "Failed to get FV0 histogram";
    return;
  }

  TAxis* yAxis = fv0Histogram->GetYaxis();
  int pmBin = yAxis->FindBin(pm.c_str());

  if (pmBin == -1) {
    LOG(error) << "Label " << pm << " not found on the Y-axis!";
    return;
  }

  std::unique_ptr<TFile> result = std::make_unique<TFile>("fv0-fd-bc.root", "RECREATE");
  result->cd(); 

  TH1D* pmProjection = fv0Histogram->ProjectionX("projection_fv0", pmBin, pmBin);

  std::unique_ptr<TCanvas> canvas = std::make_unique<TCanvas>("compare_canvas", "FV0 vs FD Comparison", 800, 600);

  
  double absoluteMax = std::max(pmProjection->GetMaximum(), fdHistogram->GetMaximum());
  pmProjection->SetMaximum(absoluteMax * 1.1);

  pmProjection->SetTitle("FV0 vs FD BCID Comparison");
  pmProjection->SetLineColor(kBlue);
  pmProjection->SetLineWidth(1);
  pmProjection->Draw("HIST");

  fdHistogram->SetLineColor(kRed);
  fdHistogram->SetLineWidth(2);
  fdHistogram->Draw("HIST SAMES");

  std::string fv0Legend = "FV0 PM" + pm;

  std::unique_ptr<TLegend> legend = std::make_unique<TLegend>(0.7, 0.7, 0.9, 0.9);
  
  legend->AddEntry(pmProjection, fv0Legend.c_str(), "l"); 
  legend->AddEntry(fdHistogram, "FD", "l");
  legend->Draw();
  
  canvas->Update();
  canvas->Write("comparision");

  result->Close();
}
#endif