import numpy as np
import xyz_py as xyzp
import numpy.linalg as la
from .objects import Sphere
from . import utils as ut
from sklearn.cluster import AgglomerativeClustering
import datetime


def trace_rays(labels, coords, centre, radial_cutoff, zcw_density):
    """
    Performs ray tracing calculation on set of atomic coordinates to find
    blocked and unblocked rays.
    Atoms within `radial_cutoff` distance from the centre are represented by
    spheres with specified `radius_type`.
    Rays emanate from `centre` and are blocked by intersection with an atom.

    Parameters
    ----------
    labels : list
        atomic labels
    coords : np.ndarray
        (n_atoms,3) array containing xyz coordinates of each atom
    centre : int
        Index of central atom from which rays emanate
    radial_cutoff : float
        Cutoff after which atoms will not be considered in raytracing
    radius_type : str {'covalent', 'atomic'}
        Type of radii to use for atomic spheres
    zcw_density : int
        Value indicating density of rays generated using
        Zaremba-Conroy-Wolfsberg algorithm.

    Returns
    -------
    list
        Blocked rays as atom_access.objects.ray objects
    list
        Unblocked rays as atom_access.objects.ray objects
    n_cut
        Number of atoms excluded by `radial_cutoff`
    """

    # Shift chosen center to origin
    coords -= coords[centre]

    # Set radius of each atom in full molecule
    radii = [xyzp.atomic_radii[lab] for lab in labels]

    # Calculate distance from center to edge of each atom and reorder coords,
    # labels and radii
    dists = la.norm(coords, axis=1) - radii
    ordering = np.argsort(dists)
    coords = coords[ordering]
    labels = [labels[ord] for ord in ordering]
    dists = dists[ordering]
    radii = [radii[ord] for ord in ordering]

    # Remove any atoms which are further than distance cutoff
    if any(dist > radial_cutoff for dist in dists):
        cut = np.argmax(dists > radial_cutoff)
        n_cut = len(dists)-cut
    else:
        cut = len(dists) + 1
        n_cut = 0
    coords = coords[1:cut]
    labels = labels[1:cut]
    radii = radii[1:cut]

    # Create list of spheres, one for each atom
    atoms = [Sphere(rad, coord) for (rad, coord) in zip(radii, coords)]

    # Create list of rays using ZCW grid
    rays = ut.create_zcw_rays(zcw_density)

    # Ray Tracing
    for atom in atoms:
        for ray in rays:
            tf, trial_ri, _ = atom.intersect(ray)
            if tf and trial_ri < ray.r_i and trial_ri < radial_cutoff:
                ray.intersection = True
                ray.r_i = trial_ri

    blocked = [ray for ray in rays if ray.intersection]
    unblocked = [ray for ray in rays if not ray.intersection]

    for ray in blocked:
        ray.calc_cart_i()

    return blocked, unblocked, n_cut


def cluster_rays(rays, zcw_density):
    """
    Clusters rays based on adjacency/connectivity to neighbour. ZCW Density
    defines distance between nearest neighbour rays generated
    in ZCW algorithm - similar to the use of atomic radii in molecular
    connectivity graphs.

    Parameters
    ----------
    labels : list
        Rays to cluster as atom_access.objects.ray objects
    zcw_density : int
        Value indicating density of rays generated using
        Zaremba-Conroy-Wolfsberg algorithm.

    Returns
    -------
    np.ndarray
        Integers specifying which cluster each ray belongs to
    """

    cart_vecs = np.array([ray.cart for ray in rays])

    # Neighbour threshold distances calculated using neighbours function,
    # rounded up at 8th decimal place
    neighbour_threshold = [
        1.36809116,
        1.13724257,
        0.87190947,
        0.69352894,
        0.55179242,
        0.43319823,
        0.34210750,
        0.26988293,
        0.21244729,
        0.16711945,
        0.13131158,
        0.10328090,
        0.08132305,
        0.06399453,
        0.05033967,
        0.03958930
    ]

    clstr = AgglomerativeClustering(
        n_clusters=None,
        compute_full_tree=True,
        linkage='single',
        distance_threshold=neighbour_threshold[zcw_density]
    )
    clstr.fit_predict(cart_vecs)

    # List of integers indicating which cluster each unblocked ray belongs to
    cluster_id = clstr.labels_

    return cluster_id


