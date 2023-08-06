# -*- coding: utf-8 -*-
import itertools
import copy
import multiprocessing
import tempfile
import os
import shutil
import time

import numpy as np
from gurobipy import *
from joblib import Parallel, delayed

from .common import *

from .construct import *

solve_methods = ["lop","hillside"]

def solve(S_orig, c_orig = None, fix_x = {}, method="hillside",num_random_restarts=0,lazy=False,verbose=False,find_pair=False,cont=False,include_model=False):
    if method not in solve_methods:
        raise Exception(f"Method '{method}' not implemented")
    
    n = S_orig.shape[0]
    
    # Pass verbosity flag to Gurobi prior to any calls
    setParam( 'OutputFlag', verbose )
    
    temp_dir = tempfile.mkdtemp() # try to write this model to memory
    
    indices = list(range(n))
    
    if method == 'hillside':
        if c_orig is None:
            c_orig = C_count(S_orig)
        c_orig = c_orig.values
        
    orig_columns = S_orig.columns
    orig_index = S_orig.index
    S_orig = S_orig.values
    
    try:
        Pfirst = []
        Pfinal = []
        objs = []
        xs = []
        pair_Pfirst = []
        pair_Pfinal = []
        pair_objs = []
        pair_xs = []
        first_k = None
        for ix in range(num_random_restarts+1):
            if ix > 0:
                perm_inxs = np.random.permutation(range(S_orig.shape[0]))
                S = S_orig[perm_inxs,:][:,perm_inxs]
            else:
                perm_inxs = np.arange(n)
                S = copy.deepcopy(S_orig)
            #include_score = np.zeros(S.shape)
            #inxs_num = np.where(~np.isnan(S))
            #include_score[inxs_num] = 1
                
            if method == 'hillside':
                c = c_orig[perm_inxs,:][:,perm_inxs]
                    
            model_file = os.path.join(temp_dir,"model.mps")
            if os.path.isfile(model_file):
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
            else:
                AP = Model(method)

                x = {}

                for i in range(n-1):
                    for j in range(i+1,n):
                        if (i,j) in fix_x:
                            x[i,j] = fix_x[i,j]
                        elif cont == True:
                            x[i,j] = AP.addVar(lb=0,vtype="C",ub=1,name="x(%s,%s)"%(i,j)) #continuous
                        else:
                            x[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="x(%s,%s)"%(i,j)) #binary

                AP.update()
                ncons = 0
                for i in range(n):
                    for j in range(i+1,n):
                        for k in range(j+1,n):
                            trans_cons = []
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] <= 1))
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] >= 0))
                            ncons += 2
                            if lazy:
                                for cons in trans_cons:
                                    cons.setAttr(GRB.Attr.Lazy,1)
                                    
                AP.update()
                AP.write(model_file)
            if first_k is not None:
                if method == 'lop':
                    AP.addConstr(quicksum((S[i,j]-S[j,i])*x[i,j]+S[j,i] for i in range(n-1) for j in range(i+1,n)) == first_k)
                elif method == 'hillside':
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)) == first_k)

            tic = time.perf_counter()
            if method == 'lop':
                AP.setObjective(quicksum((S[i,j]-S[j,i])*x[i,j]+S[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
            elif method == 'hillside':
                AP.setObjective(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MINIMIZE)
            AP.update()
            toc = time.perf_counter()
            if verbose:
                print(f"Updating opjective in {toc - tic:0.4f} seconds")

            if verbose:
                print('Start optimization %d'%ix)
            tic = time.perf_counter()
            AP.params.Threads=7
            AP.update()
            if cont:
                AP.Params.Method = 2
                AP.Params.Crossover = 0    
                AP.update()
            AP.optimize()
            toc = time.perf_counter()
            if verbose:
                print(f"Optimization in {toc - tic:0.4f} seconds")
                print('End optimization %d'%ix)

            k=AP.objVal
            if first_k is None:
                first_k = k

            P = []
            sol_x = get_sol_x_by_x(x,n,cont=cont)()
            orig_sol_x = sol_x
            reorder = np.argsort(perm_inxs)
            sol_x = sol_x[np.ix_(reorder,reorder)]
            r = np.sum(sol_x,axis=0)
            ranking = np.argsort(r)
            P.append(tuple(ranking))
            xs.append(sol_x)

            if ix == 0:
                Pfirst = P
                xfirst = get_sol_x_by_x(x,n,cont=cont)()

            Pfinal.extend(P)
            if method == 'lop':
                objs.append(np.sum(S_orig*sol_x))
            elif method == 'hillside':
                objs.append(np.sum(c_orig*sol_x))
                
            if first_k is not None:
                if method == 'lop':
                    AP.addConstr(quicksum((S[i,j]-S[j,i])*x[i,j]+S[j,i] for i in range(n-1) for j in range(i+1,n)) == first_k)
                elif method == 'hillside':
                    AP.setObjective(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MINIMIZE)
            details = {"Pfirst": Pfirst, "P":Pfinal,"x": xfirst,"objs":objs,"xs":xs}
            
            # add the objective as a constraint for scip
            if method == 'lop':
                AP.addConstr(quicksum((S[i,j]-S[j,i])*x[i,j]+S[j,i] for i in range(n-1) for j in range(i+1,n)) == AP.objVal)
            elif method == 'hillside':
                AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)) == AP.objVal)
            details['model'] = AP

            if find_pair:
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
                if method == 'lop':
                    AP.addConstr(quicksum((S[i,j]-S[j,i])*x[i,j]+S[j,i] for i in range(n-1) for j in range(i+1,n))==first_k)
                elif method == 'hillside':
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n))==first_k)                
                AP.update()
                u={}
                v={}
                b={}
                for i in range(n-1):
                    for j in range(i+1,n):
                        u[i,j] = AP.addVar(name="u(%s,%s)"%(i,j),lb=0)
                        v[i,j] = AP.addVar(name="v(%s,%s)"%(i,j),lb=0)
                        b[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="b(%s,%s)"%(i,j))
                AP.update()
                for i in range(n-1):
                    for j in range(i+1,n):
                        AP.addConstr(u[i,j] - v[i,j] == x[i,j] - orig_sol_x[i,j])
                        AP.addConstr(u[i,j] <= b[i,j])
                        AP.addConstr(v[i,j] <= 1 - b[i,j])
                AP.update()

                AP.setObjective(quicksum(u[i,j]+v[i,j] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
                AP.setParam( 'OutputFlag', verbose )
                AP.update()

                if verbose:
                    print('Start pair optimization %d'%ix)
                tic = time.perf_counter()

                if cont:
                    AP.Params.Method = 2
                    AP.Params.Crossover = 0    
                    AP.update()

                AP.optimize()
                toc = time.perf_counter()
                if verbose:
                    print(f"Optimization in {toc - tic:0.4f} seconds")
                    print('End optimization %d'%ix)

                P = []
                sol_x = get_sol_x_by_x(x,n,cont=cont)()[np.ix_(reorder,reorder)]
                sol_u = get_sol_x_by_x(u,n)()[np.ix_(reorder,reorder)]
                sol_v = get_sol_x_by_x(v,n)()[np.ix_(reorder,reorder)]
                r = np.sum(sol_x,axis=0)
                ranking = np.argsort(r)
                P.append(tuple(ranking))
                pair_xs.append(sol_x)
                if method == 'lop':
                    k = np.sum(np.sum(S_orig*sol_x))
                elif method == 'hillside':
                    k = np.sum(np.sum(c_orig*sol_x))

                if ix == 0:
                    pair_Pfirst = P
                    pair_xfirst = get_sol_x_by_x(x,n)() 

                pair_Pfinal.extend(P)
                pair_objs.append(k)

        pair_details = None
        if find_pair:
            pair_details = {"Pfirst": pair_Pfirst, "P":pair_Pfinal,"x": pair_xfirst,"objs":pair_objs,"xs":pair_xs}
        details["pair_details"] = pair_details

        details['method'] = method
        details['indices'] = indices
        
    finally:
        shutil.rmtree(temp_dir)
        
    details['obj'] = k
    if method == 'hillside':
        details['c'] = c
        k = round(k)
    elif method == 'lop': # switch to delta
        perm = np.array(Pfirst[0])
        Dre = S_orig[perm,:][:,perm]
        #print(k,np.sum(np.triu(Dre)))
        k = np.sum(np.tril(Dre,k=-1))
    if not include_model:
        del details['model']
    return k,details

def solve_exhaustive_error(D_orig,max_error=0,min_error=0,method=["lop","hillside"][1],tol=1e-6):
    P = []
    k = None
    n = D_orig.shape[0]
    solutions = {}
    if method == 'hillside':
        obj_func= objective_hillside
    elif method == 'lop':
        obj_func = objective_lop

    for perm in itertools.permutations(range(n)):
        obj = round(obj_func(D_orig,perm)/tol)*tol
        if obj not in solutions:
            solutions[obj] = []
        solutions[obj].append(perm)
    
    details = {}
    details['P'] = []
    details['objs'] = []
    if method == 'hillside':
        all_k_values = np.array(list(solutions.keys()))
        k = np.min(all_k_values)
        for error in range(max_error - min_error + 1):
            if k+error in solutions:
                details['P'].extend(solutions[k+error])
                details['objs'].extend([k+error for i in range(len(solutions[k+error]))])
    elif method == 'lop':
        all_k_values = np.array(solutions.keys())
        k = np.max(all_k_values)
        for error in range(max_error - min_error + 1):
            if k-error in solutions:
                details['P'].extend(solutions[k-error])
                details['objs'].extend([k-error for i in range(len(solutions[k-error]))])
    return k,details

def objective_lop(Dorig,perm):
    D = Dorig[np.ix_(perm,perm)]
    return np.sum(np.sum(np.triu(D)))

def objective_hillside(Dorig,perm):
    D = Dorig[perm,:][:,perm]
    score = 0
    for i in range(D.shape[0]):
        for j in range(D.shape[0]):
            score += np.count_nonzero(D[i,j]>D[i+1:,j])
            score += np.count_nonzero(D[i,j]<D[i,j+1:])
    return score

def solve_error2(D_orig,max_error=10,min_error=0,method=["lop","hillside"][1],num_random_restarts=0,lazy=False,verbose=False,find_pair=False,cont=False):
    models = {}
    if max_error > 0:
        opt_k,opt_details,opt_models = solve_error(D_orig,max_error=0,min_error=0,num_random_restarts=num_random_restarts,method=method,lazy=lazy,verbose=verbose,cont=False)
        models['zero_error_models'] = opt_models
    else:
        opt_k = None
                
    models["error_models"] = []
    models["pair_models"] = []
            
    n = D_orig.shape[0]
    
    try:
        temp_dir = tempfile.mkdtemp() # try to write this model to memory
    
        if method == 'hillside':
            c_orig = compute_C(D_orig)

        Pfirst = []
        Pfinal = []
        objs = []
        xs = []
        pair_Pfirst = []
        pair_Pfinal = []
        pair_objs = []
        pair_xs = []
        for ix in range(num_random_restarts+1):
            if ix > 0:
                perm_inxs = np.random.permutation(range(D_orig.shape[0]))
                D = D_orig[perm_inxs,:][:,perm_inxs]
            else:
                perm_inxs = np.arange(n)
                D = copy.deepcopy(D_orig)

            if method == 'hillside':
                c = compute_C(D)

            model_file = os.path.join(temp_dir,"model.mps")
            if os.path.isfile(model_file):
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
                error = AP.getVarByName("error")
            else:
                AP = Model(method)

                x = {}

                for i in range(n-1):
                    for j in range(i+1,n):
                        if cont == True:
                            x[i,j] = AP.addVar(lb=0,vtype="C",ub=1,name="x(%s,%s)"%(i,j)) #continuous
                        else:
                            x[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="x(%s,%s)"%(i,j)) #binary

                AP.update()
                for i in range(n):
                    for j in range(i+1,n):
                        for k in range(j+1,n):
                            trans_cons = []
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] <= 1))
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] >= 0))
                            if lazy:
                                for cons in trans_cons:
                                    cons.setAttr(GRB.Attr.Lazy,1)

                if max_error > 0:
                    print('Adding error varibles')
                    error_c = {}
                    for i in range(n):
                        for j in range(n):
                            if i == j:
                                continue
                            error_c[i,j] = AP.addVar(lb=0,vtype="I",name="error_c(%s,%s)"%(i,j))
                    for i in range(n):
                        for j in range(n):
                            if i == j:
                                continue
                            #if i > j:
                            #    AP.addConstr(c[i,j] + c[j,i] + error_c[i,j] + error_c[j,i] <= 2*(n-1)) # can't get above n as the max
                            AP.addConstr(error_c[i,j] <= c[i,j]-1) # can't get negative
                    AP.addConstr(quicksum(error_c[i,j] + error_c[j,i] for i in range(n-1) for j in range(i+1,n)) <= max_error)
                    AP.addConstr(quicksum(error_c[i,j] + error_c[j,i] for i in range(n-1) for j in range(i+1,n)) >= min_error)
                    #AP.addConstr(error <= max_error)
                    #AP.addConstr(error >= min_error)
                else:
                    error = 0                

                AP.update()
                AP.write(model_file)

            if opt_k is not None:
                if method == 'lop':
                    AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n)) == opt_k)
                elif method == 'hillside':
                    print('skipping this because of quadratic')
                    #if max_error > 0:
                    #    AP.addConstr(quicksum((c[i,j]+error_c[i,j]-(c[j,i]+error_c[j,i]))*x[i,j]+c[j,i]+error_c[j,i] for i in range(n-1) for j in range(i+1,n)) == opt_k)
                    #else:
                    #    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)) == opt_k)

            tic = time.perf_counter()
            if method == 'lop':
                AP.setObjective(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
            elif method == 'hillside':
                if max_error > 0:
                    print('here')
                    AP.setObjective(quicksum((c[i,j]-error_c[i,j]-(c[j,i]-error_c[j,i]))*x[i,j]+c[j,i]-error_c[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MINIMIZE)
                else:
                    AP.setObjective(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)))
            AP.setParam( 'OutputFlag', verbose )
            AP.update()
            toc = time.perf_counter()
            if verbose:
                print(f"Updating opjective in {toc - tic:0.4f} seconds")

            if verbose:
                print('Start optimization %d'%ix)
            tic = time.perf_counter()
            if cont:
                AP.Params.Method = 2
                AP.Params.Crossover = 0    
                AP.update()
            AP.optimize()

            toc = time.perf_counter()
            if verbose:
                print(f"Optimization in {toc - tic:0.4f} seconds")
                print('End optimization %d'%ix)

            k=AP.objVal
            if opt_k is None:
                opt_k = k
            # Add in this constraint for future SCIP use
            if method == 'lop':
                AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n))+error == opt_k)
            elif method == 'hillside':
                error = 0 # fix this
                AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n))-error == opt_k)

            models["error_models"].append(AP)

            P = []
            sol_x = get_sol_x_by_x(x,n,cont=cont)()
            orig_sol_x = sol_x
            reorder = np.argsort(perm_inxs)
            sol_x = sol_x[np.ix_(reorder,reorder)]
            r = np.sum(sol_x,axis=0)
            ranking = np.argsort(r)
            P.append(tuple(ranking))
            xs.append(sol_x)

            if ix == 0:
                Pfirst = P
                xfirst = get_sol_x_by_x(x,n,cont=cont)()

            Pfinal.extend(P)
            if method == 'lop':
                objs.append(np.sum(D_orig*sol_x))
            elif method == 'hillside':
                objs.append(np.sum(c_orig*sol_x))

            if find_pair:
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
                error = AP.getVarByName("error")
                if method == 'lop':
                    AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] + error for i in range(n-1) for j in range(i+1,n))==opt_k)
                elif method == 'hillside':
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] + error for i in range(n-1) for j in range(i+1,n))==opt_k)                
                AP.update()
                u={}
                v={}
                b={}
                for i in range(n-1):
                    for j in range(i+1,n):
                        u[i,j] = AP.addVar(name="u(%s,%s)"%(i,j),lb=0)
                        v[i,j] = AP.addVar(name="v(%s,%s)"%(i,j),lb=0)
                        b[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="b(%s,%s)"%(i,j))
                AP.update()
                for i in range(n-1):
                    for j in range(i+1,n):
                        AP.addConstr(u[i,j] - v[i,j] == x[i,j] - orig_sol_x[i,j])
                        AP.addConstr(u[i,j] <= b[i,j])
                        AP.addConstr(v[i,j] <= 1 - b[i,j])
                AP.update()

                AP.setObjective(quicksum(u[i,j]+v[i,j] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
                AP.setParam( 'OutputFlag', verbose )
                AP.update()

                if verbose:
                    print('Start pair optimization %d'%ix)
                tic = time.perf_counter()

                if cont:
                    AP.Params.Method = 2
                    AP.Params.Crossover = 0    
                    AP.update()

                AP.optimize()
                models["pair_models"].append(AP)
                toc = time.perf_counter()
                if verbose:
                    print(f"Optimization in {toc - tic:0.4f} seconds")
                    print('End optimization %d'%ix)

                P = []
                sol_x = get_sol_x_by_x(x,n,cont=cont)()[np.ix_(reorder,reorder)]
                sol_u = get_sol_x_by_x(u,n)()[np.ix_(reorder,reorder)]
                sol_v = get_sol_x_by_x(v,n)()[np.ix_(reorder,reorder)]
                r = np.sum(sol_x,axis=0)
                ranking = np.argsort(r)
                P.append(tuple(ranking))
                pair_xs.append(sol_x)
                if method == 'lop':
                    k = np.sum(np.sum(D_orig*sol_x))
                elif method == 'hillside':
                    k = np.sum(np.sum(c_orig*sol_x))

                if ix == 0:
                    pair_Pfirst = P
                    pair_xfirst = get_sol_x_by_x(x,n)() 

                pair_Pfinal.extend(P)
                pair_objs.append(k)

        details = {"Pfirst": Pfirst, "P":Pfinal,"x": xfirst,"objs":objs,"xs":xs}
        pair_details = None
        if find_pair:
            pair_details = {"Pfirst": pair_Pfirst, "P":pair_Pfinal,"x": pair_xfirst,"objs":pair_objs,"xs":pair_xs}
        details["pair_details"] = pair_details

        details['method'] = method

        if max_error > 0:
            details["zero_error_details"] = max_error
    
    finally:
        shutil.rmtree(temp_dir)
        
    return k,details,models

def solve_error(D_orig,max_error=10,min_error=0,method=["lop","hillside"][1],num_random_restarts=0,lazy=False,verbose=False,find_pair=False,cont=False):
    models = {}
    if max_error > 0:
        opt_k,opt_details,opt_models = solve_error(D_orig,max_error=0,min_error=0,num_random_restarts=num_random_restarts,method=method,lazy=lazy,verbose=verbose,cont=False)
        opt_tol = opt_models['error_models'][0].Params.OptimalityTol
        models['zero_error_models'] = opt_models
    else:
        opt_k = None
                
    models["error_models"] = []
    models["pair_models"] = []
            
    n = D_orig.shape[0]
    
    try:
        temp_dir = tempfile.mkdtemp() # try to write this model to memory
    
        if method == 'hillside':
            c_orig = compute_C(D_orig)

        Pfirst = []
        Pfinal = []
        objs = []
        xs = []
        pair_Pfirst = []
        pair_Pfinal = []
        pair_objs = []
        pair_xs = []
        for ix in range(num_random_restarts+1):
            if ix > 0:
                perm_inxs = np.random.permutation(range(D_orig.shape[0]))
                D = D_orig[perm_inxs,:][:,perm_inxs]
            else:
                perm_inxs = np.arange(n)
                D = copy.deepcopy(D_orig)

            if method == 'hillside':
                c = compute_C(D)

            model_file = os.path.join(temp_dir,"model.mps")
            if os.path.isfile(model_file):
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
                error = AP.getVarByName("error")
            else:
                AP = Model(method)

                x = {}

                for i in range(n-1):
                    for j in range(i+1,n):
                        if cont == True:
                            x[i,j] = AP.addVar(lb=0,vtype="C",ub=1,name="x(%s,%s)"%(i,j)) #continuous
                        else:
                            x[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="x(%s,%s)"%(i,j)) #binary

                AP.update()
                for i in range(n):
                    for j in range(i+1,n):
                        for k in range(j+1,n):
                            trans_cons = []
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] <= 1))
                            trans_cons.append(AP.addConstr(x[i,j] + x[j,k] - x[i,k] >= 0))
                            if lazy:
                                for cons in trans_cons:
                                    cons.setAttr(GRB.Attr.Lazy,1)

                if max_error > 0:
                    if max_error == min_error:
                        error = max_error
                        print('Fixing error to %f'%error)
                    else:
                        print('Adding error varible')
                        error = AP.addVar(lb=min_error,ub=max_error,vtype="I",name="error")
                        AP.addConstr(error >= min_error)
                        AP.addConstr(error <= max_error)
                else:
                    error = 0                

                AP.update()
                AP.write(model_file)

            if opt_k is not None:
                if method == 'lop':
                    AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n)) + error >= opt_k - opt_tol)
                elif method == 'hillside':
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)) >= opt_k + error)
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*(1-x[i,j])+c[j,i] for i in range(n-1) for j in range(i+1,n)) <= np.sum(np.sum(c)) - opt_k - error)

            tic = time.perf_counter()
            if method == 'lop':
                AP.setObjective(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
            elif method == 'hillside':
                if error != 0:
                    AP.setObjective(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
                else:
                    AP.setObjective(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n)),GRB.MINIMIZE)
            AP.setParam( 'OutputFlag', verbose )
            AP.update()
            toc = time.perf_counter()
            if verbose:
                print(f"Updating opjective in {toc - tic:0.4f} seconds")

            if verbose:
                print('Start optimization %d'%ix)
            tic = time.perf_counter()
            if cont:
                AP.Params.Method = 2
                AP.Params.Crossover = 0    
                AP.update()
            AP.optimize()

            toc = time.perf_counter()
            if verbose:
                print(f"Optimization in {toc - tic:0.4f} seconds")
                print('End optimization %d'%ix)

            k=AP.objVal
            if opt_k is None:
                opt_k = k
            # Add in this constraint for future SCIP use
            if method == 'lop':
                AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] for i in range(n-1) for j in range(i+1,n))+error == opt_k)
            elif method == 'hillside':
                AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] for i in range(n-1) for j in range(i+1,n))-error == opt_k)

            models["error_models"].append(AP)

            P = []
            sol_x = get_sol_x_by_x(x,n,cont=cont)()
            orig_sol_x = sol_x
            reorder = np.argsort(perm_inxs)
            sol_x = sol_x[np.ix_(reorder,reorder)]
            r = np.sum(sol_x,axis=0)
            ranking = np.argsort(r)
            P.append(tuple(ranking))
            xs.append(sol_x)

            if ix == 0:
                Pfirst = P
                xfirst = get_sol_x_by_x(x,n,cont=cont)()

            Pfinal.extend(P)
            if method == 'lop':
                objs.append(np.sum(D_orig*sol_x))
            elif method == 'hillside':
                objs.append(np.sum(c_orig*sol_x))

            if find_pair:
                AP = read(model_file)
                x = {}
                for i in range(n-1):
                    for j in range(i+1,n):
                        x[i,j] = AP.getVarByName("x(%s,%s)"%(i,j))
                error = AP.getVarByName("error")
                if method == 'lop':
                    AP.addConstr(quicksum((D[i,j]-D[j,i])*x[i,j]+D[j,i] + error for i in range(n-1) for j in range(i+1,n))==opt_k)
                elif method == 'hillside':
                    AP.addConstr(quicksum((c[i,j]-c[j,i])*x[i,j]+c[j,i] + error for i in range(n-1) for j in range(i+1,n))==opt_k)                
                AP.update()
                u={}
                v={}
                b={}
                for i in range(n-1):
                    for j in range(i+1,n):
                        u[i,j] = AP.addVar(name="u(%s,%s)"%(i,j),lb=0)
                        v[i,j] = AP.addVar(name="v(%s,%s)"%(i,j),lb=0)
                        b[i,j] = AP.addVar(lb=0,vtype=GRB.BINARY,ub=1,name="b(%s,%s)"%(i,j))
                AP.update()
                for i in range(n-1):
                    for j in range(i+1,n):
                        AP.addConstr(u[i,j] - v[i,j] == x[i,j] - orig_sol_x[i,j])
                        AP.addConstr(u[i,j] <= b[i,j])
                        AP.addConstr(v[i,j] <= 1 - b[i,j])
                AP.update()

                AP.setObjective(quicksum(u[i,j]+v[i,j] for i in range(n-1) for j in range(i+1,n)),GRB.MAXIMIZE)
                AP.setParam( 'OutputFlag', verbose )
                AP.update()

                if verbose:
                    print('Start pair optimization %d'%ix)
                tic = time.perf_counter()

                if cont:
                    AP.Params.Method = 2
                    AP.Params.Crossover = 0    
                    AP.update()

                AP.optimize()
                models["pair_models"].append(AP)
                toc = time.perf_counter()
                if verbose:
                    print(f"Optimization in {toc - tic:0.4f} seconds")
                    print('End optimization %d'%ix)

                P = []
                sol_x = get_sol_x_by_x(x,n,cont=cont)()[np.ix_(reorder,reorder)]
                sol_u = get_sol_x_by_x(u,n)()[np.ix_(reorder,reorder)]
                sol_v = get_sol_x_by_x(v,n)()[np.ix_(reorder,reorder)]
                r = np.sum(sol_x,axis=0)
                ranking = np.argsort(r)
                P.append(tuple(ranking))
                pair_xs.append(sol_x)
                if method == 'lop':
                    k = np.sum(np.sum(D_orig*sol_x))
                elif method == 'hillside':
                    k = np.sum(np.sum(c_orig*sol_x))

                if ix == 0:
                    pair_Pfirst = P
                    pair_xfirst = get_sol_x_by_x(x,n)() 

                pair_Pfinal.extend(P)
                pair_objs.append(k)

        details = {"Pfirst": Pfirst, "P":Pfinal,"x": xfirst,"objs":objs,"xs":xs}
        pair_details = None
        if find_pair:
            pair_details = {"Pfirst": pair_Pfirst, "P":pair_Pfinal,"x": pair_xfirst,"objs":pair_objs,"xs":pair_xs}
        details["pair_details"] = pair_details

        details['method'] = method

        if max_error > 0:
            details["zero_error_details"] = max_error
    
    finally:
        shutil.rmtree(temp_dir)
        
    return k,details,models




