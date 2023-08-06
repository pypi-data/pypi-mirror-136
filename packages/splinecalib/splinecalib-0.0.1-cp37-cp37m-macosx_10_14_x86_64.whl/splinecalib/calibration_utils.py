"""Calibration of predicted probabilities."""
from __future__ import division

import numpy as np
import scipy as sp
import random
import matplotlib.pyplot as plt
import warnings
from scipy.stats import binom
from loss_fun_c import pen_ll_fun, pen_ll_fun_grad

def _natural_cubic_spline_basis_expansion(xpts, knots):
    """Does the natural cubis spline bases for a set of points and knots"""
    num_knots = len(knots)
    num_pts = len(xpts)
    outmat = np.zeros((num_pts,num_knots))
    outmat[:, 0] = np.ones(num_pts)
    outmat[:, 1] = xpts

    def make_func_H(k):
        def make_func_d(k):
            def func_d(x):
                denom = knots[-1] - knots[k-1]
                numer = (np.maximum(x-knots[k-1], np.zeros(len(x))) ** 3 - 
                        np.maximum(x-knots[-1], np.zeros(len(x))) ** 3)
                return numer/denom
            return func_d

        def func_H(x):
            d_fun_k = make_func_d(k)
            d_fun_Km1 = make_func_d(num_knots-1)
            return d_fun_k(x) -  d_fun_Km1(x)
        return func_H
    for i in range(1, num_knots-1):
        curr_H_fun = make_func_H(i)
        outmat[:, i+1] = curr_H_fun(xpts)
    return outmat


def logreg_cv_direct(X, y, num_folds, reg_param_vec, method, max_iter,
              tol, weightvec=None, random_state=42, reg_prec=4, ps_mode='fast'):
    """Routine to find the best fitting penalized Logistic Regression.

    User must provide, the X, y, number of folds, range of `lambda` parameter
    and other specs for the optimization.
    """
    fn_vec = get_stratified_foldnums(y, num_folds, random_state=random_state)
    preds = np.zeros(len(y))
    ll_vec = np.zeros(len(reg_param_vec))
    start_coef_vec = np.zeros(X.shape[1])
    for i,lam_val in enumerate(reg_param_vec):
        num_folds_to_search = 1 if ps_mode=='fast' else num_folds
        for fn in range(num_folds_to_search):
            X_tr = X[fn_vec!=fn,:]
            y_tr = y[fn_vec!=fn]
            X_te = X[fn_vec==fn,:]
            if weightvec is not None:
                weightvec_tr = weightvec[fn_vec!=fn]
                opt_res = sp.optimize.minimize(pen_ll_fun_grad,
                                               start_coef_vec,
                                                (X_tr, y_tr,
                                                 float(lam_val), weightvec_tr),
                                                method=method,
                                                jac=True,
                                                options={"gtol": tol,
                                                 "maxiter": max_iter})
            else:
                opt_res = sp.optimize.minimize(pen_ll_fun_grad,
                                               start_coef_vec,
                                                (X_tr, y_tr,
                                                 float(lam_val)),
                                                method=method,
                                                jac=True,
                                                options={"gtol": tol,
                                                 "maxiter": max_iter})
            coefs = opt_res.x
            if not opt_res.success:
                warnings.warn("Optimization did not converge for lambda={}".format(lam_val))
            preds[fn_vec==fn] = 1/(1+np.exp(-X_te.dot(coefs)))
        if ps_mode=='fast':
            ll_vec[i]=my_log_loss(y[fn_vec==0],preds[fn_vec==0])
        else:
            ll_vec[i]=my_log_loss(y,preds)
    best_index = np.argmin(np.round(ll_vec,decimals=reg_prec))
    best_lam_val = reg_param_vec[best_index]
    best_loss = ll_vec[best_index]
    if weightvec is not None:
        opt_res = sp.optimize.minimize(pen_ll_fun_grad,
                               start_coef_vec,
                                (X_tr, y_tr,
                                 best_lam_val, weightvec_tr),
                                jac=True,
                                options={"gtol": tol,
                                "maxiter": max_iter})
    else:
        opt_res = sp.optimize.minimize(pen_ll_fun_grad,
                               start_coef_vec,
                                (X_tr, y_tr,
                                 best_lam_val),
                                jac=True,
                                options={"gtol": tol,
                                 "maxiter": max_iter})
    if not opt_res.success:
        warn_str = """Optimization did not converge for final fit.
                    This is usually due to numerical issues.
                    Consider in"""
        warnings.warn("".format(lam_val))

    return(best_lam_val, ll_vec, opt_res)



