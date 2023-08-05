function mpc = case136ma
%CASE136MA  Power flow data for 135 bus distribution system from Mantovani, et al
%   Please see CASEFORMAT for details on the case file format.
%
%   Data from ...
%       Mantovani JRS, Casari F, Romero RA (2000) Reconfiguração de sistemas
%       de distribuição radiais utilizando o critério de queda de tensão. Rev
%       Bras Controle Automação - SBA 11:150-159.

%% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
%% system MVA base
mpc.baseMVA = 10;

%% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
mpc.bus = [ %% (Pd and Qd are specified in kW & kVAr here, converted to MW & MVAr below)
	1	3	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	2	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	3	1	47.78	19.01	0	0	1	1	0	13.8	1	1.05	0.95;
	4	1	42.55	16.93	0	0	1	1	0	13.8	1	1.05	0.95;
	5	1	87.02	34.62	0	0	1	1	0	13.8	1	1.05	0.95;
	6	1	311.31	123.855	0	0	1	1	0	13.8	1	1.05	0.95;
	7	1	148.869	59.23	0	0	1	1	0	13.8	1	1.05	0.95;
	8	1	238.672	94.96	0	0	1	1	0	13.8	1	1.05	0.95;
	9	1	62.3	24.79	0	0	1	1	0	13.8	1	1.05	0.95;
	10	1	124.598	49.57	0	0	1	1	0	13.8	1	1.05	0.95;
	11	1	140.175	55.77	0	0	1	1	0	13.8	1	1.05	0.95;
	12	1	116.813	46.47	0	0	1	1	0	13.8	1	1.05	0.95;
	13	1	249.203	99.15	0	0	1	1	0	13.8	1	1.05	0.95;
	14	1	291.447	115.952	0	0	1	1	0	13.8	1	1.05	0.95;
	15	1	303.72	120.835	0	0	1	1	0	13.8	1	1.05	0.95;
	16	1	215.396	85.7	0	0	1	1	0	13.8	1	1.05	0.95;
	17	1	198.586	79.01	0	0	1	1	0	13.8	1	1.05	0.95;
	18	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	19	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	20	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	21	1	30.13	14.73	0	0	1	1	0	13.8	1	1.05	0.95;
	22	1	230.972	112.92	0	0	1	1	0	13.8	1	1.05	0.95;
	23	1	60.26	29.46	0	0	1	1	0	13.8	1	1.05	0.95;
	24	1	230.972	112.92	0	0	1	1	0	13.8	1	1.05	0.95;
	25	1	120.507	58.92	0	0	1	1	0	13.8	1	1.05	0.95;
	26	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	27	1	56.98	27.86	0	0	1	1	0	13.8	1	1.05	0.95;
	28	1	364.665	178.281	0	0	1	1	0	13.8	1	1.05	0.95;
	29	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	30	1	124.647	60.94	0	0	1	1	0	13.8	1	1.05	0.95;
	31	1	56.98	27.86	0	0	1	1	0	13.8	1	1.05	0.95;
	32	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	33	1	85.47	41.79	0	0	1	1	0	13.8	1	1.05	0.95;
	34	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	35	1	396.735	193.96	0	0	1	1	0	13.8	1	1.05	0.95;
	36	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	37	1	181.152	88.56	0	0	1	1	0	13.8	1	1.05	0.95;
	38	1	242.172	118.395	0	0	1	1	0	13.8	1	1.05	0.95;
	39	1	75.32	36.82	0	0	1	1	0	13.8	1	1.05	0.95;
	40	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	41	1	1.25	0.53	0	0	1	1	0	13.8	1	1.05	0.95;
	42	1	6.27	2.66	0	0	1	1	0	13.8	1	1.05	0.95;
	43	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	44	1	117.88	49.97	0	0	1	1	0	13.8	1	1.05	0.95;
	45	1	62.67	26.57	0	0	1	1	0	13.8	1	1.05	0.95;
	46	1	172.285	73.03	0	0	1	1	0	13.8	1	1.05	0.95;
	47	1	458.556	194.388	0	0	1	1	0	13.8	1	1.05	0.95;
	48	1	262.962	111.473	0	0	1	1	0	13.8	1	1.05	0.95;
	49	1	235.761	99.94	0	0	1	1	0	13.8	1	1.05	0.95;
	50	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	51	1	109.215	46.3	0	0	1	1	0	13.8	1	1.05	0.95;
	52	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	53	1	72.81	30.87	0	0	1	1	0	13.8	1	1.05	0.95;
	54	1	258.473	109.57	0	0	1	1	0	13.8	1	1.05	0.95;
	55	1	69.17	29.32	0	0	1	1	0	13.8	1	1.05	0.95;
	56	1	21.84	9.26	0	0	1	1	0	13.8	1	1.05	0.95;
	57	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	58	1	20.53	8.7	0	0	1	1	0	13.8	1	1.05	0.95;
	59	1	150.548	63.82	0	0	1	1	0	13.8	1	1.05	0.95;
	60	1	220.687	93.55	0	0	1	1	0	13.8	1	1.05	0.95;
	61	1	92.38	39.16	0	0	1	1	0	13.8	1	1.05	0.95;
	62	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	63	1	226.693	96.1	0	0	1	1	0	13.8	1	1.05	0.95;
	64	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	65	1	294.016	116.974	0	0	1	1	0	13.8	1	1.05	0.95;
	66	1	83.02	33.03	0	0	1	1	0	13.8	1	1.05	0.95;
	67	1	83.02	33.03	0	0	1	1	0	13.8	1	1.05	0.95;
	68	1	103.77	41.29	0	0	1	1	0	13.8	1	1.05	0.95;
	69	1	176.408	70.18	0	0	1	1	0	13.8	1	1.05	0.95;
	70	1	83.02	33.03	0	0	1	1	0	13.8	1	1.05	0.95;
	71	1	217.917	86.7	0	0	1	1	0	13.8	1	1.05	0.95;
	72	1	23.29	9.27	0	0	1	1	0	13.8	1	1.05	0.95;
	73	1	5.08	2.02	0	0	1	1	0	13.8	1	1.05	0.95;
	74	1	72.64	28.9	0	0	1	1	0	13.8	1	1.05	0.95;
	75	1	405.99	161.523	0	0	1	1	0	13.8	1	1.05	0.95;
	76	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	77	1	100.182	42.47	0	0	1	1	0	13.8	1	1.05	0.95;
	78	1	142.523	60.42	0	0	1	1	0	13.8	1	1.05	0.95;
	79	1	96.04	40.71	0	0	1	1	0	13.8	1	1.05	0.95;
	80	1	300.454	127.366	0	0	1	1	0	13.8	1	1.05	0.95;
	81	1	141.238	59.87	0	0	1	1	0	13.8	1	1.05	0.95;
	82	1	279.847	118.631	0	0	1	1	0	13.8	1	1.05	0.95;
	83	1	87.31	37.01	0	0	1	1	0	13.8	1	1.05	0.95;
	84	1	243.849	103.371	0	0	1	1	0	13.8	1	1.05	0.95;
	85	1	247.75	105.025	0	0	1	1	0	13.8	1	1.05	0.95;
	86	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	87	1	89.88	38.1	0	0	1	1	0	13.8	1	1.05	0.95;
	88	1	1137.28	482.108	0	0	1	1	0	13.8	1	1.05	0.95;
	89	1	458.339	194.296	0	0	1	1	0	13.8	1	1.05	0.95;
	90	1	385.197	163.29	0	0	1	1	0	13.8	1	1.05	0.95;
	91	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	92	1	79.61	33.75	0	0	1	1	0	13.8	1	1.05	0.95;
	93	1	87.31	37.01	0	0	1	1	0	13.8	1	1.05	0.95;
	94	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	95	1	74	31.37	0	0	1	1	0	13.8	1	1.05	0.95;
	96	1	232.05	98.37	0	0	1	1	0	13.8	1	1.05	0.95;
	97	1	141.819	60.12	0	0	1	1	0	13.8	1	1.05	0.95;
	98	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	99	1	76.45	32.41	0	0	1	1	0	13.8	1	1.05	0.95;
	100	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	101	1	51.32	21.76	0	0	1	1	0	13.8	1	1.05	0.95;
	102	1	59.87	25.38	0	0	1	1	0	13.8	1	1.05	0.95;
	103	1	9.07	3.84	0	0	1	1	0	13.8	1	1.05	0.95;
	104	1	2.09	0.89	0	0	1	1	0	13.8	1	1.05	0.95;
	105	1	16.735	7.09	0	0	1	1	0	13.8	1	1.05	0.95;
	106	1	1506.522	638.634	0	0	1	1	0	13.8	1	1.05	0.95;
	107	1	313.023	132.694	0	0	1	1	0	13.8	1	1.05	0.95;
	108	1	79.83	33.84	0	0	1	1	0	13.8	1	1.05	0.95;
	109	1	51.32	21.76	0	0	1	1	0	13.8	1	1.05	0.95;
	110	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	111	1	202.435	85.82	0	0	1	1	0	13.8	1	1.05	0.95;
	112	1	60.82	25.78	0	0	1	1	0	13.8	1	1.05	0.95;
	113	1	45.62	19.34	0	0	1	1	0	13.8	1	1.05	0.95;
	114	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	115	1	157.07	66.58	0	0	1	1	0	13.8	1	1.05	0.95;
	116	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	117	1	250.148	106.041	0	0	1	1	0	13.8	1	1.05	0.95;
	118	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	119	1	69.81	29.59	0	0	1	1	0	13.8	1	1.05	0.95;
	120	1	32.07	13.6	0	0	1	1	0	13.8	1	1.05	0.95;
	121	1	61.08	25.89	0	0	1	1	0	13.8	1	1.05	0.95;
	122	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
	123	1	94.62	46.26	0	0	1	1	0	13.8	1	1.05	0.95;
	124	1	49.86	24.38	0	0	1	1	0	13.8	1	1.05	0.95;
	125	1	123.164	60.21	0	0	1	1	0	13.8	1	1.05	0.95;
	126	1	78.35	38.3	0	0	1	1	0	13.8	1	1.05	0.95;
	127	1	145.475	71.12	0	0	1	1	0	13.8	1	1.05	0.95;
	128	1	21.37	10.45	0	0	1	1	0	13.8	1	1.05	0.95;
	129	1	74.79	36.56	0	0	1	1	0	13.8	1	1.05	0.95;
	130	1	227.926	111.431	0	0	1	1	0	13.8	1	1.05	0.95;
	131	1	35.61	17.41	0	0	1	1	0	13.8	1	1.05	0.95;
	132	1	249.295	121.877	0	0	1	1	0	13.8	1	1.05	0.95;
	133	1	316.722	154.842	0	0	1	1	0	13.8	1	1.05	0.95;
	134	1	333.817	163.199	0	0	1	1	0	13.8	1	1.05	0.95;
	135	1	249.295	121.877	0	0	1	1	0	13.8	1	1.05	0.95;
	136	1	0	0	0	0	1	1	0	13.8	1	1.05	0.95;
];

