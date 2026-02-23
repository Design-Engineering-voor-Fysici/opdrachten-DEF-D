import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# import time


###########################################################################################
# Imaging script for DEF assignment
# Authors: Eric Verschuur, Rolf Hut, TA Mark Melotto
# Date   : March 20, 2019 (latest update February 8, 2024)
# Delft University of Technology
###########################################################################################

# To read from CSV file, in this case with , separation - uncomment this statement and adapt file name
# data= pd.read_csv('DEF_metingen_test.csv', sep=",", header=None, names=["xs", "ys", "xr", "yr", "R"])

# Or direct input in the code
# make sure that each measurement is given by 5 numbers (in cm):
# only use the VALID measurements, not the one with maximum distance that missed the object.
# Put them ins this order per line:
# Source_x Source_y Receiver_x Receiver_y Distance

# ----------------------------------------------------------------------------------
# The DEF imaging function:
# input is the measured data (coordinates and measured distances)
# output is the estimated origin and angles of the object, including uncertainties
# it also make a plot of the final estimated object
# ----------------------------------------------------------------------------------
def imagingDEF(data):
    #    data = pd.DataFrame(columns=["xs", "ys", "xr", "yr", "R"], data=[
    #        [0,50,0,40,41.2],
    #        [0,40,0,30,41.2],
    #        [0,30,0,20,41.2],
    #        [10,0,40,0,50.0],
    #        [20,0,50,0,50.0],
    #        [30,0,60,0,50.0]
    #        ])
    # start_time = time.time()
    # just check the data
    print('Running the imaging algorithm with the following data:')
    print(data)

    ###########################################################################################
    # DO NOT CHANGE ANYTHING BELOW THIS LINE
    ###########################################################################################

    # assign arrays to the columns of the input
    xs = data['xs']
    ys = data['ys']
    xr = data['xr']
    yr = data['yr']
    R = data['R']

    # starting values of parameters and search range
    x00 = 60
    y00 = 60
    alpha0 = 20.0
    beta0 = 20.0

    # define perturbation value for derivatives
    d_xy = 0.1
    d_angle = 0.3
    step = 2.0
    stepmin = 1e-8
    improvement = 0.0

    # verbose option to show more details
    # verbose=0: regular option for student's use
    # verbose=1: show more detailed steps
    # verbose=2: also show all random objects
    # verbose = 0

    # plot initial solution
    plot_ellipses(xs, ys, xr, yr, R)
    xmin, ymin, weight = define_object(x00, y00, alpha0, beta0)
    plt.plot(xmin, ymin, 'm', linewidth=2.0)
    plt.grid()
    plt.title('Starting position')
    plt.show()
    # print('weight=',weight)

    # keep track of largest variations with similar objfun
    dx0max = 0.0
    dy0max = 0.0
    dalphamax = 0.0
    dbetamax = 0.0

    # number of iterations
    niter = 30

    print("\nWacht tot berekeningen klaar zijn; er komen %3d iteraties ...\n" %(niter))

    # ------------------------------------------------------------------------------
    # iterate over new starting points
    # ------------------------------------------------------------------------------
    for iter in range(niter):

        # reset foundmin and foundmax
        foundmin = 0
        foundmax = 0

        '''# not needed for students
        if verbose < 0:
            print('Start of iteration ', iter + 1, ' with step size=', step)
        '''
        # calculate the objective function for current best value
        objfun0 = objfun2024(x00, y00, alpha0, beta0, xs, ys, xr, yr, R)

        # keep track of the starting objfun in this iteration
        objfun00 = objfun0

        # calculate the derivative by perturbation
        objfun1 = objfun2024(x00 + d_xy, y00, alpha0, beta0, xs, ys, xr, yr, R)
        objfun2 = objfun2024(x00, y00 + d_xy, alpha0, beta0, xs, ys, xr, yr, R)
        objfun3 = objfun2024(x00, y00, alpha0 + d_angle, beta0, xs, ys, xr, yr, R)
        objfun4 = objfun2024(x00, y00, alpha0, beta0 + d_angle, xs, ys, xr, yr, R)

        # define gradient and normalize it
        grad = -np.array([objfun1 - objfun0, objfun2 - objfun0, objfun3 - objfun0, objfun4 - objfun0])
        gradnorm = grad / np.linalg.norm(grad)
        # print('normalized gradient:',gradnorm)
        # take a step along the gradient
        x0 = x00 + gradnorm[0] * step
        y0 = y00 + gradnorm[1] * step
        alpha = alpha0 + gradnorm[2] * step
        beta = beta0 + gradnorm[3] * step
        objfun = objfun2024(x0, y0, alpha, beta, xs, ys, xr, yr, R)

        while objfun > objfun0:
            ''' #  not needed for students
            if verbose > 0:
                print("Found objfun=%6.3f too large, reduce step=%13.6e" % (objfun, step))
            '''
            step = step / 2.0
            if step < stepmin:
                break
            x0 = x00 + gradnorm[0] * step
            y0 = y00 + gradnorm[1] * step
            alpha = alpha0 + gradnorm[2] * step
            beta = beta0 + gradnorm[3] * step
            objfun = objfun2024(x0, y0, alpha, beta, xs, ys, xr, yr, R)
        else:
            '''# not needed for students
            if verbose > 0:
                print(
                    "New minimum objfun=%6.3f x0=%6.3f y0=%6.3f alpha=%6.3f beta=%6.3f" % (objfun, x0, y0, alpha, beta))
            '''
            foundmin = 1
            improvement = (objfun00 - objfun) / objfun0
            objfun0 = objfun
            x00 = x0
            y00 = y0
            alpha0 = alpha
            beta0 = beta
            step = min(2 * step, 2.0, objfun / 2)

        # do random search in area around this (local) minimum
        nrand = 20 * iter
        if iter == niter - 1:
            nrand = 50000
            print('Last iteration, also determine uncertainty, wait a while..')
        objfunrand = np.zeros(nrand)
        # do random variations around this point to find better candidate
        for j in range(nrand):

            if iter < niter - 1:
                fact = 20 * np.random.rand(4) - 10.0
            else:
                fact = 100 * np.random.rand(4) - 50.0
            x0 = x00 + fact[0] * d_xy
            y0 = y00 + fact[1] * d_xy
            alpha = alpha0 + fact[2] * d_angle
            beta = beta0 + fact[3] * d_angle
            alpha, beta = limit_angle(alpha, beta)

            # calculate the objective function value
            objfun = objfun2024(x0, y0, alpha, beta, xs, ys, xr, yr, R)
            objfunrand[j] = objfun
            '''# not needed for students
            if verbose > 1:
                xmin, ymin, weight = define_object(x0, y0, alpha, beta)
                plt.plot(xmin, ymin, 'r', linewidth=0.5)
                plt.grid()
            '''

            # check if this one is better
            if objfun < objfun0:
                '''# not needed for students
                if verbose > 0:
                    print("New random minimum objfun=%6.3f x0=%6.3f y0=%6.3f alpha=%6.3f beta=%6.3f" % (
                    objfun, x0, y0, alpha, beta))
                '''
                # save these values
                foundmin = 1
                improvement = (objfun00 - objfun) / objfun0
                x00 = x0
                y00 = y0
                alpha0 = alpha
                beta0 = beta
                objfun0 = objfun
                if objfun < 2.0:
                    step = objfun
                # also reset the maximum value
                dx0max = 0.0
                dy0max = 0.0
                dalphamax = 0.0
                dbetamax = 0.0
                foundmax = 0

            # check if this is the largest error within objfun limit
            # store this limit and the object shapes
            if (iter == niter - 1 and objfun < objfun0 + 0.4):
                dx0 = abs(x00 - x0)
                dy0 = abs(y00 - y0)
                dalpha = abs(alpha0 - alpha)
                dbeta = abs(beta0 - beta)
                if dx0 > dx0max:
                    dx0max = dx0
                    xmin1, ymin1, weight = define_object(x0, y0, alpha, beta)
                if dy0 > dy0max:
                    dy0max = dy0
                    xmin2, ymin2, weight = define_object(x0, y0, alpha, beta)
                if dalpha > dalphamax:
                    dalphamax = dalpha
                    xmin3, ymin3, weight = define_object(x0, y0, alpha, beta)
                if dbeta > dbetamax:
                    dbetamax = dbeta
                    xmin4, ymin4, weight = define_object(x0, y0, alpha, beta)
                foundmax = 1
                if j > 20000:
                    break
            # give warnings for longer calculation times
            if j >= 10000 and j % 10000 == 0:
                print('wait a little longer....')

        # plot best result for this iteration
        if foundmin > 0 and improvement > 0.1 and niter % 3 == 0:
            plot_ellipses(xs, ys, xr, yr, R)
            xmin, ymin, weight = define_object(x00, y00, alpha0, beta0)
            plt.plot(xmin, ymin, 'm', linewidth=2.0)
            plt.title('iteration %d with average mismatch=%6.3f' % (iter + 1, objfun0))
            plt.grid()
            plt.show()

        # end of this iteration
        print('end iteration %d with average mismatch=%6.3f' % (iter + 1, objfun0))

    # ------------------------------------------------------------------------------
    # after iterations display final accuracy
    # ------------------------------------------------------------------------------

    # display final result for parameters with uncertainty
    print("###############################################################################")
    print("end of iteration ", iter + 1)
    print("Best alpha= %6.2f with uncertainty= %6.2f" % (alpha0, dalphamax))
    print("Best beta = %6.2f with uncertainty= %6.2f" % (beta0, dbetamax))
    print("Best x0   = %6.2f with uncertainty= %6.2f" % (x00, dx0max))
    print("Best y0   = %6.2f with uncertainty= %6.2f" % (y00, dy0max))
    print("###############################################################################")

    if foundmax == 0:
        print('no uncertainty found, please run again')
    # time.sleep(1)
    # next iteration; take output as initial values and smaller search area

    results = {'alpha': alpha0,
               'alpha_eps': dalphamax,
               'beta': beta0,
               'beta_eps': dbetamax,
               'x0': x00,
               'x0_eps': dx0max,
               'y0': y00,
               'y0_eps': dy0max}

    # define new figure te replot ellipses and optimum object
    plot_ellipses(xs, ys, xr, yr, R)
    if foundmax > 0:
        plt.plot(xmin1, ymin1, 'r', linewidth=1.0)
        plt.plot(xmin2, ymin2, 'r', linewidth=1.0)
        plt.plot(xmin3, ymin3, 'r', linewidth=1.0)
        plt.plot(xmin4, ymin4, 'r', linewidth=1.0)
    xmin, ymin, weight = define_object(x00, y00, alpha0, beta0)
    plt.plot(xmin, ymin, 'k', linewidth=4.0)
    plt.title('Final result iteration %d' % (iter + 1))
    plt.grid()
    plt.show()

    # show all objfun values from the last random search
    '''# not needed for students
    if verbose > 1:
        plt.figure()
        plt.plot(objfunrand)
    '''

    '''
    end_time = time.time() - start_time
    # print("###############################################################################")
    print(f"Tijd van het algoritme: {end_time:.2f} s")
    print("###############################################################################")
    '''
    return results