def plot_prob_calibration(calib_fn, show_baseline=True, ax=None, **kwargs):
    if ax is None:
        ax = _gca()
        fig = ax.get_figure()
    ax.plot(np.linspace(0,1,100),calib_fn(np.linspace(0,1,100)),**kwargs)
    if show_baseline:
        ax.plot(np.linspace(0,1,100),(np.linspace(0,1,100)),'k--')
    ax.axis([-0.1,1.1,-0.1,1.1])

def my_logit(vec, base=np.exp(1), eps=1e-16):
    vec = np.clip(vec, eps, 1-eps)
    return (1/np.log(base)) * np.log(vec/(1-vec))

def my_logistic(vec, base=np.exp(1)):
    return 1/(1+base**(-vec))

def plot_reliability_diagram(y,
                             x,
                             bins=np.linspace(0,1,21),
                             show_baseline=True,
                             baseline_color="black",
                             baseline_width=1,
                             error_bars=True,
                             error_bar_color='C0',
                             error_bar_alpha=.05,
                             error_bar_width=2,
                             marker=".",
                             marker_color='C1',
                             marker_edge_color="C1",
                             marker_size=50,
                             scaling='none', 
                             scaling_eps=.0001,
                             scaling_base=10, 
                             cap_width=1,
                             cap_size=5,
                             show_histogram=False,
                             bin_color="C0",
                             bin_edge_color="black",  
                             ax1_x_title="Predicted",
                             ax1_y_title="Empirical",
                             ax2_x_title="Predicted Scores",
                             ax2_y_title="Count",
                             ax_title_weight="normal",
                             ax_title_size=12,
                             title_size=16,
                             title_weight='normal',
                             reliability_title="Reliability Diagram",
                             histogram_title="Probability Distribution",
                             layout_pad=3.0,
                             legend_names=['Perfect', 'Model', '95% CI'],
                             legend_size='small',
                             grid_color="#EEEEEE",
                             grid_line_width=0.8,
                             plot_style=None,
                             **kwargs):
    """Plots a reliability diagram of predicted vs empirical probabilities.
    
    Parameters
    ----------
    y: Array-like, length (n_samples). The true outcome values as integers (0 or 1)
    
    x: The predicted probabilities, between 0 and 1 inclusive.
    
    bins: Array-like, the endpoints of the bins used to aggregate and estimate the
        empirical probabilities.  Default is 20 equally sized bins.
        from 0 to 1, i.e. [0,0.05,0.1,...,.95, .1].
        
    show_baseline: Whether or not to print a dotted line representing
        y=x (perfect calibration).  Default is True.
        
    baseline_color: The color of the baseline. Default is black.
    
    baseline_width: The width of the baseline. Default is 1.
    
    error_bars: Whether to show error bars reflecting the confidence
        interval under the assumption that the input probabilities are
        perfectly calibrated. Default is True.
        
    error_bar_color: The color of the errorbar. Default is 'C0', matplotlib blue.   
    error_bar_alpha: The alpha value to use for the error_bars.  Default
        is .05 (a 95% CI).  Confidence intervals are based on the exact
        binomial distribution, not the normal approximation.
        
    error_bar_width: The width of the error bar lines. Default is 2.
    
    marker: The style of the marker. Default is '.'
    
    marker_color: The color of the marker. Default is 'C1', matplotlib orange.
    
    marker_size: The size of the marker. Default is 50.
    
    scaling: Default is 'none'. Alternative is 'logit' which is useful for
        better examination of calibration near 0 and 1.  Values shown are
        on the scale provided and then tick marks are relabeled.
        
    scaling_eps: Default is .0001.  Ignored unless scaling='logit'. This 
        indicates the smallest meaningful positive probability you
        want to consider.
        
    scaling_base: Default is 10. Ignored unless scaling='logit'. This
        indicates the base used when scaling back and forth.  Matters
        only in how it affects the automatic tick marks.
        
    cap_size: The length of the error bar caps in points. Default is 5.
    
    show_histogram: Whether or not to show a separate histogram of the
        number of values in each bin.  Default is False.
        
    bin_color: The color of the histogram bins. Default is 'C0', 
        matplotlib blue.
    
    bin_edge_color: The color of the edges around the histogram bins. 
        Default is 'black'.
    
    ax1_x_title: X-axis title for reliability plot. Default is 
        "Predicted".
    
    ax1_y_title: Y-axis title for reliability plot. Default is 
        "Empirical".
    
    ax2_x_title: X-axis title for histogram. Default is "Predicted 
        Scores".
    
    ax2_y_title: Y-axis title for histogram. Default is "Count".
    
    ax_title_weight: The font weight for axes titles. Default 
        is "normal".
    
    ax_title_size: The font size for the axes titles. Default 
        is 12.
    
    title_size: The font size for the subplot titles. Default 
        is 16.
    
    title_weight: The font weight for the subplot titles. Default 
        is 'normal'.
    
    reliability_title: The title for the reliability plot. Default 
        is "Reliability Diagram".
    
    histogram_title: The title for the histogram. Default is "Probability 
        Distribution".
    
    layout_pad: Space to add between subplots to give y-axis title and 
        labels room to breath. Default is 3.0.
        
    legend_names: List of names for the legend labels. Defaults to 
        'Perfect', 'Model', '95% CI'.
    
    legend_size: 'xx-small', 'x-small', 'small', 'medium', 
        'large', 'x-large', 'xx-large' or integer for the legend 
        size. Defaults to 'small'.
        
    grid_color: The color of the grid. Default is "#EEEEEE".
    
    grid_line_width: The width of the gridlines. Default is 0.8.
    
    plot_style: Check available styles "plt.style.available".
        ['default', 'classic', 'Solarize_Light2', '_classic_test_patch', 'bmh', 
        'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 
        'seaborn', 'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark', 
        'seaborn-dark-palette', 'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 
        'seaborn-notebook', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk', 
        'seaborn-ticks', 'seaborn-white','seaborn-whitegrid', 'tableau-colorblind10'] 
        Defaults to None.
        
    **kwargs: additional args to be passed to the plt.scatter matplotlib call.
    
    Returns
    -------
    A dictionary containing the x and y points plotted (unscaled) and the 
        count in each bin.
    """
    
    # Set Plot Style
    if plot_style is None:
        None
        
    else:
        plt.style.use(plot_style)

    digitized_x = np.digitize(x, bins)
    mean_count_array = np.array([[np.mean(y[digitized_x == i]),
                                  len(y[digitized_x == i]),
                                  np.mean(x[digitized_x==i])] 
                                  for i in np.unique(digitized_x)])
    x_pts_to_graph = mean_count_array[:,2]
    y_pts_to_graph = mean_count_array[:,0]
    bin_counts = mean_count_array[:,1]
    if show_histogram:
        plt.subplot(1,2,1)
    if scaling=='logit':
        x_pts_to_graph_scaled = my_logit(x_pts_to_graph, eps=scaling_eps,
                                         base=scaling_base)
        y_pts_to_graph_scaled = my_logit(y_pts_to_graph, eps=scaling_eps,
                                         base=scaling_base)
        prec_int = np.max([-np.floor(np.min(x_pts_to_graph_scaled)),
                    np.ceil(np.max(x_pts_to_graph_scaled))])
        prec_int = np.max([prec_int, -np.floor(np.log10(scaling_eps))])
        low_mark = -prec_int
        high_mark = prec_int
        if show_baseline:
            plt.plot([low_mark, high_mark], [low_mark, high_mark],'--', color=baseline_color, linewidth=baseline_width, zorder=2)
        plt.scatter(x_pts_to_graph_scaled, 
                    y_pts_to_graph_scaled,
                    c=marker_color,
                    ec=marker_edge_color,
                    s=marker_size, 
                    zorder=3, 
                    marker=marker, 
                    **kwargs)
        locs, labels = plt.xticks()
        labels = np.round(my_logistic(locs, base=scaling_base), decimals=4)
        plt.xticks(locs, labels)
        locs, labels = plt.yticks()
        labels = np.round(my_logistic(locs, base=scaling_base), decimals=4)
        plt.yticks(locs, labels)
        plt.grid(which='major', color=grid_color, linewidth=grid_line_width, zorder=1)
        plt.legend(legend_names, loc='upper left', fontsize=legend_size)
        if error_bars:
            prob_range_mat = binom.interval(1-error_bar_alpha,bin_counts,x_pts_to_graph)/bin_counts
            yerr_mat = (my_logit(prob_range_mat,eps=scaling_eps, base=scaling_base) - 
                       my_logit(x_pts_to_graph, eps=scaling_eps, base=scaling_base))
            yerr_mat[0,:] = -yerr_mat[0,:]
            plt.errorbar(x_pts_to_graph_scaled, 
                         x_pts_to_graph_scaled,
                         elinewidth=error_bar_width,
                         ecolor=error_bar_color,
                         yerr=yerr_mat,
                         capthick=cap_width,
                         capsize=cap_size,
                         ls="none",
                         zorder=2)
            plt.legend(['y=x', 'Model', '95% CI'], loc='upper left', fontsize=legend_size)
        plt.axis([low_mark-.1, high_mark+.1, low_mark-.1, high_mark+.1])
        plt.grid(which='major', color=grid_color, linewidth=grid_line_width, zorder=1)
        plt.legend(legend_names, loc='upper left')
    if scaling!='logit':
        if show_baseline:
            plt.plot(np.linspace(0,1,100),(np.linspace(0,1,100)),'--', color=baseline_color, linewidth=baseline_width, zorder=2)
        # for i in range(len(y_pts_to_graph)):
        plt.scatter(x_pts_to_graph,
                    y_pts_to_graph, 
                    c=marker_color,
                    ec=marker_edge_color,
                    s=marker_size, 
                    zorder=4, 
                    marker=marker, 
                    **kwargs)
        plt.axis([-0.1,1.1,-0.1,1.1])
        plt.grid(which='major', color=grid_color, linewidth=grid_line_width, zorder=1)
        plt.legend(legend_names, loc='upper left', fontsize=legend_size)
        if error_bars:
            yerr_mat = binom.interval(1-error_bar_alpha,bin_counts,x_pts_to_graph)/bin_counts - x_pts_to_graph
            yerr_mat[0,:] = -yerr_mat[0,:]
            plt.errorbar(x_pts_to_graph, 
                         x_pts_to_graph,
                         elinewidth=error_bar_width,
                         ecolor=error_bar_color,
                         yerr=yerr_mat,
                         capthick=cap_width,
                         capsize=cap_size,
                         ls="none",
                         zorder=3)
    plt.xlabel(ax1_x_title, fontsize=ax_title_size, fontweight=ax_title_weight)
    plt.ylabel(ax1_y_title, fontsize=ax_title_size, fontweight=ax_title_weight)
    plt.title(reliability_title, fontsize=title_size, fontweight=title_weight)
    plt.grid(which='major', color=grid_color, linewidth=grid_line_width, zorder=1)
    plt.legend(legend_names, loc='upper left', fontsize=legend_size)
    if show_histogram:
        plt.subplot(1,2,2)
        plt.hist(x,
                 bins=bins, 
                 ec=bin_edge_color,
                 color=bin_color,
                 zorder=2)
        plt.xlabel(ax2_x_title, fontsize=ax_title_size, fontweight=ax_title_weight)
        plt.ylabel(ax2_y_title, fontsize=ax_title_size, fontweight=ax_title_weight)
        plt.title(histogram_title, fontsize=title_size, fontweight=title_weight)
        plt.grid(which='major', color=grid_color, linewidth=grid_line_width, zorder=1)
        plt.tight_layout(pad=layout_pad)
    out_dict = {}
    out_dict['pred_probs'] = x_pts_to_graph
    out_dict['emp_probs'] = y_pts_to_graph
    out_dict['bin_counts'] = bin_counts
    return(out_dict)



