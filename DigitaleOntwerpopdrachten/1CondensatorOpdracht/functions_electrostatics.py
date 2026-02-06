import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy.ma as ma


def find_idx_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx



def initialization_contour(V,B,V0):
    """ Initialize electrical potential of domain boundaries at V0 """
    V[0,:] = V0  # top edge
    V[-1,:] = V0  # bottom edge
    V[:,-1] = V0  # right edge
    B[0,:] = True
    B[-1,:] = True
    B[:,-1] = True
    return V, B

def create_equipotential_disk(V,B,idx_z1,idx_z2,idx_R,V1,V2):
    B[idx_z1,:idx_R] = True
    V[idx_z1,:idx_R] = V1
    B[idx_z2,:idx_R] = True
    V[idx_z2,:idx_R] = V2
    return V, B

def initialize_variables_Laplace(grid_half_width,disk_radius,half_height_domain,h,z_pos_disk1,z_pos_disk2,V0,V1,V2):
    r = np.arange(0, grid_half_width, h)  # radius
    z = np.arange(-half_height_domain, half_height_domain, h)  # width
    Nr = len(r)
    Nz = len(z)

    r_repmat = np.tile(r,(Nz,1))

    V = np.zeros((Nz,Nr))
    B = np.zeros((Nz,Nr), dtype=bool)

    idx_z1 = find_idx_nearest(z, z_pos_disk1)
    idx_z2 = find_idx_nearest(z, z_pos_disk2)
    idx_R = find_idx_nearest(r, disk_radius)

    V, B = initialization_contour(V,B,V0)
    V, B = create_equipotential_disk(V,B,idx_z1,idx_z2,idx_R,V1,V2)

    return r, z, r_repmat, V, B, idx_R, idx_z1, idx_z2


def compute_diff(Va,Vb):
    Nz = Va.shape[0]
    Nr = Va.shape[1]
    squared_diff = 0
    for i in range(Nz):
        for j in range(Nr):
            squared_diff += (Va[i,j]-Vb[i,j])**2
    return (squared_diff/(Nr*Nz))**(1/2)


"""============================================================================
METHOD OF JACOBI to solve Laplace equation (relaxation)
-------------------------------------------------------------------------------
"""

def iteration_jacobi_FAST(V,B,r_repmat,h,idx_z1,idx_z2,idx_R,V1,V2):
    V_copy = V.copy()
    """
    for i in range(1,Nr):
        for j in range(Nz):
            if B[i,j]: # if [i,j] is point on domain boundaries ... do nothing
                V[i,j] = V_copy[i,j]
            else:
                #V[i,j] = (V_copy[i+1,j]+V_copy[i-1,j]+V_copy[i,j+1]+V_copy[i,j-1])/4
                V[i,j] = (V_copy[i+1,j]*(1+h/(2*r[i]))+V_copy[i-1,j]*(1-h/(2*r[i]))+V_copy[i,j+1]+V_copy[i,j-1])/4
    """         
    V[1:-1,1:-1] = (V_copy[1:-1,2:]*(1+h/(2*r_repmat[1:-1,1:-1]))+V_copy[1:-1,:-2]*(1-h/(2*r_repmat[1:-1,1:-1]))+V_copy[2:,1:-1]+V_copy[:-2,1:-1])/4

    create_equipotential_disk(V,B,idx_z1,idx_z2,idx_R,V1,V2)  # maintain electric potential in conducting disk(s) constant

    V[:,0] = V_copy[:,1]  # on axis of disk, dV/dr=0

    return compute_diff(V_copy,V)


def solve_Laplace_equation(V,B,r_repmat,h,idx_z1,idx_z2,idx_R,V1,V2,eps):
    compteur = 0
    while iteration_jacobi_FAST(V,B,r_repmat,h,idx_z1,idx_z2,idx_R,V1,V2) > eps:
        iteration_jacobi_FAST(V,B,r_repmat,h,idx_z1,idx_z2,idx_R,V1,V2)
        compteur += 1
        #print(iteration_jacobi_FAST() - eps)
    return compteur

def compute_E_disk(V,B,h):
    Nz = V.shape[0]
    Nr = V.shape[1]
    Er = np.zeros((Nz-2,Nr-1))
    Ez = np.zeros((Nz-2,Nr-1))
    norme_E = np.zeros((Nz-2,Nr-1))
    for i in range(1,Nz-1): 
        for j in range(1,Nr-1):
            if (B[i,j] or B[i,j+1] or B[i,j-1] or B[i-1,j] or B[i+1,j]):  # if grid point on domain boundary
                Er[i-1,j-1] = 0.
                Ez[i-1,j-1] = 0.
            else:
                Er[i-1,j-1] = -(V[i,j+1]-V[i,j-1])/(2.*h)
                Ez[i-1,j-1] = -(V[i+1,j]-V[i-1,j])/(2.*h)

    Er[:,0] = 0  # first column is the symmetry axis
    Ez[:,0] = -(V[2:,0]-V[:-2,0])/(2.*h)                

    norme_E = (Er**2+Ez**2)**0.5
    return Er, Ez, norme_E