# ----------------------------------------------------------------------------------
# Function objfun2023: calculate the error for an assumed object location
# ----------------------------------------------------------------------------------

def objfun2024(x0, y0, alpha, beta, xs, ys, xr, yr, R):
    # eps defines weight of slopes in objfun
    eps = 3.0
    # define number of measurements points
    n = len(R)
    # print(n)
    # define the chosen object
    xobj, yobj, weight = define_object(x0, y0, alpha, beta)

    # calculate distance to all points
    xobj_new = np.tile(xobj, (n,1))
    yobj_new = np.tile(yobj, (n,1))

    # Convert to NumPy arrays explicitly
    xr_array = np.array(xr)[:, np.newaxis]
    yr_array = np.array(yr)[:, np.newaxis]

    new_DR = np.sqrt(np.square(xobj_new - xr_array) + np.square(yobj_new - yr_array))
    # print(f"{new_DR = }")

    # Convert to NumPy arrays explicitly
    xs_array = np.array(xs)[:, np.newaxis]
    ys_array = np.array(ys)[:, np.newaxis]

    new_DS = np.sqrt(np.square(xobj_new - xs_array) + np.square(yobj_new - ys_array))

    # Convert to NumPy arrays explicitly
    R_array = np.array(R)[:, np.newaxis]

    Dtot_new = np.abs(new_DR + new_DS - R_array)

    Dmin_new = np.min(Dtot_new, axis=1)
    Imin_new = np.argmin(Dtot_new, axis=1)
    ii_new = np.minimum(np.maximum(1, Imin_new), len(xobj) - 2)

    weight_new = np.tile(weight, (7,1))

    slope_new = weight_new[:,ii_new] * (new_DR[np.arange(len(new_DR)), ii_new + 1] + new_DS[np.arange(len(new_DS)), ii_new + 1] - new_DR[np.arange(len(new_DR)), ii_new - 1] - new_DS[np.arange(len(new_DS)), ii_new - 1])
    slope_new = slope_new[0]

    D_aver_new = np.mean(Dmin_new)
    slope_aver_new = np.mean(abs(slope_new))

    objfun_new = D_aver_new + eps * slope_aver_new

    # return the objfun value
    return objfun_new