def cluster_size(cluster_id, total_rays):
    '''
    Calculate the size of each cluster in terms of % solid angle.

    Parameters
    ----------
    cluster_id : np.ndarray
        Integers specifying which cluster each ray belongs to
    total_rays : int
        Total number of rays generated using
        Zaremba-Conroy-Wolfsberg algorithm.

    Returns
    -------
    list
        % solid angle of each cluster, ordered from largest to smallest
        cluster.
    list
        Integers specifying ordering of cluster percentages relative to
        initial `cluster_id` order
    '''

    _, counts = np.unique(cluster_id, return_counts=True)

    clust_percent = counts / total_rays * 100

    # Order clusters based on size
    ordering = np.argsort(clust_percent)[::-1]
    clust_percent = clust_percent[ordering]

    return clust_percent, ordering


def generate_output(f_head, density, pc_unblocked, clust_percent,
                    radial_cutoff, no_header=False):
    '''
    Generate an output file with molecule name, settings and cluster sizes.

    Parameters
    ----------
    f_head : str
        Input .xyz file name without .xyz extension
    '''

    # Output file name
    out_f_name = "{}.out".format(f_head)

    # Print results to output
    with open(out_f_name, "w") as f:
        if no_header:
            f.write("                                          Atom Access") # noqa
        else:
            f.write(":5PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP:                                     !GPPPPPPPPPPPPPPPPPPPPPPP5:\n") # noqa
            f.write("^@B?JJJJJJJJJJ????????JJJJJ????????^7YYYYYYYYYYYYYYY5555YYYYYYYYYYYYYYYJ~~??JJ???????JJJJJJJJJJJ?#@^\n") # noqa
            f.write("^@Y           :!!!!!!~     .!!!!!!!!?5#&@@@@@@@@@@&BGGGB#@@@@@@@@@@@@#BJ7!!!  :!!!!!!            P@^\n") # noqa
            f.write("^@Y           5@@@@@@@^    7@@@@@@@@@@P !5#@@@@G7^.      :!Y#@@@@&P7.7@@@@@@? 5@@@@@@^           P@^\n") # noqa
            f.write("^@Y          .#@@@@@@@J    :??5@@@@B??!   .!PP^             .J#5!.   7@@@@@@P #@@@@@@^           P@^\n") # noqa
            f.write("^@Y          ~@@@&5@@@B       !@@@@P                 ..       .      7@@@@@@&!@@@@@@@^           P@^\n") # noqa
            f.write("^@Y          J@@@#~@@@@^      7@@@@P              .Y#&#G^            7@@@&B@@B@@G@@@@^           P@^\n") # noqa
            f.write("^@Y          G@@@5 #@@@?      7@@@@P              ~@@@@@5            7@@@#J@@@@@?@@@@^           P@^\n") # noqa
            f.write("^@Y         :&@@@B5&@@@G      7@@@@P               7PBGJ:            7@@@&~&@@@B!@@@@^           P@^\n") # noqa
            f.write("^@Y         7@@@@@&&@@@@^     7@@@@P      .^7^                !^.    7@@@&.G@@@Y~@@@@^           P@^\n") # noqa
            f.write("^@Y         P@@@@J Y@@@@J     7@@@@P  .~?P#@@&J:            !G@@#57^ 7@@@@.?@@@~~@@@@^           P@^\n") # noqa
            f.write("^@Y         ?YJJY^ ^YJJY7     ^JJYPPYG&@@@@@@@@&P?~^:.::^7Y#@@@@@@@@BB#PJ? :JJJ.:YJJJ:           P@^\n") # noqa
            f.write("^@Y                          .^75B&@@@@@@@@@@@@@@@@@&&&&@@@@@@@@@@@@@@@&GJ!.                     P@^\n") # noqa
            f.write("^@Y                      :!YG&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&GJ~.                 P@^\n") # noqa
            f.write("^@Y                 .^?5B&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&G?~.             P@^\n") # noqa
            f.write("^@Y            .^!YG#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&P?^.         P@^\n") # noqa
            f.write("^@Y        .^?!^7???#@@@@@@@P?!~!75&@@@@@@#Y7~~!?G@@@@@@P7??77J@@@@@&57!~!?P@@@@@@&Y?!~^..:      P@^\n") # noqa
            f.write("^@Y    :~JP#@@~     Y@@@@@@7   J:  ^&@@@@#:  ^?   J@@@@@?   :^7@@@@@!  :J   J@@@@@~  :J   Y#5!:  G@^\n") # noqa
            f.write("^@Y:7YB&@@@@@#.  ~  ~@@@@@@:  :@7   G@@@@P   ?@.  ^@@@@@?   P@@@@@@@^  :PJYYP@@@@@:  ^PJYYG@@@&BY5P:\n") # noqa
            f.write(" :?@@@@@@@@@@5  :P   #@@@@@:  :&BPPP&@@@@P   ?@PPPG@@@@@?   ..7@@@@@B!.  :!P@@@@@@B!.  :7P@@@@@@@!  \n") # noqa
            f.write("  7@@@@@@@@@@7  ^P.  Y@@@@@:  :@PJJJ#@@@@P   ?@YJJ5@@@@@?   JPG@@@@@BG5?!   7@@@@@BG5?!   ?@@@@@@!  \n") # noqa
            f.write("  7@@@@@@@@@&:   :   ~@@@@@^  :&!   B@@@@G   ?#   ~@@@@@?   Y#B@@@@@~  ^@~  :&@@@@^  ~@^  ^@@@@@@!  \n") # noqa
            f.write("  7@@@@@@@@@G   !@~  .#@@@@P:  :  .J@@@@@@?.  :  ^G@@@@@?      #@@@@G:  :  .J@@@@@P:  :  .Y@@@@@@!  \n") # noqa
            f.write("  7@@@@@@@@@&BBB&@#BBB&@@@@@@BGPPB&@@@@@@@@&BPPG#@@@@@@@&BBBBBB@@@@@@@BGPPB&@@@@@@@@BGPGB&@@@@@@@!  \n") # noqa
            f.write("  !BBBBBBBBBBBBBBBBBBBBBBBBBBB###BBBBBBBBBBBB###BBBBBBBBBBBBBBBBBBBBBBB###BBBBBBBBBBB###BBBBBBBBB~  \n") # noqa
        f.write("\n                  Gemma K. Gransbury, Jon G. C. Kragskow, Nicholas F. Chilton\n") # noqa
        f.write("                                           Citation\n\n")
        f.write("{}\n\n".format(
            datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y "))
        )

        f.write("Output file for {}\n".format(f_head))

        f.write("Integration density: {:d}\n".format(density))
        f.write("Radial cutoff: {:f} Angstrom\n\n".format(radial_cutoff))
        f.write("Total visible solid angle is {:.6f}\n\n".format(pc_unblocked))
        f.write("There are {:d} clusters of visible points:\n".format(
            clust_percent.size
        ))

        for idx, x in enumerate(clust_percent):
            f.write(
                "Cluster {:d} contains {:.6f} % solid angle\n".format(
                    idx+1, x
                )
            )
    return


def neighbours(rays, n):
    '''
    Define maximum nth-nearest neighbour distance for a group of rays.

    Parameters
    ----------
    rays : np.array
        rays as cartesian vectors, indended to be entire set of ZCW rays
    n : int
        nth nearest neighbour

    Returns
    -------
    float:
        maximum distance between any ray and its nth nearest neighbour
    '''

    # Extract ray vectors from rays
    cart_vecs = np.array([ray.cart for ray in rays])

    # Pairwise difference of all ray vectors
    diff = cart_vecs[:, np.newaxis] - cart_vecs

    # Take norm within each [x,y,z] to give distance between original vectors
    dist = la.norm(diff, axis=2)

    # Find distance to nth nearest neighbour for each ray
    index = np.argpartition(dist, kth=n, axis=0)
    n_dists = np.take_along_axis(dist, index, axis=0)[n]

    # Maximum distance to nth nearest neighbour
    max_dist = np.nanmax(n_dists)

    return max_dist