def cv_predictions(model, X, y, num_cv_folds=5, stratified=True, clone_model=False, random_state=42):
    """Creates a vector of cross-validated predictions given the model and data.

   This function takes a model and repeatedly fits it on all but one fold and
   then makes predictions (using `predict_proba`) on the remaining fold.  It
   returns the full set of cross-validated predictions.

    Parameters
    ----------
    model: The model to be used for the fit and predict_proba calls.  If clone_model
        is True, model will be copied before it is refit, and the original will not 
        be modified.  If clone_model is False, model will be refit and changed.
        The `clone_model` option may not work outside of sklearn.

    X: The feature matrix to be used for the cross-validated predictions

    y: The outcome vector to be used for cross-validated predictions.  Should
        contain integers from 0 to num_classes-1.

    num_cv_folds: The number of folds to create when doing the cross-validated
        fit and predict calls.  More folds will take more time but may yield 
        better results.  Default is 5.

    stratified: Boolean variable indicating whether or not to assign points
        to folds in a stratified manner.  Default is True.

    clone_model: Whether to use the sklearn "clone" function to copy the model
        before it is refit.  If False, the model object will be modified.  The 
        setting True may not work outside of sklearn.  In this case it is
        best to make an identical (before fitting) model object and pass that
        as the argument.

    random_state: A random_state to pass to the fold selection.

    Returns
    ---------------------

    A matrix of size (nrows, ncols) where nrows is the number of rows in X and
    ncols is the number of classes as indicated by y.
    """
    if stratified:
        foldnum_vec = get_stratified_foldnums(y, num_cv_folds, random_state)
    else:
        foldnum_vec = np.floor(np.random.uniform(size=X.shape[0])*num_cv_folds).astype(int)
    model_to_fit = clone(model) if clone_model else model
    n_classes = np.max(y).astype(int)+1
    out_probs = np.zeros((X.shape[0],n_classes))
    for fn in range(num_cv_folds):
        X_tr = X.loc[foldnum_vec!=fn]
        y_tr = y[foldnum_vec!=fn]
        X_te = X.loc[foldnum_vec==fn]
        model_to_fit.fit(X_tr, y_tr)
        out_probs[foldnum_vec==fn,:] = model_to_fit.predict_proba(X_te)
    
    return(out_probs)