# ----------------------------------------------------------------------------------
# Function make_object: calculate the object gridpoints
# ----------------------------------------------------------------------------------
def define_object(x0, y0, alpha, beta):
    # length of one segment (in cm)
    lenseg = 20
    # set up left branche
    dy = np.linspace(0, lenseg, lenseg + 1)
    y1 = y0 + dy
    x1 = x0 + dy * np.tan(beta * np.pi / 180)
    # set up right branche
    dx = np.linspace(0, lenseg, lenseg + 1)
    x2 = x0 + dx
    y2 = y0 + dx * np.tan(alpha * np.pi / 180)
    # return the object location vector
    xobj = np.concatenate((x1, x2), axis=0)
    yobj = np.concatenate((y1, y2), axis=0)
    # also define a weight for the slopes: exclude the edges
    weight = 1.0 + 0.0 * xobj
    # weight = np.ones_like(xobj)  # somehow this seems to be slower
    weight[0] = 0.1
    weight[lenseg] = 0.1
    weight[lenseg + 1] = 0.1
    weight[2 * lenseg + 1] = 0.1
    return xobj, yobj, weight


# ----------------------------------------------------------------------------------
# Function to limit the values of alpha and beta
# ----------------------------------------------------------------------------------

def limit_angle(alpha, beta):
    # keep alpha and beta within pre-defined range
    alpha = np.minimum(43, np.maximum(-43, alpha))
    beta = np.minimum(43, np.maximum(-43, beta))
    return alpha, beta


