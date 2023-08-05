"""
This module contains the command line interface to atom_access
"""

import argparse
from textwrap import dedent
import numpy as np
import numpy.linalg as la
import xyz_py as xyzp
import copy
import time
from . import atom_access as aa


def run_aa_func(args):
    """

    Wrapper function for atom access program

    Parameters
    ----------
    args : argparser object
        User arguments

    Returns
    -------
    None

    """


    def unassigned(array):

        # TODO MOVE THIS TO atom_access.py
        # WARNING THIS FUNCTION IS USING GLOBAL VARIABLES, AND DOES NOT USE THE
        # INPUT VARIABLE ARRAY, THERE IS STRONG POTENTIAL FOR UNPREDICTABLE
        # BEHAVIOUR

        # Checks if any points in the one 1D array are equal to 0
        # (visible and unassigned)
        # True means there are visible points not assigned.
        # False means there are no unassigned visible points
        bool = False
        for i in range(n_grid_pts):
            if track_assgn[i] == 0:
                bool = True
        return bool

    start = time.time()

    # Get head of xyz file name (i.e. without extension)
    f_head = args.xyz_f_name.split(".", 1)[0]

    # Output file name
    out_f_name = "{}.out".format(f_head)

    labels, coords = xyzp.load_xyz(args.xyz_f_name)
    labels_nn = xyzp.remove_label_indices(labels)

    center = labels_nn[args.atom-1]
    n_atoms = len(labels) - 1
    xyz = np.delete(coords, args.atom-1, 0)
    Xn = copy.copy(labels)
    Xn.pop(args.atom-1)

    # Define nonbonded and covalent radius atom dictionary.
    # Taken from RSC periodic table website
    # https://www.rsc.org/periodic-table/
    nonbonded_radius = { "H" : 1.1, "He" : 1.4, "Li" : 1.82, "Be" : 1.53, "B" : 1.92, "C" : 1.7, "N" : 1.55, "O" : 1.52, "F" : 1.47, "Ne" : 1.54, "Na" : 2.27, "Mg" : 1.73, "Al" : 1.84, "Si" : 2.1, "P" : 1.8, "S" : 1.8, "Cl" : 1.75, "Ar" : 1.88, "K" : 2.75, "Ca" : 2.31, "Sc" : 2.15, "Ti" : 2.11, "V" : 2.07, "Cr" : 2.06, "Mn" : 2.05, "Fe" : 2.04, "Co" : 2.0, "Ni" : 1.97, "Cu" : 1.96, "Zn" : 2.01, "Ga" : 1.87, "Ge" : 2.11, "As" : 1.85, "Se" : 1.9, "Br" : 1.85, "Kr" : 2.02, "Rb" : 3.03, "Sr" : 2.49, "Y" : 2.32, "Zr" : 2.23, "Nb" : 2.18, "Mo" : 2.17, "Tc" : 2.16, "Ru" : 2.13, "Rh" : 2.1, "Pd" : 2.1, "Ag" : 2.11, "Cd" : 2.18, "In" : 1.93, "Sn" : 2.17, "Sb" : 2.06, "Te" : 2.06, "I" : 1.98, "Xe" : 2.16, "Cs" : 3.43, "Ba" : 2.68, "La" : 2.43, "Ce" : 2.42, "Pr" : 2.4, "Nd" : 2.39, "Pm" : 2.38, "Sm" : 2.36, "Eu" : 2.35, "Gd" : 2.34, "Tb" : 2.33, "Dy" : 2.31, "Ho" : 2.3, "Er" : 2.29, "Tm" : 2.27, "Yb" : 2.26, "Lu" : 2.24, "Hf" : 2.23, "Ta" : 2.22, "W" : 2.18, "Re" : 2.16, "Os" : 2.16, "Ir" : 2.13, "Pt" : 2.13, "Au" : 2.14, "Hg" : 2.23, "Tl" : 1.96, "Pb" : 2.02, "Bi" : 2.07, "Po" : 1.97, "At" : 2.02, "Rn" : 2.2, "Fr" : 3.48, "Ra" : 2.83, "Ac" : 2.47, "Th" : 2.45, "Pa" : 2.43, "U" : 2.41, "Np" : 2.39, "Pu" : 2.43, "Am" : 2.44, "Cm" : 2.45, "Bk" : 2.44, "Cf" : 2.45, "Es" : 2.45, "Fm" : 2.45, "Md" : 2.46, "No" : 2.46, "Lr" : 2.46} # noqa
    covalent_radius = { "H" : 0.32, "He" : 0.37, "Li" : 1.3, "Be" : 0.99, "B" : 0.84, "C" : 0.75, "N" : 0.71, "O" : 0.64, "F" : 0.6, "Ne" : 0.62, "Na" : 1.6, "Mg" : 1.4, "Al" : 1.24, "Si" : 1.14, "P" : 1.09, "S" : 1.04, "Cl" : 1.0, "Ar" : 1.01, "K" : 2.0, "Ca" : 1.74, "Sc" : 1.59, "Ti" : 1.48, "V" : 1.44, "Cr" : 1.3, "Mn" : 1.29, "Fe" : 1.24, "Co" : 1.18, "Ni" : 1.17, "Cu" : 1.22, "Zn" : 1.2, "Ga" : 1.23, "Ge" : 1.2, "As" : 1.2, "Se" : 1.18, "Br" : 1.17, "Kr" : 1.16, "Rb" : 2.15, "Sr" : 1.9, "Y" : 1.76, "Zr" : 1.64, "Nb" : 1.56, "Mo" : 1.46, "Tc" : 1.38, "Ru" : 1.36, "Rh" : 1.34, "Pd" : 1.3, "Ag" : 1.36, "Cd" : 1.4, "In" : 1.42, "Sn" : 1.4, "Sb" : 1.4, "Te" : 1.37, "I" : 1.36, "Xe" : 1.36, "Cs" : 2.38, "Ba" : 2.06, "La" : 1.94, "Ce" : 1.84, "Pr" : 1.9, "Nd" : 1.88, "Pm" : 1.86, "Sm" : 1.85, "Eu" : 1.83, "Gd" : 1.82, "Tb" : 1.81, "Dy" : 1.8, "Ho" : 1.79, "Er" : 1.77, "Tm" : 1.77, "Yb" : 1.78, "Lu" : 1.74, "Hf" : 1.64, "Ta" : 1.58, "W" : 1.5, "Re" : 1.41, "Os" : 1.36, "Ir" : 1.32, "Pt" : 1.3, "Au" : 1.3, "Hg" : 1.32, "Tl" : 1.44, "Pb" : 1.45, "Bi" : 1.5, "Po" : 1.42, "At" : 1.48, "Rn" : 1.46, "Fr" : 2.42, "Ra" : 2.11, "Ac" : 2.01, "Th" : 1.9, "Pa" : 1.84, "U" : 1.83, "Np" : 1.8, "Pu" : 1.8, "Am" : 1.73, "Cm" : 1.68, "Bk" : 1.68, "Cf" : 1.68, "Es" : 1.65, "Fm" : 1.67, "Md" : 1.73, "No" : 1.76, "Lr" : 1.61, "Rf" : 1.57, "Db" : 1.49, "Sg" : 1.43, "Bh" : 1.41, "Hs" : 1.34, "Mt" : 1.29, "Ds" : 1.28, "Rg" : 1.21, "Cn" : 1.22, "Nh" : 1.36, "Fl" : 1.43, "Mc" : 1.62, "Lv" : 1.75, "Ts" : 1.65, "Og" : 1.57}  # noqa

    # Define radius for each non-metal atom (radii array).
    # Use vdw radii for metals and covalent for non-metals
    radii = np.zeros(n_atoms)
    if args.covalent:
        radius_type = "covalent"
    elif args.nonbonded:
        radius_type = "nonbonded"
    else:
        if center not in xyzp.metals:
            radius_type = "covalent"
        else:
            radius_type = "nonbonded"

    if radius_type == "covalent":
        radii = [covalent_radius[lab] for lab in Xn]
    elif radius_type == "nonbonded":
        radii = [nonbonded_radius[lab] for lab in Xn]

    # Generate ZCW grid
    gridrtp = aa.ZCWgrid(args.density)
    # Calculate number of points in grid
    n_grid_pts = gridrtp.shape[0]

    # Define starting radius as radius of central atom
    if radius_type == "covalent":
        start_radius = covalent_radius[center]
    elif radius_type == "nonbonded":
        start_radius = nonbonded_radius[center]

    # Generate distances between central atom and all peripheral atoms
    rXn = np.array([la.norm(xyz[i]) for i in range(n_atoms)])

    # For all peripheral atoms generate list of distance for central atom
    # + radius of peripheral atom
    dist_rad = rXn + radii

    # Check that no atoms are entirely contained within sphere of central atom
    if np.nanmin(dist_rad) < start_radius:
        exit(dedent(
            "****Error: Peripheral atom is entirely contained within the"
            " atom of interest. Check structure.****"
            )
        )

    # Choose maximum distance based on size of molecule. Equal to maximum
    # distance of peripheral atoms from atom of interest + radius of that atom
    # or 20 Angstrom which ever is less
    max_dist = np.nanmax(dist_rad)
    if max_dist > 20:
        with open(out_f_name, "a") as f:
            f.write(dedent(
                "****Note: Large molecule, blocking will only be considered \
                    by atoms within 20 Angstrom of centre of interest.****\n"
                )
            )
        max_dist = 20
    r = np.arange(start_radius, max_dist, args.radialstep)

    n_rad_pts = r.size

    # List of visible (1) or blocked (0) for each grid point
    track_pts = np.ones(n_grid_pts, dtype=int)

    blocked = np.zeros([n_grid_pts, 3])
    blocked[:, :2] = np.copy(gridrtp)

    # Iterate over 2 angles, theta and phi. Indexed by i
    for i in range(n_grid_pts):
        # Iterate over radial distance, as given by array r
        for x in range(n_rad_pts):
            # Will stop loop once line of sight is blocked
            if track_pts[i]:
                p1 = aa.sph_to_cart_pt(r[x], gridrtp[i, 0], gridrtp[i, 1])
                # Iterate over peripheral atoms and find the distance between
                # (r, theta, phi) of integration grid and the peripheral atom
                # centre (rtp)
                for y in range(n_atoms):
                    d = la.norm(p1-xyz[y])
                    # If the distance between points is less than the radius
                    # of the peripheral atom the line of sight becomes blocked.
                    if d <= radii[y]:
                        track_pts[i] = 0
                        # Save the shortest distance at which line of sight is
                        # blocked
                        blocked[i, 2] = x

    # Count the number and percentage of visible points
    n_visible_pts = track_pts.sum()
    pc_visible_pts = 100. * n_visible_pts/n_visible_pts.size
    track_assgn = np.copy(track_pts) - 1

    # Define the threshold for a ZCW point to be considered a neighbour to
    # another point. This is a function of ZCW density
    # Calculated assuming there are 8 points immediately surrounding any one
    # point - valid because the ZCW points give "stripes" of points around
    # the sphere
    # The threshold is equal to the maximum distance between a point and the
    # 8th closest point for all points on the sphere, rounded up at the 4th
    # decimal place.
    # Threshold for gM = i is Thresh[i]
    neighbour_threshold = [
        1.3681,
        1.1373,
        0.8720,
        0.6936,
        0.5518,
        0.4332,
        0.3422,
        0.2699,
        0.2125,
        0.1672,
        0.1314,
        0.1033,
        0.0814,
        0.0640,
        0.0504,
        0.0396
    ]

    # Create a xyz grid of ZCW points
    gridxyz = aa.sph_to_cart(np.ones(n_grid_pts), gridrtp[:, 0], gridrtp[:, 1])
    # Create a second index to flag newly assigned points
    # Unassigned = 0
    # Assigned = 1
    flag = np.zeros(n_grid_pts)

    # Initialise counting parameters
    clust = 0
    pt = 0

    # Create lists for clusters
    clust_large = []
    clust_small = []

    # Continue assigning clusters until all points are assigned
    while unassigned(flag) is True:
        # When all points are unflagged, find the first visible point not
        # assigned to a cluster
        while track_assgn[pt] != 0:
            pt = pt+1
            if pt == n_grid_pts:
                break
        # Flag the visible point that was found and assign it to a cluster.
        # Start counting points in cluster
        flag[pt] = 1
        clust = clust+1
        count_clust = 1
        # While there are flagged points, check all flagged points (i) and for
        # each flagged point check for unassigned points (j)
        while sum(flag) != 0:
            for i in range(n_grid_pts):
                if flag[i] == 1:
                    for j in range(n_grid_pts):
                        if track_assgn[j] == 0:
                            # For points i and j on ZCW grid calculate the
                            # distance
                            # between them. If j is within the threshold of i,
                            # assign to the cluster, flag new point and add the
                            # point to the cluster count
                            d = la.norm(gridxyz[i] - gridxyz[j])
                            if d < neighbour_threshold[args.density]:
                                track_assgn[j] = clust
                                flag[j] = 1
                                count_clust = count_clust+1
                    flag[i] = 0
        # Calculate the size of the cluster as % visible solid angle.
        # (So threshold comparison is independent of NM)
        clust_percent = count_clust/n_grid_pts*100
        # For clusters that are larger than a cluster threshold,
        # add them to a list of large clusters and continue.
        # For clusters that are smaller than the threshold, add to a
        # list of small clusters but otherwise remove this cluster and
        # reassign points as Blocked
        # Cluster threshold set at 0.0 %
        if clust_percent < args.clusterthreshold:
            for i in range(n_grid_pts):
                if track_assgn[i] == clust:
                    # New tracking tag -2 means belonging to a cluster
                    # that is below the threshold
                    track_assgn[i] = -2
                    # Blocked distance set to the max integration distance
                    blocked[i, 2] = max_dist
                    track_pts[i] = "Blocked"
            clust_small.append(clust_percent)
            clust = clust-1
        else:
            clust_large.append(clust_percent)
        count_clust = 0
        clust_percent = 0

    # Calculate total number of visible points
    percent_large = sum(clust_large)
    percent_small = sum(clust_small)
    clust_order = sorted(clust_large, reverse=True)

    # # Form a list of visible points
    visible_pts = gridxyz[np.nonzero(track_pts)]

    # Calculate geometric paramters for M(Cp)2 complex
    if args.cp:
        (dist1, dist2, angle) = aa.centroid_dists_angles(Xn, xyz, rXn, n_atoms)

    # Print results into output file
    with open(out_f_name, "a") as f:
        f.write("Output file for {}:\n".format(f_head))
        f.write("Integration density: {:d}\n".format(args.density))
        f.write("Radial step: {:f} Angstrom\n".format(args.radialstep))
        f.write("Atomic radius type: {}\n".format(radius_type))
        f.write("Cluster size threshold: {:f}\n".format(args.clusterthreshold))
        f.write("Visible Solid Angle is {:.2f}\n".format(percent_large))
        f.write("There are {:d} clusters of visible points:\n".format(clust))

        # Print number of points in each cluster
        for n in range(0, clust):
            f.write("{:.2f} %%\n".format(clust_order[n]))

        if args.clusterthreshold != 0:
            f.write(
                "There are {} cluster(s) smaller than the threshold\n".format(
                    len(clust_small)
                )
            )
            f.write(
                "These make up {:.2f} %% of the solid angle\n".format(
                    len(percent_small)
                )
            )

        # Print geometric parameters for M(Cp)2
        if args.cp:
            f.write(
                "The Metal---Cp(cent) distances are {:.3f}".format(dist1),
                " and {:.3f} Angstrom\n".format(dist2)
            )
            f.write(
                "The Cp(cent)-Metal-Cp(cent) angle is {:.2f} degrees\n".format(
                    angle
                )
            )

        end = time.time()

        f.write("Calculation completed in {:.2f} seconds.\n".format(end-start))

    # Batch file for batch mode
    if args.batch:
        batch_f_name = "{}_d{:d}_r{:f}_t{:f}_{}.csv".format(
            f_head,
            args.density,
            args.radialstep,
            args.clusterthreshold,
            radius_type
        )
        aa.make_batch_csv(batch_f_name, title=f_head, cp=args.cp)

    # Save csv of visible points
    if args.csv:
        np.savetxt(
            "{}.csv".format(f_head),
            visible_pts,
            delimiter=",",
            newline="\n",
            header="Visible theta and phi coordinates for {}\n".format(f_head)
        )

    return