def lp(D,relaxation_method=None,level=2):
    n = D.shape[0]

    AP = Model('lop')
   
    AP.setParam('OutputFlag', False )

    x = {}
        
    for i in range(n):
        for j in range(n):
            x[i,j] = AP.addVar(lb=0,vtype="C",ub=1,name="x(%s,%s)"%(i,j)) #continuous
                                  
    AP.update()

    for i in range(n):
        for j in range(n):
            if j!=i:
                AP.addConstr(x[i,j] + x[j,i] == 1)
    AP._x = x
    AP._constraints = []
   
    AP.update()
    AP.setObjective(quicksum(D[i,j]*x[i,j] for i in range(n) for j in range(n)),GRB.MAXIMIZE)
    AP.update()
       
    I = []
    values = set()
    for i,j in x.keys():
        values.add(i)
        values.add(j)
    for i in values:#range(n):
        for j in values:#range(n):
            for k in values:#range(n):
                if j != i and k != j and k != i:
                    idx = (i,j,k)
                    if relaxation_method == "constraints":
                        if (idx[0],idx[1]) in x and (idx[1],idx[2]) in x and (idx[2],idx[0]) in x:
                            AP.addConstr(AP._x[idx[0],idx[1]] + AP._x[idx[1],idx[2]] + AP._x[idx[2],idx[0]] <= 2).setAttr(GRB.Attr.Lazy,level)
                    else:
                        AP.addConstr(AP._x[idx[0],idx[1]] + AP._x[idx[1],idx[2]] + AP._x[idx[2],idx[0]] <= 2)

    AP.Params.Method = 2
    AP.Params.Crossover = 0    
    AP.update()
    AP.optimize()
        
    def get_sol_x_by_x(x,n):
        def myfunc():
            values = []
            for i in range(n):
                for j in range(n):
                    values.append(x[i,j].X)
            return np.reshape(values,(n,n))
        return myfunc
    k=AP.objVal
    details = {"P":[],"x": get_sol_x_by_x(x,n)()}
        
    return k,details

