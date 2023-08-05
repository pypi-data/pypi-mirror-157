import numpy as np
import os


def sph_to_cart_pt(r, theta, phi):
    """
    Takes values of r, theta, and phi and converts to (xyz) 1D array
    """
    xyz = np.zeros(3)
    xyz[0] = r*np.sin(theta)*np.cos(phi)
    xyz[1] = r*np.sin(theta)*np.sin(phi)
    xyz[2] = r*np.cos(theta)
    return xyz


def sph_to_cart(r, theta, phi):
    """
    Takes values of r, theta, and phi and converts to (xyz) 1D array
    """
    x = np.zeros(r.size)
    y = np.zeros(r.size)
    z = np.zeros(r.size)
    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return np.array([x, y, z]).T


def centroid_dists_angles(Xn, xyz, rXn, N):
    """
    Calculate metal-centroid distances and centroid-metal-centroid angle
    Create a list of 10 closest carbon atoms
    """

    C_atoms = []
    for i in range(0, N):
        if Xn[i] == "C":
            C_atoms.append((xyz[i, 0], xyz[i, 1], xyz[i, 2], rXn[i]))
    sorted_list = np.array(sorted(C_atoms, key=lambda x: x[3]))
    top_ten_coord = sorted_list[:10]

    # Calculate distances between 10 C atoms closest to metal
    dist_sq = np.sum((top_ten_coord[:, :] - top_ten_coord[0, :]) ** 2, axis=1)
    # Determine which indicies belong to Cp1 and Cp2
    ind1 = np.argpartition(dist_sq, 5)[0:5]
    ind2 = np.argpartition(dist_sq, 5)[5:10]
    # Calculate centroid for each Cp ring
    cent1 = np.sum(top_ten_coord[ind1]/5, axis=0)
    cent2 = np.sum(top_ten_coord[ind2]/5, axis=0)
    # Calculate metal-centroid distance
    M_cent1 = np.sqrt(np.sum(cent1[:] ** 2))
    M_cent2 = np.sqrt(np.sum(cent2[:] ** 2))
    # Calculate angle cent-met-cent
    angle = (180/np.pi)*np.arccos(np.dot(cent1, cent2)/(M_cent1 * M_cent2))
    return M_cent1, M_cent2, angle


def ZCWgrid(density):
    """
    Generate a ZCW grid for a given integration density

    Parameters
    ----------
    density : int
        Density number for ZCW algorithm

    Returns
    -------
    np.ndarray
        gM from g(0) to g(M+2)
    """

    calcgM = np.zeros(density+3)
    calcgM[0] = 8
    calcgM[1] = 13
    for i in range(2, density+3):
        calcgM[i] = calcgM[i-1] + calcgM[i-2]
    # Calculate total number of orientations, n_ori = g(M+2)
    n_ori = int(calcgM[-1])
    # Index gM for generating angles
    gM = int(calcgM[-3])
    # Index j for calculating ZCW angles
    j = np.linspace(0, n_ori-1, num=n_ori)
    # Generating array of ZCW angles theta (beta) and  phi (alpha) for full
    # sphere
    # Polar coordinates: radial distance r, polar angle theta, azimuthal angle
    # phi (rtp). Physics convention
    theta = np.arccos(2*np.fmod(j/n_ori, 1)-1)
    phi = 2*np.pi*np.fmod(j*gM/n_ori, 1)
    # ZCW grid as an array with radius 1
    gridrtp = np.zeros((n_ori, 2))
    gridrtp[:, 0] = theta
    gridrtp[:, 1] = phi

    return gridrtp


def make_batch_csv(batch_f_name, title, dist1, dist2, angle,
                   percent_large, clust_order, cp=False):
    """
    Parameters
    ----------
        batch_f_name : str
            Name of output batch file
    Returns
    -------
    None
    """

    if os.path.exists(batch_f_name):
        g = open(batch_f_name, "a")
    else:
        g = open(batch_f_name, "w")
        g.write("Data for file:{}".format(title))
        if cp:
            g.write("M-Cp1 (Angstrom), M-Cp2 (Angstrom), Cp1-M-Cp2 (degrees),")
        g.write("Total VSA (%%),Maximum Cluster VSA (%%) \n")
    if cp:
        g.write(", {:.3f}, {:.3f}, {:.2f}".format(dist1, dist2, angle))
    g.write(", {:.2f}, {:.2f}\n".format(percent_large, clust_order[0]))
    g.close()

    return
