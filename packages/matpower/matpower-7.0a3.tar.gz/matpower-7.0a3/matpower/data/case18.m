function mpc = case18
%CASE18  Power flow data for 18 bus distribution system
%    Please see CASEFORMAT for details on the case file format.
%
%    Data from ...
%       W. M. Grady, M. J. Samotyj and A. H. Noyola, "The application of
%       network objective functions for actively minimizing the impact of
%       voltage harmonics in power systems," IEEE Transactions on Power
%       Delivery, vol. 7, no. 3, pp. 1379-1386, Jul 1992.
%       https://doi.org/10.1109/61.141855

%% MATPOWER Case Format : Version 2
mpc.version = '2';

%% system MVA base
mpc.baseMVA = 1;

%% bus data
% bus_i  type  Pd  Qd  Gs  Bs  area  Vm  Va  baseKV  zone  Vmax  Vmin
mpc.bus = [
  1  3  0.0000  0.0000  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
  2  1  0.0000  0.0000  0.0000  1.2000  1  1  0  12.5  1  1.1  0.9
  3  1  0.0000  0.0000  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
  4  1  0.2000  0.1200  0.0000  1.0500  1  1  0  12.5  1  1.1  0.9
  5  1  0.4000  0.2500  0.0000  0.6000  1  1  0  12.5  1  1.1  0.9
  6  1  1.5000  0.9300  0.0000  0.6000  1  1  0  12.5  1  1.1  0.9
  7  1  3.0000  2.2600  0.0000  1.8000  1  1  0  12.5  1  1.1  0.9
  8  1  0.8000  0.5000  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
  9  1  0.2000  0.1200  0.0000  0.6000  1  1  0  12.5  1  1.1  0.9
 10  1  1.0000  0.6200  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
 11  1  0.5000  0.3100  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
 12  1  1.0000  0.6200  0.0000  0.6000  1  1  0  12.5  1  1.1  0.9
 13  1  0.3000  0.1900  0.0000  1.2000  1  1  0  12.5  1  1.1  0.9
 14  1  0.2000  0.1200  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
 15  1  0.8000  0.5000  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
 16  1  0.5000  0.3100  0.0000  1.5000  1  1  0  12.5  1  1.1  0.9
 17  1  1.0000  0.6200  0.0000  0.9000  1  1  0  12.5  1  1.1  0.9
 18  1  0.2000  0.1200  0.0000  0.0000  1  1  0  12.5  1  1.1  0.9
];

%% generator data
% bus  Pg  Qg  Qmax  Qmin Vg  mBase  status  Pmax  Pmin  Pc1  Pc2  Qc1min  Qc1max  Qc2min  Qc2max  ramp_agc  ramp_10  ramp_30  ramp_q  apf
mpc.gen = [
  1  0.0000  0.0000  999  -999  1.0500  100  1   999  0  0  0  0  0  0  0  0  0  0  0  0
];

%% branch data
% fbus  tbus  r  x  b  rateA  rateB  rateC  ratio  angle  status  angmin  angmax
mpc.branch = [
   1   2  0.00004998  0.00035398  0.00000000  999  999  999  0  0  1  -360  360
   2   3  0.00031200  0.00675302  0.00000000  999  999  999  0  0  1  -360  360
   3   4  0.00043098  0.00120403  0.00035000  999  999  999  0  0  1  -360  360
   4   5  0.00060102  0.00167699  0.00049000  999  999  999  0  0  1  -360  360
   5   6  0.00031603  0.00088198  0.00026000  999  999  999  0  0  1  -360  360
   6   7  0.00089600  0.00250202  0.00073000  999  999  999  0  0  1  -360  360
   7   8  0.00029498  0.00082400  0.00024000  999  999  999  0  0  1  -360  360
   8   9  0.00172000  0.00212000  0.00046000  999  999  999  0  0  1  -360  360
   9  10  0.00407002  0.00305299  0.00051000  999  999  999  0  0  1  -360  360
   4  11  0.00170598  0.00220902  0.00043000  999  999  999  0  0  1  -360  360
   3  12  0.00291002  0.00376800  0.00074000  999  999  999  0  0  1  -360  360
  12  13  0.00222202  0.00287699  0.00056000  999  999  999  0  0  1  -360  360
  13  14  0.00480301  0.00621798  0.00122000  999  999  999  0  0  1  -360  360
  13  15  0.00398502  0.00516000  0.00101000  999  999  999  0  0  1  -360  360
  15  16  0.00291002  0.00376800  0.00074000  999  999  999  0  0  1  -360  360
  15  17  0.00372698  0.00459302  0.00100000  999  999  999  0  0  1  -360  360
  17  18  0.00110400  0.00136000  0.00118000  999  999  999  0  0  1  -360  360
];
