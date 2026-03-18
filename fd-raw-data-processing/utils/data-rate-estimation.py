# Fill parameters
mu = 0.0324
coliding_bunches = 2092
bc_time = 25 * 1e-9
bc_max = 3564

# Trigger rate
trg_rate = 1.0/(bc_time) * coliding_bunches/bc_max * mu

# Readout parameters
# RDHv7: https://github.com/AliceO2Group/AliceO2/blob/dev/DataFormats/Headers/include/Headers/RAWDataHeader.h#L28
rdh_header_size = 64
heart_beat_orbits = 32

# FEE data parameters
# Raw data structure: https://github.com/AliceO2Group/AliceO2/blob/dev/DataFormats/Detectors/FIT/common/include/DataFormatsFIT/RawEventData.h
fee_event_header_size = 10
fee_event_data_size = 5
fee_data_payloads_per_event = 1
fee_data_size = fee_event_header_size + fee_event_data_size * fee_data_payloads_per_event

# Data rate
# FIT FEE forwards data to CRU already in packet formats with proper RDH header for each HBF
data_rate_correction = 1.0/(bc_time * heart_beat_orbits) * rdh_header_size * coliding_bunches/bc_max * mu
data_rate = trg_rate * fee_data_size + data_rate_correction

print(f"Expected trigger rate: {trg_rate/1000} kHz. Expected data rate: {data_rate*1e-9} GB/s ({data_rate * 60e-9}) GB/min")