# ----------------------------------------------------------------------------------
# plot the ellipses
# ----------------------------------------------------------------------------------
def plot_ellipses(xs, ys, xr, yr, R):
    # get number of coordinate pairs
    n = len(R)

    # define midpoints for all measurements
    xm = (xs + xr) / 2
    ym = (ys + yr) / 2

    # define offset for all measurements
    offset = np.sqrt((xs - xr) * (xs - xr) + (ys - yr) * (ys - yr))

    # define distance from midpoint to ellipse point
    d = 0.5 * np.sqrt(R * R - offset * offset)

    # define the ellipse point from midpoint
    vecx = d * (ys - yr) / offset
    # vecy = -d * (xs - xr) / offset  # is not used

    # define new figure te replot ellipses and optimum object
    plt.figure(figsize=(8, 8))
    axes = plt.gca()
    axes.set_xlim([0, 70])
    axes.set_ylim([0, 70])
    plt.xlabel('X-axis (cm)')
    plt.ylabel('Y-axis (cm)')

    # for each measurement, plot one ellipse   
    for i in range(n):
        # plot the source and receiver location
        plt.plot(xs[i], ys[i], 'ro')
        plt.plot(xr[i], yr[i], 'bo')
        plt.grid()
        # plot the ellipe point from the midpoint
        if (xm[i] + vecx[i]) > 0:
            scl = 1
        else:
            scl = -1
        # plot points away from the ellipse
        teta = np.arctan2(ys[i] - yr[i], xs[i] - xr[i])
        # define array of ellipse points
        th = np.linspace(0, 2 * np.pi, 100)

        # calculate x and y points
        x = xm[i] + 0.5 * R[i] * np.cos(th) * np.cos(teta) - d[i] * np.sin(th) * np.sin(teta)
        y = ym[i] + 0.5 * R[i] * np.cos(th) * np.sin(teta) + d[i] * np.sin(th) * np.cos(teta)
        plt.plot(x, y)
        plt.grid()
        # h=ellipse(xm(i),ym(i),R(i)/2,d(i),teta)
        # print(teta)



# Test the module by uncommenting this block
data = pd.DataFrame(columns=["xs", "ys", "xr", "yr", "R"], data=[
    # [0,43,0,40,40.0],
    [0, 39, 0, 29, 41.2],
    [0, 30, 0, 20, 41.2],
    [10, 0, 40, 0, 50.0],
    # [19,0,49,0,50.0],
    [29, 0, 59, 0, 50.8]
])
data = pd.DataFrame(columns=["xs", "ys", "xr", "yr", "R"], data=[
    [0, 30, 0, 20, 35],
    [0, 22, 0, 12, 35.2],
    [38, 0, 28, 0, 32],
    [30, 0, 20, 0, 31.9]
])
# results=imagingDEF(data)