%% generator data
%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf
mpc.gen = [
	1	0	0	10	-10	1	100	1	10	0	0	0	0	0	0	0	0	0	0	0	0;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax
mpc.branch = [  %% (r and x specified in ohms here, converted to p.u. below)
	1	2	0.33205	0.76653	0	100	100	100	0	0	1	-360	360;
	2	3	0.00188	0.00433	0	100	100	100	0	0	1	-360	360;
	3	4	0.22324	0.51535	0	100	100	100	0	0	1	-360	360;
	4	5	0.09943	0.22953	0	100	100	100	0	0	1	-360	360;
	5	6	0.15571	0.35945	0	100	100	100	0	0	1	-360	360;
	6	7	0.16321	0.37677	0	100	100	100	0	0	1	-360	360;
	7	8	0.11444	0.26417	0	100	100	100	0	0	1	-360	360;
	7	9	0.05675	0.05666	0	100	100	100	0	0	1	-360	360;
	9	10	0.52124	0.27418	0	100	100	100	0	0	1	-360	360;
	9	11	0.10877	0.10860	0	100	100	100	0	0	1	-360	360;
	11	12	0.39803	0.20937	0	100	100	100	0	0	1	-360	360;
	11	13	0.91744	0.31469	0	100	100	100	0	0	1	-360	360;
	11	14	0.11823	0.11805	0	100	100	100	0	0	1	-360	360;
	14	15	0.50228	0.26421	0	100	100	100	0	0	1	-360	360;
	14	16	0.05675	0.05666	0	100	100	100	0	0	1	-360	360;
	16	17	0.29379	0.15454	0	100	100	100	0	0	1	-360	360;
	1	18	0.33205	0.76653	0	100	100	100	0	0	1	-360	360;
	18	19	0.00188	0.00433	0	100	100	100	0	0	1	-360	360;
	19	20	0.22324	0.51535	0	100	100	100	0	0	1	-360	360;
	20	21	0.10881	0.25118	0	100	100	100	0	0	1	-360	360;
	21	22	0.71078	0.37388	0	100	100	100	0	0	1	-360	360;
	21	23	0.18197	0.42008	0	100	100	100	0	0	1	-360	360;
	23	24	0.30326	0.15952	0	100	100	100	0	0	1	-360	360;
	23	25	0.02439	0.05630	0	100	100	100	0	0	1	-360	360;
	25	26	0.04502	0.10394	0	100	100	100	0	0	1	-360	360;
	26	27	0.01876	0.04331	0	100	100	100	0	0	1	-360	360;
	27	28	0.11823	0.11805	0	100	100	100	0	0	1	-360	360;
	28	29	0.02365	0.02361	0	100	100	100	0	0	1	-360	360;
	29	30	0.18954	0.09970	0	100	100	100	0	0	1	-360	360;
	30	31	0.39803	0.20937	0	100	100	100	0	0	1	-360	360;
	29	32	0.05675	0.05666	0	100	100	100	0	0	1	-360	360;
	32	33	0.09477	0.04985	0	100	100	100	0	0	1	-360	360;
	33	34	0.41699	0.21934	0	100	100	100	0	0	1	-360	360;
	34	35	0.11372	0.05982	0	100	100	100	0	0	1	-360	360;
	32	36	0.07566	0.07555	0	100	100	100	0	0	1	-360	360;
	36	37	0.36960	0.19442	0	100	100	100	0	0	1	-360	360;
	37	38	0.26536	0.13958	0	100	100	100	0	0	1	-360	360;
	36	39	0.05675	0.05666	0	100	100	100	0	0	1	-360	360;
	1	40	0.33205	0.76653	0	100	100	100	0	0	1	-360	360;
	40	41	0.11819	0.27283	0	100	100	100	0	0	1	-360	360;
	41	42	2.96288	1.01628	0	100	100	100	0	0	1	-360	360;
	41	43	0.00188	0.00433	0	100	100	100	0	0	1	-360	360;
	43	44	0.06941	0.16024	0	100	100	100	0	0	1	-360	360;
	44	45	0.81502	0.42872	0	100	100	100	0	0	1	-360	360;
	44	46	0.06378	0.14724	0	100	100	100	0	0	1	-360	360;
	46	47	0.13132	0.30315	0	100	100	100	0	0	1	-360	360;
	47	48	0.06191	0.14291	0	100	100	100	0	0	1	-360	360;
	48	49	0.11444	0.26417	0	100	100	100	0	0	1	-360	360;
	49	50	0.28374	0.28331	0	100	100	100	0	0	1	-360	360;
	50	51	0.28374	0.28331	0	100	100	100	0	0	1	-360	360;
	49	52	0.04502	0.10394	0	100	100	100	0	0	1	-360	360;
	52	53	0.02626	0.06063	0	100	100	100	0	0	1	-360	360;
	53	54	0.06003	0.13858	0	100	100	100	0	0	1	-360	360;
	54	55	0.03002	0.06929	0	100	100	100	0	0	1	-360	360;
	55	56	0.02064	0.04764	0	100	100	100	0	0	1	-360	360;
	53	57	0.10881	0.25118	0	100	100	100	0	0	1	-360	360;
	57	58	0.25588	0.13460	0	100	100	100	0	0	1	-360	360;
	58	59	0.41699	0.21934	0	100	100	100	0	0	1	-360	360;
	59	60	0.50228	0.26421	0	100	100	100	0	0	1	-360	360;
	60	61	0.33170	0.17448	0	100	100	100	0	0	1	-360	360;
	61	62	0.20849	0.10967	0	100	100	100	0	0	1	-360	360;
	48	63	0.13882	0.32047	0	100	100	100	0	0	1	-360	360;
	1	64	0.00750	0.01732	0	100	100	100	0	0	1	-360	360;
	64	65	0.27014	0.62362	0	100	100	100	0	0	1	-360	360;
	65	66	0.38270	0.88346	0	100	100	100	0	0	1	-360	360;
	66	67	0.33018	0.76220	0	100	100	100	0	0	1	-360	360;
	67	68	0.32830	0.75787	0	100	100	100	0	0	1	-360	360;
	68	69	0.17072	0.39409	0	100	100	100	0	0	1	-360	360;
	69	70	0.55914	0.29412	0	100	100	100	0	0	1	-360	360;
	69	71	0.05816	0.13425	0	100	100	100	0	0	1	-360	360;
	71	72	0.70130	0.36890	0	100	100	100	0	0	1	-360	360;
	72	73	1.02352	0.53839	0	100	100	100	0	0	1	-360	360;
	71	74	0.06754	0.15591	0	100	100	100	0	0	1	-360	360;
	74	75	1.32352	0.45397	0	100	100	100	0	0	1	-360	360;
	1	76	0.01126	0.02598	0	100	100	100	0	0	1	-360	360;
	76	77	0.72976	1.68464	0	100	100	100	0	0	1	-360	360;
	77	78	0.22512	0.51968	0	100	100	100	0	0	1	-360	360;
	78	79	0.20824	0.48071	0	100	100	100	0	0	1	-360	360;
	79	80	0.04690	0.10827	0	100	100	100	0	0	1	-360	360;
	80	81	0.61950	0.61857	0	100	100	100	0	0	1	-360	360;
	81	82	0.34049	0.33998	0	100	100	100	0	0	1	-360	360;
	82	83	0.56862	0.29911	0	100	100	100	0	0	1	-360	360;
	82	84	0.10877	0.10860	0	100	100	100	0	0	1	-360	360;
	84	85	0.56862	0.29911	0	100	100	100	0	0	1	-360	360;
	1	86	0.01126	0.02598	0	100	100	100	0	0	1	-360	360;
	86	87	0.41835	0.96575	0	100	100	100	0	0	1	-360	360;
	87	88	0.10499	0.13641	0	100	100	100	0	0	1	-360	360;
	87	89	0.43898	1.01338	0	100	100	100	0	0	1	-360	360;
	89	90	0.07520	0.02579	0	100	100	100	0	0	1	-360	360;
	90	91	0.07692	0.17756	0	100	100	100	0	0	1	-360	360;
	91	92	0.33205	0.76653	0	100	100	100	0	0	1	-360	360;
	92	93	0.08442	0.19488	0	100	100	100	0	0	1	-360	360;
	93	94	0.13320	0.30748	0	100	100	100	0	0	1	-360	360;
	94	95	0.29320	0.29276	0	100	100	100	0	0	1	-360	360;
	95	96	0.21753	0.21721	0	100	100	100	0	0	1	-360	360;
	96	97	0.26482	0.26443	0	100	100	100	0	0	1	-360	360;
	94	98	0.10318	0.23819	0	100	100	100	0	0	1	-360	360;
	98	99	0.13507	0.31181	0	100	100	100	0	0	1	-360	360;
	1	100	0.00938	0.02165	0	100	100	100	0	0	1	-360	360;
	100	101	0.16884	0.38976	0	100	100	100	0	0	1	-360	360;
	101	102	0.11819	0.27283	0	100	100	100	0	0	1	-360	360;
	102	103	2.28608	0.78414	0	100	100	100	0	0	1	-360	360;
	102	104	0.45587	1.05236	0	100	100	100	0	0	1	-360	360;
	104	105	0.69600	1.60669	0	100	100	100	0	0	1	-360	360;
	105	106	0.45774	1.05669	0	100	100	100	0	0	1	-360	360;
	106	107	0.20298	0.26373	0	100	100	100	0	0	1	-360	360;
	107	108	0.21348	0.27737	0	100	100	100	0	0	1	-360	360;
	108	109	0.54967	0.28914	0	100	100	100	0	0	1	-360	360;
	109	110	0.54019	0.28415	0	100	100	100	0	0	1	-360	360;
	108	111	0.04550	0.05911	0	100	100	100	0	0	1	-360	360;
	111	112	0.47385	0.24926	0	100	100	100	0	0	1	-360	360;
	112	113	0.86241	0.45364	0	100	100	100	0	0	1	-360	360;
	113	114	0.56862	0.29911	0	100	100	100	0	0	1	-360	360;
	109	115	0.77711	0.40878	0	100	100	100	0	0	1	-360	360;
	115	116	1.08038	0.56830	0	100	100	100	0	0	1	-360	360;
	110	117	1.09933	0.57827	0	100	100	100	0	0	1	-360	360;
	117	118	0.47385	0.24926	0	100	100	100	0	0	1	-360	360;
	105	119	0.32267	0.74488	0	100	100	100	0	0	1	-360	360;
	119	120	0.14633	0.33779	0	100	100	100	0	0	1	-360	360;
	120	121	0.12382	0.28583	0	100	100	100	0	0	1	-360	360;
	1	122	0.01126	0.02598	0	100	100	100	0	0	1	-360	360;
	122	123	0.64910	1.49842	0	100	100	100	0	0	1	-360	360;
	123	124	0.04502	0.10394	0	100	100	100	0	0	1	-360	360;
	124	125	0.52640	0.18056	0	100	100	100	0	0	1	-360	360;
	124	126	0.02064	0.04764	0	100	100	100	0	0	1	-360	360;
	126	127	0.53071	0.27917	0	100	100	100	0	0	1	-360	360;
	126	128	0.09755	0.22520	0	100	100	100	0	0	1	-360	360;
	128	129	0.11819	0.27283	0	100	100	100	0	0	1	-360	360;
	128	130	0.13882	0.32047	0	100	100	100	0	0	1	-360	360;
	130	131	0.04315	0.09961	0	100	100	100	0	0	1	-360	360;
	131	132	0.09192	0.21220	0	100	100	100	0	0	1	-360	360;
	132	133	0.16134	0.37244	0	100	100	100	0	0	1	-360	360;
	133	134	0.37832	0.37775	0	100	100	100	0	0	1	-360	360;
	134	135	0.39724	0.39664	0	100	100	100	0	0	1	-360	360;
	135	136	0.29320	0.29276	0	100	100	100	0	0	1	-360	360;
	8	74	0.13132	0.30315	0	100	100	100	0	0	0	-360	360;
	10	25	0.26536	0.13958	0	100	100	100	0	0	0	-360	360;
	16	84	0.14187	0.14166	0	100	100	100	0	0	0	-360	360;
	39	136	0.08512	0.08499	0	100	100	100	0	0	0	-360	360;
	26	52	0.04502	0.10394	0	100	100	100	0	0	0	-360	360;
	51	97	0.14187	0.14166	0	100	100	100	0	0	0	-360	360;
	56	99	0.14187	0.14166	0	100	100	100	0	0	0	-360	360;
	63	121	0.03940	0.09094	0	100	100	100	0	0	0	-360	360;
	67	80	0.12944	0.29882	0	100	100	100	0	0	0	-360	360;
	80	132	0.01688	0.03898	0	100	100	100	0	0	0	-360	360;
	85	136	0.33170	0.17448	0	100	100	100	0	0	0	-360	360;
	92	105	0.14187	0.14166	0	100	100	100	0	0	0	-360	360;
	91	130	0.07692	0.17756	0	100	100	100	0	0	0	-360	360;
	91	104	0.07692	0.17756	0	100	100	100	0	0	0	-360	360;
	93	105	0.07692	0.17756	0	100	100	100	0	0	0	-360	360;
	93	133	0.07692	0.17756	0	100	100	100	0	0	0	-360	360;
	97	121	0.26482	0.26443	0	100	100	100	0	0	0	-360	360;
	111	48	0.49696	0.64567	0	100	100	100	0	0	0	-360	360;
	127	77	0.17059	0.08973	0	100	100	100	0	0	0	-360	360;
	129	78	0.05253	0.12126	0	100	100	100	0	0	0	-360	360;
	136	99	0.29320	0.29276	0	100	100	100	0	0	0	-360	360;
];

%%-----  OPF Data  -----%%
%% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
mpc.gencost = [
	2	0	0	3	0	20	0;
];


%% convert branch impedances from Ohms to p.u.
[PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, ...
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN] = idx_bus;
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, ...
    TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ...
    ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX] = idx_brch;
Vbase = mpc.bus(1, BASE_KV) * 1e3;      %% in Volts
Sbase = mpc.baseMVA * 1e6;              %% in VA
mpc.branch(:, [BR_R BR_X]) = mpc.branch(:, [BR_R BR_X]) / (Vbase^2 / Sbase);

%% convert loads from kW to MW
mpc.bus(:, [PD, QD]) = mpc.bus(:, [PD, QD]) / 1e3;
