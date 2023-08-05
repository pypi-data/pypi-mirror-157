"""
This module contains the command line interface to atom_access
"""

import argparse
from textwrap import dedent
import numpy as np
import xyz_py as xyzp
from . import utils as ut
from .core import trace_rays, cluster_rays, cluster_size, generate_output
import pickle


def tracing_func(args):
    """

    Wrapper function for ray tracing program

    Parameters
    ----------
    args : argparser object
        User arguments

    Returns
    -------
    None

    """

    # Load xyz file
    labels, coords = xyzp.load_xyz(args.xyz_f_name)
    labels_nn = xyzp.remove_label_indices(labels)

    blocked, unblocked, n_cut = trace_rays(
        labels_nn,
        coords,
        args.atom-1,
        args.cutoff,
        args.density
    )

    total_rays = len(blocked) + len(unblocked)
    pc_unblocked = len(unblocked)/(total_rays) * 100.

    if not args.quiet:
        print("\nUsing {:d} rays".format(total_rays))
        print(
            "Cutoff of {:f} Angstroms has been enforced, ".format(args.cutoff),
            "{:d} atoms are completely excluded".format(n_cut)
        )

        print("{:.2f} % solid angle is visible".format(pc_unblocked))

    # Cluster rays
    cluster_id = cluster_rays(unblocked, args.density)

    if not cluster_id.size and args.quiet:
        exit("All rays are blocked")
    elif not cluster_id.size:
        exit()

    # Calculate size of clusters
    clust_percent, _ = cluster_size(cluster_id, total_rays)

    if not args.quiet:
        print("\nThere are {:d} clusters".format(clust_percent.size))

        for idx, x in enumerate(clust_percent):
            print(
              "Cluster {:d} contains {:.2f} % solid angle".format(idx+1, x)
            )

    # Get head of xyz file name (i.e. without extension)
    f_head = args.xyz_f_name.split(".", 1)[0]

    # Print output file
    generate_output(
        f_head, args.density, pc_unblocked, clust_percent, args.cutoff,
        no_header=args.quiet
    )

    if args.save_rays:
        _coords = coords - coords[args.atom-1]
        xyzp.save_xyz("{}_shift.xyz".format(f_head), labels, _coords)
        with open("rays.pickle", 'wb') as f:
            pickle.dump(unblocked, f)

    if args.plot:
        cart_vecs = np.array([ray.cart for ray in unblocked])
        ut.plot_rays(cart_vecs, cluster_id, clust_percent.size, show=True)

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

    description = """
    A program for assessing steric hinderance using ray tracing
    """

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.set_defaults(func=tracing_func) # noqa

    parser.add_argument(
        "xyz_f_name",
        help="Name of .xyz file containing atomic coordinates"
    )

    parser.add_argument(
        "-a",
        "--atom",
        help="Index of atom for which %% visible rays is calculated.",
        type=int,
        default=1
    )

    parser.add_argument(
        "-d",
        "--density",
        help=dedent(
            "ZCW integration density.Integer between 0 and 15,"
            " note - number of points does not increase linearly.\n"
        ),
        type=int,
        default=12
    )

    parser.add_argument(
        "-c",
        "--cutoff",
        help=dedent(
            "Cutoff for intersection distance in Angstroms"
        ),
        default=5.,
        type=float,
    )

    parser.add_argument(
        "-p",
        "--plot",
        help=dedent(
            "Plot unblocked points in browser using Plotly"
        ),
        action='store_true'
    )

    parser.add_argument(
        "-sr",
        "--save_rays",
        help=dedent(
            "Pickle unblocked rays and save xyz file"
        ),
        action='store_true'
    )

    parser.add_argument(
        "-q",
        "--quiet",
        help=dedent(
            "Suppress print to terminal and output file header"
        ),
        action='store_true'
    )

    # If argument list is none, then call function func
    # which is assigned to help function
    args = parser.parse_args(arg_list)
    args.func(args)

    return


def main():
    read_args()