"""
Code below here needs checking out more so
"""

def generate_perms(perm_iters):
    if len(perm_iters) == 0:
        return [[]]
    rem_perms = generate_perms(perm_iters[1:])
    perms = []
    offset = perm_iters[0][0]
    for perm in perm_iters[0][1]:
        for rem_perm in rem_perms:
            new_perm = list(np.array(perm)+offset)+rem_perm
            if len(new_perm) > 0:
                perms.append(new_perm)
    return perms

def find_P_from_x(D,k,details,lower_cut=1e-3,upper_cut=1-1e-3):
    n = details['x'].shape[0]
    r = np.sum(details['x'],axis=1)
    ixs = np.argsort(-1*r)
    Xstar = details['x'][np.ix_(ixs,ixs)]
    Xstar = threshold_x(Xstar,lower_cut=lower_cut,upper_cut=upper_cut)
    Dordered = D[np.ix_(ixs,ixs)]
    Xstar[range(n),range(n)] = 0
    # for loop to look for binary cross and then try to extend it
    n = Xstar.shape[0]
    fixed_positions = np.zeros((n,)).astype(bool)
    fixed_positions[0] = np.array_equal(np.zeros(n-1,),Xstar[1:,0])
    fixed_positions[-1] = np.array_equal(np.ones(n-1,),Xstar[:-1,-1])
    for i in range(1,n-1):
        fixed_positions[i] = np.array_equal(np.ones(i,),Xstar[:i,i]) and np.array_equal(np.zeros(n-i-1,),Xstar[np.arange(i+1,n),i])
    # construct groups
    groups = []
    is_variable = []
    start_var = False
    group = []
    if fixed_positions[0] == False:
        start_var = True
    group.append(0)
    for i in range(1,n):
        # check to see if this is a change and we need to save the results
        if fixed_positions[i] == True and start_var:
            groups.append(group)
            is_variable.append(True)
            group = []
            start_var = False
        elif fixed_positions[i] == False and not start_var:
            groups.append(group)
            is_variable.append(False)
            group = []
            start_var = True
        group.append(i)

    if len(group) > 0:
        if start_var:
            is_variable.append(True)
        else:
            is_variable.append(False)
        groups.append(group)
        
    new_k,new_details = lp(Dordered,relaxation_method='constraints')
    perm_iters = []
    for i,group in enumerate(groups):
        if is_variable[i] == False:
            perm_iters.append((0,[group]))
        else:
            Xsub = np.round(new_details['x'])
            Xsub[np.ix_(group,group)] = Xstar[np.ix_(group,group)]
            obj_sub, permutations_sub = objective_count(Dordered,Dordered[np.ix_(group,group)],Xsub,k,group)
            perm_iters.append((group[0],permutations_sub))
    permutations = generate_perms(perm_iters)
    details["P"] = [list(np.array(ixs)[perm])[::-1] for perm in permutations]
    P = [tuple(entry) for entry in details['P']]
    details["P"] = list(set(P))
    new_P = []
    num_removed = 0
    for perm in details["P"]:
        obj = objective_count_perm(D,perm[::-1])
        if compare_objective_values(obj,k): # or (k == 0 and obj == 0): #remove and figure out +1
            new_P.append(list(perm))
        else:
            num_removed += 1
            continue
            #import pdb; pdb.set_trace()
            #print("Is this ever going to happen?")
    details["P"] = new_P
    details["Xstar_cut"] = Xstar
        
    info = {"Xstar":Xstar,"fixed_positions":fixed_positions,"groups":groups,"Dordered":Dordered,"ixs":ixs, "num_removed":num_removed}
    return new_P,info