def compute_E_pt_charge(V,B,h):
    Nz = V.shape[0]
    Nr = V.shape[1]
    Er = np.zeros((Nz-2,Nr-2))
    Ez = np.zeros((Nz-2,Nr-2))
    norme_E = np.zeros((Nz-2,Nr-2))
    for i in range(1,Nz-1): 
        for j in range(1,Nr-1):
            if (B[i,j] or B[i,j+1] or B[i,j-1] or B[i-1,j] or B[i+1,j]):  # if grid point on domain boundary
                Er[i-1,j-1] = 0.
                Ez[i-1,j-1] = 0.
            else:
                Er[i-1,j-1] = -(V[i,j+1]-V[i,j-1])/(2.*h)
                Ez[i-1,j-1] = -(V[i+1,j]-V[i-1,j])/(2.*h)

    norme_E = (Er**2+Ez**2)**0.5
    return Er, Ez, norme_E




def initialize_plane_grid_for_uniformly_charged_disk(half_height_domain,grid_half_width,grid_step):

    r = np.arange(0, grid_half_width, grid_step)  # width
    z = np.arange(-half_height_domain, half_height_domain, grid_step)  # width
    Nr = len(r)
    Nz = len(z)

    B = np.zeros((Nz,Nr), dtype=bool)

    return r,z,B



def initialize_plane_grid_for_pt_charge_at_origin(half_height_domain,grid_half_width,grid_step):

    r = np.arange(0, grid_half_width, grid_step)  # width
    z = np.arange(-half_height_domain, half_height_domain, grid_step)  # width
    Nr = len(r)
    Nz = len(z)
    B = np.zeros((Nz,Nr), dtype=bool)

    idx_z = find_idx_nearest(z, 0)
    idx_R = find_idx_nearest(r, 0)
    B[idx_z, idx_R] = True

    return r,z,B





def electric_potential_point_charge_cartesian(r_charge, R, Z, charge):
    epsilon0 = 8.854e-12  # permittivity of free space (F/m)

    # Separation vector (between charge and field point)
    sx = R - r_charge[0]
    sy = 0. - r_charge[1]
    sz = Z - r_charge[2]

    s_norm = np.sqrt(sx**2 + sy**2 + sz**2)
    V = charge / (4 * np.pi * epsilon0 * s_norm)
    V[s_norm<0.00001] = 0.

    return V




def calculate_V_disk_at_origin_uniform_surface_charge_density(z_disk,charge_one_point,disk_radius,inter_charge_distance,r,z):
    x_positions = np.arange(-disk_radius, disk_radius, inter_charge_distance)
    y_positions = np.arange(-disk_radius, disk_radius, inter_charge_distance)
    cnt = 0

    Nr = len(r)
    Nz = len(z)
    V = np.zeros((Nz,Nr))
    Z, R = np.meshgrid(z, r, indexing='ij')

    for xc in x_positions:
        for yc in y_positions:
            if np.sqrt(xc**2+yc**2)<=disk_radius:
                r_charge = np.array([xc, yc, z_disk])
                #r_field = np.array([r, 0, z])
                V += electric_potential_point_charge_cartesian(r_charge, R, Z, charge_one_point)
                cnt += 1

    XX, YY = np.meshgrid(x_positions, y_positions)
    RR_mask = np.sqrt(XX*XX+YY*YY) > disk_radius
    XX[RR_mask] = np.nan
    YY[RR_mask] = np.nan
    
    # Create a figure and 3D axis
    fig = plt.figure(figsize=(8, 8))  # width, height in inches.
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(left=0)
    # Create scatter plot
    ax.scatter3D(XX, YY, YY*0, color='red', marker='o', s=3)
    #ax.view_init(60, 35)
    # Set specific Z-axis ticks
    ax.set_zticks([-1, 0, 1])
    ax.plot([0, 0], [0, 0], [-1, 1], 'k', linewidth=2)  # vierkante haken om 0,0 toegevoegd
    #ax.set_zlim(-1, 1)
    ax.legend(['punt ladingen','schijf as'])
    # Labels
    ax.set_xlabel('X as')
    ax.set_ylabel('Y as')
    ax.set_zlabel('Z as')
    ax.set_title(f'Uniform geladen schijf ({cnt:1d} punt ladingen)')
    ax.set_box_aspect(None, zoom=0.88)

    return V, cnt

