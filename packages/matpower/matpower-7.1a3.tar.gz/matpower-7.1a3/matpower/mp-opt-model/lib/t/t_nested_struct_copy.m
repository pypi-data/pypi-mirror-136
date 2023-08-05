function t_nested_struct_copy(quiet)
%T_NESTED_STUCT_COPY  Tests for NESTED_STUCT_COPY.

%   MP-Opt-Model
%   Copyright (c) 2013-2020, Power Systems Engineering Research Center (PSERC)
%   by Ray Zimmerman, PSERC Cornell
%
%   This file is part of MP-Opt-Model.
%   Covered by the 3-clause BSD License (see LICENSE file for details).
%   See https://github.com/MATPOWER/mp-opt-model for more info.

if nargin < 1
    quiet = 0;
end

t_begin(11, quiet);

%% set up some structs
D = struct( ...
    'a', 1, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'bye'));

S = struct( ...
    'a', 10, ...
    'b', struct(...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'g', 'chau', ...
        'h', 'oops'), ...
    'u', struct( ...
        'v', -1, ...
        'w', -2) );

%% default
t = 'DS = nested_struct_copy(D, S)';
DS = nested_struct_copy(D, S);
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4, ...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau', ...
        'h', 'oops'), ...
    'u', struct( ...
        'v', -1, ...
        'w', -2 ) );
t_ok(isequal(DS, E), t);

t = 'check = 0';
opt = struct('check', 0);
DS = nested_struct_copy(D, S, opt);
t_ok(isequal(DS, E), t);

t = 'check = -1';
opt = struct('check', -1);
DS = nested_struct_copy(D, S, opt);
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau'));
t_ok(isequal(DS, E), t);

t = 'check = 1 ==> error';
opt = struct('check', 1);
% if have_feature('catchme')
%     try
%         DS = nested_struct_copy(D, S, opt);
%         t_ok(0, t);
%     catch me
%         TorF = strcmp(me.message, 'nested_struct_copy: ''b.x'' is not a valid field name');
%         t_ok(TorF, t);
%         if ~TorF
%             me
%         end
%     end
% else
    try
        DS = nested_struct_copy(D, S, opt);
        t_ok(0, t);
    catch
        me = lasterr;
        TorF = strfind(me, 'nested_struct_copy: ''b.x'' is not a valid field name');
        t_ok(TorF, t);
        if ~TorF
            me
        end
    end
% end

t = 'check = 1, copy_mode = ''=''';
S2 = rmfield(S, 'u');
opt = struct('check', 1, 'copy_mode', '=');
DS = nested_struct_copy(D, S2, opt);
t_ok(isequal(DS, S2), t);

t = 'exceptions = <''b'', ''=''>';
ex = struct('name', 'b', 'copy_mode', '=');
opt = struct('exceptions', ex);
DS = nested_struct_copy(D, S2, opt);
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau', ...
        'h', 'oops'));
t_ok(isequal(DS, E), t);

t = 'exceptions = <''b'', ''=''>, <''c'', ''=''>';
ex = struct('name', {'b', 'c'}, 'copy_mode', {'=', '='});
opt = struct('exceptions', ex);
DS = nested_struct_copy(D, S2, opt);
t_ok(isequal(DS, S2), t);

t = 'exceptions = <''b'', ''=''>, <''c.g'', @upper>';
ex = struct('name', {'b', 'c.g'}, 'copy_mode', {'=', @upper});
opt = struct('exceptions', ex);
DS = nested_struct_copy(D, S2, opt);
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'CHAU', ...
        'h', 'oops'));
t_ok(isequal(DS, E), t);

t = 'check = 1, exceptions = <''b'', ck=-1>, <''c'', ck=0>';
ex = struct('name', {'b', 'c'}, 'check', {-1,0});
opt = struct('check', 1, 'exceptions', ex);
DS = nested_struct_copy(D, S2, opt);
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau', ...
        'h', 'oops'));
t_ok(isequal(DS, E), t);


t = 'default, with struct overwriting non-struct field';
D2 = D;
D2.pi = pi;
S3 = S;
S3.pi = struct('apple', 'yes', 'mud', 'no');
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4, ...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau', ...
        'h', 'oops'), ...
    'pi', struct( ...
        'apple', 'yes', ...
        'mud', 'no'), ...
    'u', struct( ...
        'v', -1, ...
        'w', -2 ) );
DS = nested_struct_copy(D2, S3);
t_ok(isequal(DS, E), t);

t = 'default, with struct array field';
S3 = S;
S3.u(2).v = -3;
S3.u(2).w = -4;
E = struct( ...
    'a', 10, ...
    'b', struct( ...
        'd', [2;3], ...
        'e', 4, ...
        'x', 100, ...
        'y', 200), ...
    'c', struct( ...
        'f', {{'hello', 'world'}}, ...
        'g', 'chau', ...
        'h', 'oops'), ...
    'u', struct( ...
        'v', {-1, -3}, ...
        'w', {-2, -4} ) );
DS = nested_struct_copy(D, S3);
t_ok(isequal(DS, E), t);

% D2
% S3
% DS
% E

% DS
% DS.b
% DS.c
% 
% E
% E.b
% E.c

t_end;