def objective_count(Dordered,D,Xstar,min_value,group):
    frac_ixs = np.where((Xstar < 1) & (Xstar > 0))
    if len(frac_ixs[0]) == 0:
        return sum(sum(Xstar*Dordered)), [list(range(D.shape[0]))]
    new_rows = []
    new_cols = []
    for i in range(len(frac_ixs[0])):
        if frac_ixs[0][i] < frac_ixs[1][i]:
            new_rows.append(frac_ixs[0][i])
            new_cols.append(frac_ixs[1][i])
    frac_ixs = (np.array(new_rows),np.array(new_cols))
            
    cpu_count = multiprocessing.cpu_count()
    init_digits = int(np.log2(cpu_count))
    init_seqs = list(itertools.product([0.,1.], repeat=init_digits))
    if len(frac_ixs[0])-len(init_seqs) < 1:
        init_seqs = [[]]

    print("Going to loop for",2**len(frac_ixs[0])*1./len(init_seqs))

    def compute(init_seq,min_value=min_value,Xstar=Xstar):
        #min_value = np.Inf
        Xsub_min_value = []
        frac_ixs_min_value = []
        max_trials = np.Inf
        c = 0
        for rem_seq in itertools.product([0.,1.], repeat=len(frac_ixs[0])-len(init_seq)):
            seq = list(init_seq) + list(rem_seq)
            if c > max_trials:
                break
            c+=1
            Xsub = copy.copy(Xstar)
            Xsub[frac_ixs] = seq
            Xsub[(frac_ixs[1],frac_ixs[0])] = 1.-np.array(seq)
            obj = np.sum(np.sum(Xsub*Dordered))
            if compare_objective_values(obj,min_value):
                Xsub_min_value.append(Xsub)
                frac_ixs_min_value.append(frac_ixs)
        
        return min_value,Xsub_min_value,frac_ixs_min_value
    
    results = Parallel(n_jobs=cpu_count)(delayed(compute)(init_seq) for init_seq in init_seqs)
    # combine
    #min_value = np.Inf
    Xsub_min_value = []
    frac_ixs_min_value = []
    for result in results:
        if compare_objective_values(result[0],min_value):
            Xsub_min_value.extend(result[1])
            frac_ixs_min_value.extend(result[2])

    permutations = set()
    prev_n_permutations = 0
    for i,Xsub in enumerate(Xsub_min_value):
        r = np.sum(Xsub[np.ix_(group,group)],axis=1)
        ixs = np.argsort(-1*r,kind='stable')
        sets = {}
        for j,v in enumerate(r):
            if v not in sets:
                sets[v] = [j]
            else:
                sets[v].append(j)
        perm_iters = []
        last_v = None
        for ix in ixs:
            v = r[ix]
            if last_v is None or last_v != v:
                perm_iters.append((0,itertools.permutations(sets[v])))
                last_v = v
        new_permutations = [tuple(perm) for perm in generate_perms(perm_iters)]
        permutations = permutations.union(set(new_permutations))
        prev_n_permutations = len(permutations)
        
    return min_value, permutations

def objective_count_perm(Dorig,perm):
    D = Dorig[np.ix_(perm,perm)]#[perm,:][:,perm]
    return np.sum(np.sum(np.triu(D)))

def objective_count_exhaustive(D):
    n = D.shape[0]
    min_value = -np.Inf
    solutions = []
    for perm in itertools.permutations(range(n)):
        obj = objective_count_perm(D,perm)
        if not compare_objective_values(obj,min_value) and obj > min_value:
            min_value = obj
            solutions = [perm]
        elif compare_objective_values(obj,min_value):
            solutions.append(perm)
    details = {}
    details["P"] = solutions
    return min_value,details

def ranking_from_matrices(matrix,b,inxs=None):
    try:
        r = np.linalg.solve(matrix,b)
    except:
        r = np.dot(np.linalg.pinv(matrix),b)
    r = pd.Series(r,index=matrix.columns)
    if inxs is not None:
        r=r.iloc[inxs]
    perm,ranking = perm_ranking_from_r(r)
    return ranking, r, perm

def perm_ranking_from_r(r):
    perm = (-r).argsort()
    ranking = pd.Series(range(len(r)),index=r.sort_values(ascending=False).index)+1
    ranking = ranking.loc[perm.index]
    return perm, ranking
