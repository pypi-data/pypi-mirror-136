function mpc = t_case30_userfcns
%T_CASE30_USERFCNS  Power flow data for 30 bus, 6 gen case w/reserves & iflims
%   Please see CASEFORMAT for details on the case file format.
%
%   Same as case30.m, but with fixed reserve and interface flow limit data.
%   The reserve data is defined in the fields of mpc.reserves and the
%   interface flow limit data in mpc.if at the bottom of the file.

%   MATPOWER

%% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
%% system MVA base
mpc.baseMVA = 100;

%% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
mpc.bus = [
	1	3	0	0	0	0	1	1	0	135	1	1.05	0.95;
	2	2	21.7	12.7	0	0	1	1	0	135	1	1.1	0.95;
	300	1	2.4	1.2	0	0	1	1	0	135	1	1.05	0.95;
	4	1	7.6	1.6	0	0	1	1	0	135	1	1.05	0.95;
	5	1	0	0	0	0.19	1	1	0	135	1	1.05	0.95;
	6	1	0	0	0	0	1	1	0	135	1	1.05	0.95;
	7	1	22.8	10.9	0	0	1	1	0	135	1	1.05	0.95;
	8	1	30	30	0	0	1	1	0	135	1	1.05	0.95;
	9	1	0	0	0	0	1	1	0	135	1	1.05	0.95;
	10	1	5.8	2	0	0	3	1	0	135	1	1.05	0.95;
	11	1	0	0	0	0	1	1	0	135	1	1.05	0.95;
	12	1	11.2	7.5	0	0	2	1	0	135	1	1.05	0.95;
	13	2	0	0	0	0	2	1	0	135	1	1.1	0.95;
	14	1	6.2	1.6	0	0	2	1	0	135	1	1.05	0.95;
	15	1	8.2	2.5	0	0	2	1	0	135	1	1.05	0.95;
	16	1	3.5	1.8	0	0	2	1	0	135	1	1.05	0.95;
	17	1	9	5.8	0	0	2	1	0	135	1	1.05	0.95;
	18	1	3.2	0.9	0	0	2	1	0	135	1	1.05	0.95;
	19	1	9.5	3.4	0	0	2	1	0	135	1	1.05	0.95;
	20	1	2.2	0.7	0	0	2	1	0	135	1	1.05	0.95;
	21	1	17.5	11.2	0	0	3	1	0	135	1	1.05	0.95;
	22	2	0	0	0	0	3	1	0	135	1	1.1	0.95;
	23	2	3.2	1.6	0	0	2	1	0	135	1	1.1	0.95;
	24	1	8.7	6.7	0	0.04	3	1	0	135	1	1.05	0.95;
	25	1	0	0	0	0	3	1	0	135	1	1.05	0.95;
	26	1	3.5	2.3	0	0	3	1	0	135	1	1.05	0.95;
	27	2	0	0	0	0	3	1	0	135	1	1.1	0.95;
	28	1	0	0	0	0	1	1	0	135	1	1.05	0.95;
	29	1	2.4	0.9	0	0	3	1	0	135	1	1.05	0.95;
	30	1	10.6	1.9	0	0	3	1	0	135	1	1.05	0.95;
];

