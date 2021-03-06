import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import  chi2

def plot_ellipse(semimaj=1,semimin=1,phi=0,x_cent=0,y_cent=0,theta_num=int(1e3),ax=None,plot_kwargs=None,\
                    fill=False,fill_kwargs=None,data_out=False,cov=None,mass_level=0.68):
    '''
        An easy to use function for plotting ellipses in Python 2.7!

        The function creates a 2D ellipse in polar coordinates then transforms to cartesian coordinates.
        It can take a covariance matrix and plot contours from it.
        
        semimaj : float
            length of semimajor axis (always taken to be some phi (-90<phi<90 deg) from positive x-axis!)

        semimin : float
            length of semiminor axis

        phi : float
            angle in radians of semimajor axis above positive x axis

        x_cent : float
            X coordinate center

        y_cent : float
            Y coordinate center

        theta_num : int
            Number of points to sample along ellipse from 0-2pi

        ax : matplotlib axis property
            A pre-created matplotlib axis

        plot_kwargs : dictionary
            matplotlib.plot() keyword arguments

        fill : bool
            A flag to fill the inside of the ellipse 

        fill_kwargs : dictionary
            Keyword arguments for matplotlib.fill()

        data_out : bool
            A flag to return the ellipse samples without plotting

        cov : ndarray of shape (2,2)
            A 2x2 covariance matrix, if given this will overwrite semimaj, semimin and phi

        mass_level : float
            if supplied cov, mass_level is the contour defining fractional probability mass enclosed
            for example: mass_level = 0.68 is the standard 68% mass

    '''
    # Get Ellipse Properties from cov matrix
    if cov is not None:
        eig_vec,eig_val,u = np.linalg.svd(cov)
        # Make sure 0th eigenvector has positive x-coordinate
        if eig_vec[0][0] < 0:
            eig_vec[0] *= -1
        semimaj = np.sqrt(eig_val[0])
        semimin = np.sqrt(eig_val[1])
        if mass_level is None:
            multiplier = np.sqrt(2.279)
        else:
            distances = np.linspace(0,20,20001)
            chi2_cdf = chi2.cdf(distances,df=2)
            multiplier = np.sqrt(distances[np.where(np.abs(chi2_cdf-mass_level)==np.abs(chi2_cdf-mass_level).min())[0][0]])
        semimaj *= multiplier
        semimin *= multiplier
        phi = np.arccos(np.dot(eig_vec[0],np.array([1,0])))
        if eig_vec[0][1] < 0 and phi > 0:
            phi *= -1

    # Generate data for ellipse structure
    theta = np.linspace(0,2*np.pi,theta_num)
    r = 1 / np.sqrt((np.cos(theta))**2 + (np.sin(theta))**2)
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    data = np.array([x,y])
    S = np.array([[semimaj,0],[0,semimin]])
    R = np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])
    T = np.dot(R,S)
    data = np.dot(T,data)
    data[0] += x_cent
    data[1] += y_cent

    # Output data?
    if data_out == True:
        return data

    # Plot!
    return_fig = False
    if ax is None:
        return_fig = True
        fig,ax = plt.subplots()

    if plot_kwargs is None:
        ax.plot(data[0],data[1],color='b',linestyle='-')
    else:
        ax.plot(data[0],data[1],**plot_kwargs)

    if fill == True:
        ax.fill(data[0],data[1],**fill_kwargs)

    if return_fig == True:
        return fig


def plot(plotDetails:dict):
    data = plotDetails['data']
    predictions = plotDetails['predictions']
    mu = plotDetails['mu']
    cov = plotDetails['cov']
    ax = plt.axes()
    ax.scatter(data[:,0], data[:,1], c=predictions, cmap='Pastel2')
    ax.plot(mu[:,0], mu[:,1], 'bx')
    for k in range(len(cov)):
        plot_ellipse(x_cent=mu[k,0], y_cent=mu[k,1], cov=cov[k][0:2,0:2], ax=ax)
    plt.title(plotDetails['title'] + ', epoch = ' + str(plotDetails['epoch']))
    plt.xlabel(plotDetails['xlabel'])
    plt.ylabel(plotDetails['ylabel'])
    plt.show()