"""
def calculate_E_point_charge_at_origin(E,charge_one_point,r_field):
    # one point charge at origin:
    xc = 0
    yc = 0
    zc = 0
    r_charge = np.array([xc, yc, zc])
    ex, ey, ez = electric_field_point_charge_cartesian(r_charge, r_field, charge_one_point)
    E["x"] = ex
    E["y"] = ey
    E["z"] = ez
    E_norm = np.sqrt(E["x"]**2 + E["y"]**2 + E["z"]**2)
    return E, E_norm
"""

def calculate_V_point_charge_at_origin(charge_one_point,r,z):
    # One point charge at origin:
    xc = 0
    yc = 0
    zc = 0
    r_charge = np.array([xc, yc, zc])

    Nr = len(r)
    Nz = len(z)
    V = np.zeros((Nz,Nr))
    Z, R = np.meshgrid(z, r, indexing='ij')

    V = electric_potential_point_charge_cartesian(r_charge, R, Z, charge_one_point)
    return V


def extents(f):
    delta = f[1] - f[0]
    return [f[0] - delta/2, f[-1] + delta/2]


def plot_results_disk(Ez,Er,normE,V,r,z,h,disk_radius,z_pos_disk1,z_pos_disk2):
    plt.figure(10, figsize=(9, 4))
    plt.subplot(1, 3, 1)
    nb_equipot = 20
    cont=plt.contour(r,z,V,nb_equipot,colors='k')
    plt.plot([0, disk_radius-h], [z_pos_disk1, z_pos_disk1], 'r', linewidth=2)
    plt.plot([0, disk_radius-h], [z_pos_disk2, z_pos_disk2], 'r', linewidth=2)
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.title('Elektrisch potentiaal \n(equipotentiaal lijnen)')
    plt.axis('scaled')
    plt.clabel(cont)

    plt.subplots_adjust(wspace=0.5)

    # Create field point coordinates:
    Z, R = np.meshgrid(z[1:-1], r[1:-1], indexing='ij')

    plt.figure(10)
    plt.subplot(1, 3, 2)
    skip = 5  # downsample for clearer arrows
    plt.quiver(R[::skip, ::skip], Z[::skip, ::skip], Er[::skip, ::skip], Ez[::skip, ::skip])
    plt.plot([0, disk_radius-h], [z_pos_disk1, z_pos_disk1], 'r', linewidth=2)
    plt.plot([0, disk_radius-h], [z_pos_disk2, z_pos_disk2], 'r', linewidth=2)
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.axis('scaled')
    plt.title("Elektrische veld vectoren")

    plt.figure(10)
    plt.subplot(1, 3, 3)
    plt.imshow(normE, aspect='auto', interpolation='none',
            extent=extents(r[:-1]) + extents(z[1:-1]), origin='lower')
    plt.plot([0, disk_radius-h], [z_pos_disk1, z_pos_disk1], 'r', linewidth=2)
    plt.plot([0, disk_radius-h], [z_pos_disk2, z_pos_disk2], 'r', linewidth=2)
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.title("Norm elektrische veld")
    plt.colorbar(label='|E| (V/m)')
    plt.axis('scaled')

    plt.show()


def plot_results_pt_charge_at_origin(Ez,Er,normE,V,r,z,h):
    plt.figure(10,figsize=(9, 4))
    plt.subplot(1, 3, 1)
    nb_equipot = 200
    cont=plt.contour(r,z,V,nb_equipot,colors='k')
    plt.scatter(0,0,marker = 'o',color ='red')
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.title('Elektrisch potentiaal \n(equipotentiaal lijnen)')
    plt.axis('scaled')
    plt.clabel(cont)

    plt.subplots_adjust(wspace=0.5)

    # create field point coordinates:
    Z, R = np.meshgrid(z[1:-1], r[1:-1], indexing='ij')

    plt.figure(10)
    plt.subplot(1, 3, 2)
    skip = 5  # downsample for clearer arrows
    plt.quiver(R[::skip, ::skip], Z[::skip, ::skip], Er[::skip, ::skip], Ez[::skip, ::skip])
    plt.scatter(0,0,marker = 'o',color ='red')
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.axis('scaled')
    plt.title("Elektrische veld vectoren")

    plt.figure(10)
    plt.subplot(1, 3, 3)
    plt.imshow(normE, aspect='auto', interpolation='none',
            extent=extents(r[1:-1]) + extents(z[1:-1]), origin='lower')
    plt.scatter(0,0,marker = 'o',color ='red')
    plt.ylabel("Hoogte (m)")
    plt.xlabel("Radius (m)")
    plt.title("Norm elektrische veld")
    plt.colorbar(label='|E| (V/m)')
    plt.axis('scaled')

    plt.show()