%% generator data
%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
mpc.gen = [
	1	23.54	0	150	-20	1	100	1	80	0	0	0	0	0	0	0	0	0	0	0	0;
	2	60.97	0	60	-20	1	100	1	80	0	0	0	0	0	0	0	0	0	0	0	0;
	22	21.59	0	62.5	-15	1	100	1	50	0	0	0	0	0	0	0	0	0	0	0	0;
	27	26.91	0	48.7	-15	1	100	1	55	0	0	0	0	0	0	0	0	0	0	0	0;
	23	19.2	0	40	-10	1	100	1	30	0	0	0	0	0	0	0	0	0	0	0	0;
	13	37	0	44.7	-15	1	100	1	40	0	0	0	0	0	0	0	0	0	0	0	0;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax
mpc.branch = [
	1	2	0.02	0.06	0.03	130	130	130	0	0	1	-360	360;
	1	300	0.05	0.19	0.02	130	130	130	0	0	1	-360	360;
	2	4	0.06	0.17	0.02	65	65	65	0	0	1	-360	360;
	300	4	0.01	0.04	0	130	130	130	0	0	1	-360	360;
	2	5	0.05	0.2	0.02	130	130	130	0	0	1	-360	360;
	2	6	0.06	0.18	0.02	65	65	65	0	0	1	-360	360;
	4	6	0.01	0.04	0	90	90	90	0	0	1	-360	360;
	5	7	0.05	0.12	0.01	70	70	70	0	0	1	-360	360;
	6	7	0.03	0.08	0.01	130	130	130	0	0	1	-360	360;
	6	8	0.01	0.04	0	32	32	32	0	0	1	-360	360;
	6	9	0	0.21	0	65	65	65	0	0	1	-360	360;
	6	10	0	0.56	0	32	32	32	0	0	1	-360	360;
	9	11	0	0.21	0	65	65	65	0	0	1	-360	360;
	9	10	0	0.11	0	65	65	65	0	0	1	-360	360;
	4	12	0	0.26	0	65	65	65	0	0	1	-360	360;
	12	13	0	0.14	0	65	65	65	0	0	1	-360	360;
	12	14	0.12	0.26	0	32	32	32	0	0	1	-360	360;
	12	15	0.07	0.13	0	32	32	32	0	0	1	-360	360;
	12	16	0.09	0.2	0	32	32	32	0	0	1	-360	360;
	14	15	0.22	0.2	0	16	16	16	0	0	1	-360	360;
	16	17	0.08	0.19	0	16	16	16	0	0	1	-360	360;
	15	18	0.11	0.22	0	16	16	16	0	0	1	-360	360;
	18	19	0.06	0.13	0	16	16	16	0	0	1	-360	360;
	19	20	0.03	0.07	0	32	32	32	0	0	1	-360	360;
	10	20	0.09	0.21	0	32	32	32	0	0	1	-360	360;
	10	17	0.03	0.08	0	32	32	32	0	0	1	-360	360;
	10	21	0.03	0.07	0	32	32	32	0	0	1	-360	360;
	10	22	0.07	0.15	0	32	32	32	0	0	1	-360	360;
	21	22	0.01	0.02	0	32	32	32	0	0	1	-360	360;
	15	23	0.1	0.2	0	16	16	16	0	0	1	-360	360;
	22	24	0.12	0.18	0	16	16	16	0	0	1	-360	360;
	23	24	0.13	0.27	0	16	16	16	0	0	1	-360	360;
	24	25	0.19	0.33	0	16	16	16	0	0	1	-360	360;
	25	26	0.25	0.38	0	16	16	16	0	0	1	-360	360;
	25	27	0.11	0.21	0	16	16	16	0	0	1	-360	360;
	28	27	0	0.4	0	65	65	65	0	0	1	-360	360;
	27	29	0.22	0.42	0	16	16	16	0	0	1	-360	360;
	27	30	0.32	0.6	0	16	16	16	0	0	1	-360	360;
	29	30	0.24	0.45	0	16	16	16	0	0	1	-360	360;
	8	28	0.06	0.2	0.02	32	32	32	0	0	1	-360	360;
	6	28	0.02	0.06	0.01	32	32	32	0	0	1	-360	360;
];

%%-----  OPF Data  -----%%
%% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
mpc.gencost = [
	2	0	0	3	0.02	2	0;
	2	0	0	3	0.0175	1.75	0;
	2	0	0	3	0.0625	1	0;
	2	0	0	3	0.00834	3.25	0;
	2	0	0	3	0.025	3	0;
	2	0	0	3	0.025	3	0;
];

%%-----  Reserve Data  -----%%
%% reserve zones, element i, j is 1 if gen j is in zone i, 0 otherwise
mpc.reserves.zones = [
	1	1	1	1	1	1;
	0	0	0	0	1	1
];

%% reserve requirements for each zone in MW
mpc.reserves.req   = [60; 20];

%% reserve costs in $/MW for each gen that belongs to at least 1 zone
%% (same order as gens, but skipping any gen that does not belong to any zone)
mpc.reserves.cost  = [	1.9;	2;	3;	4;	5;	5.5	];
%mpc.reserves.cost  = [	6;	5;	4;	3;	2;	1	];

%% OPTIONAL max reserve quantities for each gen that belongs to at least 1 zone
%% (same order as gens, but skipping any gen that does not belong to any zone)
mpc.reserves.qty   = [	25;	25;	25;	25;	25;	25	];

%%-----  Interface Flow Limit Data  -----%%
%	ifnum	branchidx (negative defines opposite direction)
mpc.if.map = [
	1	-12;	%% 1 : area 1 imports
	1	-14;
	1	-15;
	1	-36;
	2	15;	%% 2 : area 2 imports
	2	25;
	2	26;
	2	-32;
	3	12;	%% 3 : area 3 imports
	3	14;
	3	-25;
	3	-26;
	3	32;
	3	36;
];

%% DC model flow limits in MW
%% (negative and positive directions can be different)
%	ifnum	lower	upper
mpc.if.lims = [
	1	-15	25;	%% area 1 imports
	2	-10	20;	%% area 2 imports
];
