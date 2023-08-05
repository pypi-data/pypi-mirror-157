import numpy as np
import numpy.linalg as la


class Sphere:
    """
    Contains all information required to define a sphere and to calculate
    its intersection with a ray

    Attributes
    ----------
    radius : float
        Radius of sphere
    radius2 : float
        Squared radius of sphere
    center : np.ndarray
        x,y,z coordinates of sphere center
    center_dist : np.ndarray
        Distance to center from origin
    """
    __slots__ = 'radius', 'radius2', 'center', 'center_dist'

    def __init__(self, radius, center):
        """
        Parameters
        ----------
        radius : float
            Radius of sphere
        center : np.ndarray
            x,y,z coordinates of sphere center
        """

        self.radius = radius
        self.radius2 = radius**2
        self.center = center
        self.center_dist = la.norm(self.center)

        return

    def intersect(self, ray):
        """
        Calculate intersection points of normalised ray vector with
        sphere if they exist.

        Parameters
        ----------
        ray : Ray
            Ray object

        Returns
        -------
        bool :
            True if intersection, else False
        float :
            First intersection point, 0 if no intersection
        float :
            Second intersection point, 0 if no intersection
        """

        # Find projection of ray onto sphere centre-origin vector
        tc = np.dot(self.center, ray.cart)

        if tc < 0.:
            return False, 0., 0.
        # Find minimum sphere centre to ray distance (squared)
        d2 = self.center_dist**2 - tc**2
        if d2 > self.radius2:
            return False, 0., 0.
        t1c = np.sqrt(self.radius2-d2)

        # Find ray-sphere intersection points
        # These are scalars in vector equation of line
        # P1 = O + t1*rhat
        # P2 = O + t2*rhat
        # where P1 is some point on the ray, rhat is the
        # normalised ray vector, and O is a point in space,
        # in this case the origin
        t1 = tc - t1c
        t2 = tc + t1c

        return True, t1, t2


class Ray:
    """
    Contains all information required to define a ray of light and its
    intersection with an object

    Attributes
    ----------
    theta : float
        Polar angle 0 <= theta <= pi
    phi : float
        Azimuthal angle 0 <= phi <= 2pi
    r : float
        Length of ray, assumed unity (ray is normalised)
    x : float
        x component of ray vector in cartesian coordinates
    y : float
        y component of ray vector in cartesian coordinates
    z : float
        z component of ray vector in cartesian coordinates
    cart : np.ndarray
        Direction vector of ray as (3,) np.array
    intersection : bool
        True if ray intersects with object
    r_i : float
        Distance to intersection point from origin
    cart_i : np.ndarray
        Position vector of intersection point as (3,) np.array

    """
    __slots__ = [
        'theta', 'phi', 'x', 'y', 'z', 'intersection', 'r', 'r_i', 'cart',
        'cart_i'
    ]

    def __init__(self, theta, phi):
        """
        Parameters
        ----------
        theta : float
            Polar angle 0 <= theta <= pi
        phi : float
            Azimuthal angle 0 <= phi <= 2pi
        """

        # Spherical coordinates
        self.theta = theta
        self.phi = phi
        self.r = 1.

        # Cartesian coordinates
        st = np.sin(self.theta)
        self.x = self.r*st*np.cos(self.phi)
        self.y = self.r*st*np.sin(self.phi)
        self.z = self.r*np.cos(self.theta)
        self.cart = np.array([self.x, self.y, self.z])

        # Intersection point
        self.intersection = False
        self.r_i = np.inf
        self.cart_i = np.array([0., 0., 0.])

        return

    def reset_intersection(self):
        """
        Resets intersection attributes of ray

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.intersection = False
        self.r_i = 0.
        self.cart_i = [0., 0., 0.]

        return

    def calc_cart_i(self):
        """
        Calculates position vector of intersection point using intersection
        distance

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.cart_i = self.cart * self.r_i

        return