def get_stratified_foldnums(y, num_folds, random_state=42):
    """Given an outcome vector y, assigns each data point to a fold in a stratified manner.
    
    Assumes that y contains only integers between 0 and num_classes-1
    """
    fn_vec = -1 * np.ones(len(y))
    for y_val in np.unique(y):
        curr_yval_indices = np.where(y==y_val)[0]
        np.random.seed(random_state)
        np.random.shuffle(curr_yval_indices)
        index_indices = np.round((len(curr_yval_indices)/num_folds)*np.arange(num_folds+1)).astype(int)
        for i in range(num_folds):
            fold_to_assign = i if ((y_val%2)==0) else (num_folds-i-1)
            fn_vec[curr_yval_indices[index_indices[i]:index_indices[i+1]]] = fold_to_assign
    return(fn_vec)

def penalized_ll_fun(beta, X, y, lam=0, weight_vec=None, max_exp=50):
    betaX = X.dot(beta)
    mask_1a = (betaX >= -max_exp)
    mask_1b = (betaX < -max_exp)
    mask_2a = (betaX <=max_exp)
    mask_2b = (betaX > max_exp)
    ll_term = 0
    if weight_vec is None:
        ll_term += np.sum(y[mask_1a]*np.log(np.exp(-betaX[mask_1a])+1))
        ll_term += np.sum(y[mask_1b]*(-betaX[mask_1b]))
        ll_term += np.sum((1-y[mask_2a])*np.log(np.exp(betaX[mask_2a])+1))
        ll_term +=  np.sum((1-y[mask_2b])*(betaX[mask_2b]))
    else:
        ll_term += np.sum(weight_vec[mask_1a]*y[mask_1a]*np.log(np.exp(-betaX[mask_1a])+1))
        ll_term += np.sum(weight_vec[mask_1b]*y[mask_1b]*(-betaX[mask_1b]))
        ll_term += np.sum(weight_vec[mask_2a]*(1-y[mask_2a])*np.log(np.exp(betaX[mask_2a])+1))
        ll_term +=  np.sum(weight_vec[mask_2b]*(1-y[mask_2b])*(betaX[mask_2b]))
    reg_term = lam*np.mean(beta*beta)
    return(ll_term/X.shape[0]+reg_term)

def my_log_loss(truth_vec, pred_vec, eps=1e-16):
    pred_vec = np.clip(pred_vec, eps, 1-eps)
    val = np.mean(truth_vec*np.log(pred_vec)+(1-truth_vec)*np.log(1-pred_vec))
    return(-val)