def read_args(arg_list=None):
    """

    Creates parser and subparsers for command line arguments

    Parameters
    ----------
    arg_list : list
        User arguments

    Returns
    -------
    None

    """

    description = '''
    A program for assessing steric hinderance using ray tracing
    '''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.set_defaults(func=run_aa_func) # noqa

    parser.add_argument(
        "xyz_f_name",
        help="Name of .xyz file containing atomic coordinates"
    )

    parser.add_argument(
        "-a",
        "--atom",
        help="Index of atom for which %% visible solid angle is calculated.",
        type=int,
        default=1
    )

    parser.add_argument(
        "-d",
        "--density",
        help=dedent(
            "ZCW integration density.Integer between 0 and 15,"
            " note - number of points does not increase linearly.\n"
            "At least 7 should be used, values above 11 tend not to improve"
            " accuracy."
        ),
        type=int,
        default=7
    )

    parser.add_argument(
        "-r",
        "--radialstep",
        help="Radial step size in Angstrom",
        type=float,
        default=0.05
    )

    parser.add_argument(
        "-t",
        "--clusterthreshold",
        help=dedent(
            "Visible solid angle cluster threshold (%%).\n"
            "Clusters of visible points below this size are considered"
            " blocked."
        ),
        type=float,
        default=0.
    )

    parser.add_argument(
        "--covalent",
        help="Use covalent radii rather than ionic",
        action="store_true"
    )

    parser.add_argument(
        "--nonbonded",
        help="Use non-bonded radii rather than ionic",
        action="store_true"
    )

    parser.add_argument(
        "--csv",
        help="Save csv file of visible theta and phi coordinates.",
        action="store_true"
    )

    parser.add_argument(
        "--batch",
        help=dedent(
            "Save a csv file with tabulated results.\n"
            "An input file <name>.xyz will create a file\n"
            "<name>_<clusterthreshold>_<radialstep>_<radiustype>.csv"
        ),
        action="store_true"
    )

    parser.add_argument(
        "--cp",
        help=dedent(
            "Calculate metal-Cp(centroid) distances and"
            " Cp(centroid)-metal-Cp(centroid) angle for M(CpR)2 complexes"
        ),
        action="store_true"
    )

    # If argument list is none, then call function func
    # which is assigned to help function
    args = parser.parse_args(arg_list)
    args.func(args)

    return


def main():
    read_args()
